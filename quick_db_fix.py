#!/usr/bin/env python3
"""
Quick database migration script to fix missing columns
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def fix_database():
    """Fix database by adding missing columns and creating test users"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Starting database fix...")
            
            # Get database connection
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            # Add missing columns if they don't exist
            missing_columns = [
                ('reports_used_this_month', 'INTEGER DEFAULT 0'),
                ('last_reset_date', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('is_admin', 'BOOLEAN DEFAULT FALSE'),
                ('reset_token', 'VARCHAR(100)'),
                ('reset_token_expires', 'TIMESTAMP'),
                ('language', 'VARCHAR(10) DEFAULT \'no\''),
                ('notification_settings', 'TEXT'),
                ('two_factor_enabled', 'BOOLEAN DEFAULT FALSE'),
                ('two_factor_secret', 'VARCHAR(32)'),
                ('email_verified', 'BOOLEAN DEFAULT TRUE'),
                ('is_locked', 'BOOLEAN DEFAULT FALSE'),
                ('last_login', 'TIMESTAMP'),
                ('login_count', 'INTEGER DEFAULT 0')
            ]
            
            print("Adding missing columns...")
            for column_name, column_def in missing_columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {column_name} {column_def}")
                    print(f"✅ Added column: {column_name}")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"✅ Column already exists: {column_name}")
                    else:
                        print(f"❌ Error adding {column_name}: {e}")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Create or update test users
            print("\nCreating test users...")
            
            test_users = [
                ('helene721', 'helene721@gmail.com', 'password123', True),
                ('eirik', 'eirik@example.com', 'password123', False),
                ('admin', 'admin@example.com', 'admin123', True)
            ]
            
            for username, email, password, is_admin in test_users:
                existing_user = User.query.filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    # Update existing user
                    existing_user.set_password(password)
                    existing_user.has_subscription = True
                    existing_user.subscription_type = 'monthly'
                    existing_user.is_admin = is_admin
                    existing_user.email_verified = True
                    print(f"✅ Updated user: {username}")
                else:
                    # Create new user
                    user = User(
                        username=username,
                        email=email,
                        has_subscription=True,
                        subscription_type='monthly',
                        is_admin=is_admin,
                        email_verified=True,
                        reports_used_this_month=0,
                        login_count=0,
                        language='no'
                    )
                    user.set_password(password)
                    db.session.add(user)
                    print(f"✅ Created user: {username}")
            
            db.session.commit()
            
            print("\n🎉 Database fix completed successfully!")
            print("\nYou can now log in with:")
            print("  - Username: helene721, Password: password123")
            print("  - Username: eirik, Password: password123")
            print("  - Username: admin, Password: admin123")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during database fix: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = fix_database()
    if not success:
        sys.exit(1)
