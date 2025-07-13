#!/usr/bin/env python3
"""
Add missing reset_token columns to database
"""
import sys
import os
sys.path.append('/workspaces/aksjeny')

from app import create_app, db
from app.models.user import User
import sqlite3

def add_reset_token_columns():
    """Add reset_token columns to users table"""
    print("🔧 ADDING RESET TOKEN COLUMNS TO DATABASE")
    print("=" * 50)
    
    # Get database path
    db_path = '/workspaces/aksjeny/app/app.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns in users table: {len(columns)}")
        
        # Add reset_token column if it doesn't exist
        if 'reset_token' not in columns:
            print("   Adding reset_token column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)")
            print("   ✅ reset_token column added")
        else:
            print("   ✅ reset_token column already exists")
        
        # Add reset_token_expires column if it doesn't exist
        if 'reset_token_expires' not in columns:
            print("   Adding reset_token_expires column...")
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires DATETIME")
            print("   ✅ reset_token_expires column added")
        else:
            print("   ✅ reset_token_expires column already exists")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        import traceback
        traceback.print_exc()

def test_database_update():
    """Test that the database update worked"""
    print("\n🧪 TESTING DATABASE UPDATE")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Try to query a user
            user = User.query.first()
            if user:
                print(f"✅ Database query works")
                print(f"   User: {user.email}")
                print(f"   Reset token: {user.reset_token}")
                print(f"   Reset token expires: {user.reset_token_expires}")
            else:
                print("⚠️ No users found in database")
                
        except Exception as e:
            print(f"❌ Database query failed: {e}")

if __name__ == "__main__":
    add_reset_token_columns()
    test_database_update()
