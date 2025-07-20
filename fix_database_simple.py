#!/usr/bin/env python3
"""
Simple database column fix
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database():
    from app import create_app
    from flask import current_app
    
    app = create_app()
    
    with app.app_context():
        try:
            from app import db
            from sqlalchemy import text
            
            print("Checking database connection...")
            
            # Try to add the missing columns
            with db.engine.begin() as conn:
                try:
                    print("Adding reset_token column...")
                    conn.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255)'))
                    print("✅ reset_token column handled")
                except Exception as e:
                    print(f"Reset token column: {e}")
                
                try:
                    print("Adding reset_token_expires column...")
                    conn.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP'))
                    print("✅ reset_token_expires column handled")
                except Exception as e:
                    print(f"Reset token expires column: {e}")
            
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
                
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = fix_database()
    sys.exit(0 if success else 1)
