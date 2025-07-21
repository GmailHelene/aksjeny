#!/usr/bin/env python3
"""
Create missing database columns for Railway production
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def create_missing_columns():
    """Add missing columns to Railway production database"""
    print("🔧 FIXING RAILWAY DATABASE COLUMNS")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            print("📋 Checking database type and existing columns...")
            
            # Check if we're using SQLite or PostgreSQL
            engine_name = db.engine.name
            print(f"   Database engine: {engine_name}")
            
            existing_columns = []
            
            if engine_name == 'postgresql':
                # For PostgreSQL, use information_schema
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND table_schema = 'public'
                """))
                existing_columns = [row[0] for row in result]
                
            elif engine_name == 'sqlite':
                # For SQLite, use PRAGMA
                result = db.session.execute(text("PRAGMA table_info(users)"))
                existing_columns = [row[1] for row in result]  # Column name is at index 1
            
            print(f"   Found {len(existing_columns)} existing columns")
            
            # Check for missing columns and add them
            missing_columns = []
            
            # Check reset_token
            if 'reset_token' not in existing_columns:
                print("   Adding reset_token column...")
                db.session.execute(text('ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)'))
                missing_columns.append('reset_token')
                print("   ✅ reset_token column added")
            else:
                print("   ✅ reset_token column already exists")
            
            # Check reset_token_expires  
            if 'reset_token_expires' not in existing_columns:
                print("   Adding reset_token_expires column...")
                if engine_name == 'postgresql':
                    db.session.execute(text('ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP'))
                else:
                    db.session.execute(text('ALTER TABLE users ADD COLUMN reset_token_expires DATETIME'))
                missing_columns.append('reset_token_expires')
                print("   ✅ reset_token_expires column added")
            else:
                print("   ✅ reset_token_expires column already exists")
            
            # Commit changes
            if missing_columns:
                db.session.commit()
                print(f"✅ Successfully added {len(missing_columns)} missing columns: {missing_columns}")
            else:
                print("✅ All columns already exist - no changes needed")
            
            # Test user lookup that was failing
            print("\n🧪 Testing user lookup...")
            from app.models.user import User
            
            test_user = User.query.filter(
                (User.username == 'eirik') | (User.email == 'eirik')
            ).first()
            
            if test_user:
                print(f"✅ Successfully found user: {test_user.username} ({test_user.email})")
            else:
                print("ℹ️  User 'eirik' not found - checking all users...")
                all_users = User.query.all()
                print(f"   Total users in database: {len(all_users)}")
                for user in all_users[:5]:  # Show first 5 users
                    print(f"   - {user.username} ({user.email})")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False
            
    return True

if __name__ == '__main__':
    success = create_missing_columns()
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("   Railway production should now work correctly.")
    else:
        print("\n💥 Database migration failed!")
        sys.exit(1)
