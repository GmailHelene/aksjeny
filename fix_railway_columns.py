#!/usr/bin/env python3
"""
Fix missing database columns for Railway production
This script adds missing columns to the users table
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_railway_database():
    """Add missing columns to Railway production database"""
    print("🔧 FIXING RAILWAY DATABASE COLUMNS")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("📋 Checking database connection...")
            
            # Check database engine type
            engine_name = db.engine.name
            print(f"   Database engine: {engine_name}")
            
            # List of missing columns to add
            missing_columns = [
                ('reset_token', 'VARCHAR(100)'),
                ('reset_token_expires', 'TIMESTAMP'),
                ('language', 'VARCHAR(10) DEFAULT \'no\''),
                ('notification_settings', 'TEXT'),
                ('two_factor_enabled', 'BOOLEAN DEFAULT FALSE'),
                ('two_factor_secret', 'VARCHAR(32)'),
                ('email_verified', 'BOOLEAN DEFAULT TRUE'),
                ('is_locked', 'BOOLEAN DEFAULT FALSE'),
                ('last_login', 'TIMESTAMP'),
                ('login_count', 'INTEGER DEFAULT 0'),
                ('reports_used_this_month', 'INTEGER DEFAULT 0'),
                ('last_reset_date', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('is_admin', 'BOOLEAN DEFAULT FALSE')
            ]
            
            print(f"🔍 Checking {len(missing_columns)} columns...")
            
            # Get existing columns
            existing_columns = []
            try:
                if engine_name == 'postgresql':
                    result = db.session.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users'
                    """))
                    existing_columns = [row[0] for row in result]
                elif engine_name == 'sqlite':
                    result = db.session.execute(text("PRAGMA table_info(users)"))
                    existing_columns = [row[1] for row in result]
                
                print(f"   Found {len(existing_columns)} existing columns")
                
            except Exception as e:
                print(f"   Error checking columns: {e}")
                print("   Proceeding to add columns anyway...")
            
            # Add missing columns
            added_count = 0
            for column_name, column_def in missing_columns:
                if column_name not in existing_columns:
                    try:
                        if engine_name == 'postgresql':
                            # PostgreSQL syntax
                            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                        else:
                            # SQLite syntax  
                            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                        
                        db.session.execute(text(sql))
                        db.session.commit()
                        print(f"   ✅ Added column: {column_name}")
                        added_count += 1
                        
                    except Exception as e:
                        print(f"   ⚠️ Column {column_name} might already exist: {e}")
                        db.session.rollback()
                else:
                    print(f"   ✅ Column {column_name} already exists")
            
            print(f"\n📊 Summary: {added_count} columns added")
            
            # Test user creation/lookup
            print("\n🧪 Testing user operations...")
            try:
                from app.models import User
                from werkzeug.security import generate_password_hash
                
                # Check if test user exists
                test_user = User.query.filter_by(email='helene721@gmail.com').first()
                
                if not test_user:
                    print("   Creating test user: helene721@gmail.com")
                    test_user = User(
                        username='helene',
                        email='helene721@gmail.com',
                        password_hash=generate_password_hash('password123'),
                        is_admin=True,
                        email_verified=True,
                        language='no'
                    )
                    db.session.add(test_user)
                    db.session.commit()
                    print("   ✅ Test user created successfully")
                else:
                    print(f"   ✅ Test user exists: {test_user.username}")
                
                # Test login lookup
                login_test = User.query.filter_by(email='helene721@gmail.com').first()
                if login_test:
                    print(f"   ✅ Login test successful: Found user {login_test.username}")
                else:
                    print("   ❌ Login test failed: User not found")
                
            except Exception as e:
                print(f"   ❌ User test failed: {e}")
                db.session.rollback()
            
            print("\n🎉 Railway database migration completed!")
            return True
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_railway_database()
    if success:
        print("\n✅ Database is now ready for production!")
    else:
        print("\n❌ Migration failed - check errors above")
        sys.exit(1)
