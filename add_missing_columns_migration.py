"""
Database migration to add missing columns to users table
Run this to add language and notification_settings columns
"""

import sqlite3
import os
from datetime import datetime

def add_missing_columns():
    """Add missing columns to users table"""
    
    # Path to database
    db_path = 'app/app.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute('PRAGMA table_info(users)')
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        migrations_performed = []
        
        # Add language column if missing
        if 'language' not in existing_columns:
            print("Adding language column...")
            cursor.execute('ALTER TABLE users ADD COLUMN language VARCHAR(10) DEFAULT "no"')
            migrations_performed.append('language')
            print("✅ Added language column with default 'no'")
        else:
            print("✅ Language column already exists")
        
        # Add notification_settings column if missing
        if 'notification_settings' not in existing_columns:
            print("Adding notification_settings column...")
            cursor.execute('ALTER TABLE users ADD COLUMN notification_settings TEXT DEFAULT NULL')
            migrations_performed.append('notification_settings')
            print("✅ Added notification_settings column")
        else:
            print("✅ Notification_settings column already exists")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        if migrations_performed:
            print(f"\n✅ Successfully added columns: {migrations_performed}")
        else:
            print("\n✅ All required columns already exist!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    print(f"Timestamp: {datetime.now()}")
    
    success = add_missing_columns()
    
    if success:
        print("\n🎉 Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
