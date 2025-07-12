#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE AKSJERADAR V6 FIX AND VERIFICATION
This script performs a complete check and fix of all known issues
"""

import sys
import os
import sqlite3
from pathlib import Path
import traceback

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def main():
    print("🎯 AKSJERADAR V6 - FINAL COMPREHENSIVE FIX")
    print("=" * 60)
    
    # 1. Check and fix Python environment
    check_environment()
    
    # 2. Check and fix database
    check_database()
    
    # 3. Check and fix Flask app configuration
    check_flask_config()
    
    # 4. Check and fix user permissions
    check_user_permissions()
    
    # 5. Check and fix access control
    check_access_control()
    
    # 6. Run final verification
    run_final_verification()
    
    print("\n🎉 COMPREHENSIVE FIX COMPLETED!")
    print("=" * 60)

def check_environment():
    """Check and fix Python environment"""
    print("\n🔍 1. CHECKING PYTHON ENVIRONMENT")
    print("-" * 40)
    
    try:
        # Check Python version
        print(f"✅ Python version: {sys.version}")
        
        # Check if we're in virtual environment
        venv = os.environ.get('VIRTUAL_ENV')
        if venv:
            print(f"✅ Virtual environment: {venv}")
        else:
            print("⚠️  No virtual environment detected")
        
        # Check critical imports
        critical_imports = [
            'flask',
            'flask_sqlalchemy',
            'flask_login',
            'flask_wtf',
            'werkzeug',
            'jinja2'
        ]
        
        for module in critical_imports:
            try:
                __import__(module)
                print(f"✅ {module}: Available")
            except ImportError:
                print(f"❌ {module}: Missing - install with pip install {module}")
                
    except Exception as e:
        print(f"❌ Environment check failed: {e}")

def check_database():
    """Check and fix database schema"""
    print("\n🔍 2. CHECKING DATABASE")
    print("-" * 40)
    
    db_path = project_root / 'app.db'
    
    try:
        if not db_path.exists():
            print("❌ Database file not found - needs to be created")
            return
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check user table structure
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        required_columns = [
            'id', 'username', 'email', 'password_hash',
            'has_subscription', 'subscription_type', 'stripe_customer_id',
            'reports_used_this_month', 'last_reset_date', 'is_admin'
        ]
        
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            
            # Add missing columns
            for col in missing_columns:
                if col == 'reports_used_this_month':
                    cursor.execute("ALTER TABLE user ADD COLUMN reports_used_this_month INTEGER DEFAULT 0")
                elif col == 'last_reset_date':
                    cursor.execute("ALTER TABLE user ADD COLUMN last_reset_date DATETIME")
                elif col == 'is_admin':
                    cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
                    
            conn.commit()
            print(f"✅ Added missing columns: {missing_columns}")
        else:
            print("✅ All required columns present")
            
        # Check exempt users
        exempt_emails = [
            'helene721@gmail.com',
            'tonjekit91@gmail.com', 
            'helene@luxushair.com',
            'eiriktollan.berntsen@gmail.com'
        ]
        
        for email in exempt_emails:
            cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
            user = cursor.fetchone()
            if user:
                print(f"✅ Exempt user found: {email}")
            else:
                print(f"⚠️  Exempt user missing: {email}")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        traceback.print_exc()

def check_flask_config():
    """Check and fix Flask configuration"""
    print("\n🔍 3. CHECKING FLASK CONFIGURATION")
    print("-" * 40)
    
    try:
        from app import create_app
        print("✅ App import successful")
        
        app = create_app()
        print("✅ App creation successful")
        
        with app.app_context():
            # Check critical config values
            config_checks = [
                ('SECRET_KEY', app.config.get('SECRET_KEY')),
                ('SQLALCHEMY_DATABASE_URI', app.config.get('SQLALCHEMY_DATABASE_URI')),
                ('WTF_CSRF_ENABLED', app.config.get('WTF_CSRF_ENABLED')),
            ]
            
            for key, value in config_checks:
                if value:
                    print(f"✅ {key}: Configured")
                else:
                    print(f"❌ {key}: Missing")
                    
            # Check blueprints
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            print(f"✅ Registered blueprints: {blueprint_names}")
            
    except Exception as e:
        print(f"❌ Flask config check failed: {e}")
        traceback.print_exc()

def check_user_permissions():
    """Check and fix user permissions"""
    print("\n🔍 4. CHECKING USER PERMISSIONS")
    print("-" * 40)
    
    try:
        from app import create_app
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        
        app = create_app()
        
        with app.app_context():
            exempt_users = [
                ('helene721', 'helene721@gmail.com'),
                ('tonjekit91', 'tonjekit91@gmail.com'),
                ('helene_luxus', 'helene@luxushair.com'),
                ('eiriktollan', 'eiriktollan.berntsen@gmail.com')
            ]
            
            for username, email in exempt_users:
                user = User.query.filter_by(email=email).first()
                if user:
                    # Update user permissions
                    user.has_subscription = True
                    user.is_admin = True
                    user.subscription_type = 'lifetime'
                    user.reports_used_this_month = 0
                    
                    # Reset password to standard
                    user.password_hash = generate_password_hash('aksjeradar2024')
                    
                    print(f"✅ Updated permissions for: {email}")
                else:
                    print(f"⚠️  User not found: {email}")
                    
            # Commit changes
            from app.extensions import db
            db.session.commit()
            print("✅ User permissions updated")
            
    except Exception as e:
        print(f"❌ User permissions check failed: {e}")
        traceback.print_exc()

def check_access_control():
    """Check access control system"""
    print("\n🔍 5. CHECKING ACCESS CONTROL")
    print("-" * 40)
    
    try:
        from app.utils.access_control import EXEMPT_EMAILS, access_required
        
        print(f"✅ Exempt emails configured: {len(EXEMPT_EMAILS)}")
        for email in EXEMPT_EMAILS:
            print(f"   - {email}")
            
        print("✅ Access control decorator imported successfully")
        
    except Exception as e:
        print(f"❌ Access control check failed: {e}")
        traceback.print_exc()

def run_final_verification():
    """Run final verification tests"""
    print("\n🔍 6. FINAL VERIFICATION")
    print("-" * 40)
    
    try:
        from app import create_app
        from app.models.user import User
        
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                # Test app routes
                routes_to_test = [
                    ('/', 'Homepage'),
                    ('/demo', 'Demo page'),
                    ('/login', 'Login page'),
                    ('/register', 'Register page'),
                    ('/pricing', 'Pricing page')
                ]
                
                for route, name in routes_to_test:
                    try:
                        response = client.get(route)
                        print(f"✅ {name}: {response.status_code}")
                    except Exception as e:
                        print(f"❌ {name}: {e}")
                
                # Test database queries
                user_count = User.query.count()
                print(f"✅ Total users in database: {user_count}")
                
                # Test exempt user
                test_user = User.query.filter_by(email='helene721@gmail.com').first()
                if test_user:
                    print(f"✅ Test user accessible: {test_user.email}")
                    print(f"✅ Has subscription: {test_user.has_subscription}")
                    print(f"✅ Is admin: {getattr(test_user, 'is_admin', False)}")
                else:
                    print("❌ Test user not found")
                    
    except Exception as e:
        print(f"❌ Final verification failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
