#!/usr/bin/env python3
"""
Fix missing reset_token columns in users table
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from sqlalchemy import text

def fix_reset_columns():
    """Add missing reset_token and reset_token_expires columns"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns exist first
            with db.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('reset_token', 'reset_token_expires')
                """))
                
                existing_columns = [row[0] for row in result]
                print(f"Existing reset columns: {existing_columns}")
                
                # Add reset_token column if missing
                if 'reset_token' not in existing_columns:
                    print("Adding reset_token column...")
                    conn.execute(text('ALTER TABLE users ADD COLUMN reset_token VARCHAR(255)'))
                    print("✅ reset_token column added")
                else:
                    print("✅ reset_token column already exists")
                
                # Add reset_token_expires column if missing
                if 'reset_token_expires' not in existing_columns:
                    print("Adding reset_token_expires column...")
                    conn.execute(text('ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP'))
                    print("✅ reset_token_expires column added")
                else:
                    print("✅ reset_token_expires column already exists")
                
                conn.commit()
            print("✅ All reset token columns are now present!")
            
            # Test user query
            print("\nTesting user query...")
            user = User.query.filter(
                (User.username == 'helene721@gmail.com') | 
                (User.email == 'helene721@gmail.com')
            ).first()
            
            if user:
                print(f"✅ Found user: {user.username} ({user.email})")
            else:
                print("❌ User not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    success = fix_reset_columns()
    sys.exit(0 if success else 1)
