#!/usr/bin/env python3
"""
Fix missing database columns
"""

from app import create_app
from app.extensions import db
from sqlalchemy import text

def main():
    app = create_app()
    with app.app_context():
        try:
            # Check if language column exists using SQLAlchemy 2.0+ syntax
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='notification_settings' 
                AND column_name='language'
            """))
            
            if not result.fetchone():
                # Add missing language column
                db.session.execute(text("""
                    ALTER TABLE notification_settings 
                    ADD COLUMN language VARCHAR(10) DEFAULT 'no'
                """))
                db.session.commit()
                print("✅ Added language column to notification_settings")
            else:
                print("✅ Language column already exists")
                
        except Exception as e:
            print(f"❌ Error fixing database: {e}")
            db.session.rollback()

if __name__ == "__main__":
    main()
