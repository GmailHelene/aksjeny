#!/usr/bin/env python3
"""
Database migration to add missing columns to users table
"""

import os
import sys
sys.path.append('/workspaces/aksjeradarv6')

from app import create_app
from app.extensions import db
from sqlalchemy import text

def add_missing_columns():
    """Add missing columns to users table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check which columns are missing
            with db.engine.connect() as connection:
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND table_schema = 'public'
                """))
                
                existing_columns = [row[0] for row in result]
                print(f"Existing columns: {existing_columns}")
                
                # Define columns that should exist
                required_columns = {
                    'reports_used_this_month': 'INTEGER DEFAULT 0',
                    'last_reset_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                    'is_admin': 'BOOLEAN DEFAULT FALSE'
                }
                
                # Add missing columns
                for column_name, column_def in required_columns.items():
                    if column_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                            print(f"Adding column: {sql}")
                            connection.execute(text(sql))
                            connection.commit()
                            print(f"✅ Added column: {column_name}")
                        except Exception as e:
                            print(f"❌ Error adding column {column_name}: {e}")
                    else:
                        print(f"✅ Column {column_name} already exists")
            
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_missing_columns()
