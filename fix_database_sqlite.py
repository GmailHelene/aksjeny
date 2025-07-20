#!/usr/bin/env python3
"""
SQLite-compatible database column fix
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database():
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        try:
            from app import db
            from sqlalchemy import text
            
            print("Checking database connection...")
            
            # Check if columns exist
            with db.engine.begin() as conn:
                # Get existing columns
                result = conn.execute(text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result]
                print(f"Existing columns: {existing_columns}")
                
                # Add reset_token if missing
                if 'reset_token' not in existing_columns:
                    print("Adding reset_token column...")
                    conn.execute(text('ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)'))
                    print("✅ reset_token column added")
                else:
                    print("✅ reset_token column already exists")
                
                # Add reset_token_expires if missing
                if 'reset_token_expires' not in existing_columns:
                    print("Adding reset_token_expires column...")
                    conn.execute(text('ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP'))
                    print("✅ reset_token_expires column added")
                else:
                    print("✅ reset_token_expires column already exists")
            
            print("✅ Database columns fixed!")
            
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
    success = fix_database()
    sys.exit(0 if success else 1)
