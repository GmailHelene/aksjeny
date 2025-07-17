#!/usr/bin/env python3
"""
Add missing language column to notification_settings table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def add_language_column():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if language column exists using SQLAlchemy 2.0+ syntax
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='notification_settings' AND column_name='language'
            """))
            
            if not result.fetchone():
                print("Adding language column to notification_settings table...")
                db.session.execute(text("""
                    ALTER TABLE notification_settings 
                    ADD COLUMN language VARCHAR(8) DEFAULT 'nb' NOT NULL
                """))
                db.session.commit()
                
                print("✅ Language column added successfully")
            else:
                print("✅ Language column already exists")
                
        except Exception as e:
            print(f"❌ Error adding language column: {e}")
            db.session.rollback()
            # For SQLite, use a different approach
            if "information_schema" in str(e).lower():
                try:
                    print("Detected SQLite - using PRAGMA approach...")
                    result = db.session.execute(text("PRAGMA table_info(notification_settings)"))
                    columns = [row[1] for row in result]
                    
                    if 'language' not in columns:
                        print("Adding language column to SQLite table...")
                        db.session.execute(text("""
                            ALTER TABLE notification_settings 
                            ADD COLUMN language VARCHAR(8) DEFAULT 'nb' NOT NULL
                        """))
                        db.session.commit()
                        print("✅ Language column added to SQLite successfully")
                    else:
                        print("✅ Language column already exists in SQLite")
                        
                except Exception as sqlite_error:
                    print(f"❌ SQLite error: {sqlite_error}")
                    db.session.rollback()

if __name__ == "__main__":
    add_language_column()
