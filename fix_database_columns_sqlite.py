#!/usr/bin/env python3
"""
Database migration script to add missing columns to users table (SQLite compatible)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text
import logging

def migrate_database():
    """Migrate database to add missing columns"""
    print("🔄 Starting SQLite database migration...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get existing columns using SQLite PRAGMA
            with db.engine.connect() as connection:
                result = connection.execute(text("PRAGMA table_info(users)"))
                
                existing_columns = {row[1] for row in result}  # row[1] is column name
                print(f"📋 Existing columns: {sorted(existing_columns)}")
            
            # List of columns that should exist based on User model
            required_columns = [
                ('reset_token', 'VARCHAR(100)'),
                ('reset_token_expires', 'TIMESTAMP'),
                ('language', 'VARCHAR(10) DEFAULT \'no\''),
                ('notification_settings', 'TEXT'),
                ('two_factor_enabled', 'BOOLEAN DEFAULT 0'),
                ('two_factor_secret', 'VARCHAR(32)'),
                ('email_verified', 'BOOLEAN DEFAULT 1'),
                ('is_locked', 'BOOLEAN DEFAULT 0'),
                ('last_login', 'TIMESTAMP'),
                ('login_count', 'INTEGER DEFAULT 0')
            ]
            
            print(f"🔍 Checking {len(required_columns)} required columns...")
            
            # Add missing columns
            columns_added = 0
            with db.engine.connect() as connection:
                for column_name, column_type in required_columns:
                    if column_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                            print(f"➕ Adding column: {sql}")
                            connection.execute(text(sql))
                            connection.commit()
                            print(f"✅ Added column: {column_name}")
                            columns_added += 1
                        except Exception as e:
                            print(f"❌ Failed to add column {column_name}: {e}")
                            connection.rollback()
                    else:
                        print(f"✅ Column {column_name} already exists")
            
            print(f"🎉 Migration completed! Added {columns_added} new columns.")
            
            # Verify the migration by checking columns again
            print("\n📋 Final column verification:")
            with db.engine.connect() as connection:
                result = connection.execute(text("PRAGMA table_info(users)"))
                final_columns = [row[1] for row in result]
                print(f"Final columns: {sorted(final_columns)}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    migrate_database()
