#!/usr/bin/env python3
"""
Fix all missing columns in users table
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_all_columns():
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        try:
            from app import db
            from sqlalchemy import text
            
            print("Checking database connection...")
            
            # Define all required columns
            required_columns = {
                'language': 'VARCHAR(10) DEFAULT "no"',
                'notification_settings': 'TEXT',
                'two_factor_enabled': 'BOOLEAN DEFAULT 0',
                'two_factor_secret': 'VARCHAR(255)',
                'email_verified': 'BOOLEAN DEFAULT 0',
                'is_locked': 'BOOLEAN DEFAULT 0',
                'last_login': 'TIMESTAMP',
                'login_count': 'INTEGER DEFAULT 0'
            }
            
            # Check which columns exist
            with db.engine.begin() as conn:
                # Get existing columns
                result = conn.execute(text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result]
                print(f"Existing columns: {existing_columns}")
                
                # Add missing columns
                for column_name, column_def in required_columns.items():
                    if column_name not in existing_columns:
                        print(f"Adding {column_name} column...")
                        conn.execute(text(f'ALTER TABLE users ADD COLUMN {column_name} {column_def}'))
                        print(f"✅ {column_name} column added")
                    else:
                        print(f"✅ {column_name} column already exists")
            
            print("✅ All database columns fixed!")
            
            # Test the user query that was failing
            print("Testing user lookup...")
            from app.models import User
            
            user = User.query.filter(
                (User.username == 'helene721@gmail.com') | 
                (User.email == 'helene721@gmail.com')
            ).first()
            
            if user:
                print(f"✅ User found: {user.username} ({user.email})")
                print(f"   Admin: {user.is_admin}")
                print(f"   Email verified: {user.email_verified}")
            else:
                print("❌ User not found - may need to create test users")
                
                # Let's check all users
                all_users = User.query.all()
                print(f"Total users in database: {len(all_users)}")
                for u in all_users:
                    print(f"  - {u.username} ({u.email}) - Admin: {u.is_admin}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_all_columns()
    sys.exit(0 if success else 1)
