#!/usr/bin/env python3
"""
Database migration script to add missing columns to users table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text
import logging
import psycopg2

def migrate_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Check what columns exist using SQLite syntax
            with db.engine.connect() as connection:
                # For SQLite, use PRAGMA table_info to get column information
                result = connection.execute(text("PRAGMA table_info(users)"))
                existing_columns = {row[1] for row in result}  # row[1] is column name
                print(f"📋 Existing columns: {sorted(existing_columns)}")
            
            # List of columns that should exist
            required_columns = [
                ('password', 'VARCHAR(255)'),
                ('username', 'VARCHAR(100)'),
                ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                ('reset_token', 'VARCHAR(255)'),
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
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            raise

def fix_database_connection():
    """Fix database connection and add missing columns"""
    # Use the correct Railway PostgreSQL URL
    database_url = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"
    
    print("🔧 Fixing database columns...")
    print(f"🗄️ Connecting to Railway PostgreSQL...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully")
        
        # Add all missing columns
        columns_to_add = [
            ("password", "VARCHAR(255)"),
            ("username", "VARCHAR(100)"),
            ("created_at", "TIMESTAMP DEFAULT NOW()"),
            ("reset_token", "VARCHAR(255)"),
            ("reset_token_expires", "TIMESTAMP")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                print(f"✅ Added/verified column: {col_name}")
            except Exception as e:
                print(f"⚠️ Issue with column {col_name}: {e}")
        
        conn.commit()
        
        # Verify all columns exist
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Current users table structure ({len(columns)} columns):")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        print("\n✅ Database columns fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_database()
    fix_database_connection()
