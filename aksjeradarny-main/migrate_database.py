#!/usr/bin/env python3
"""
Database migration to add missing columns
"""

import os
import sys
sys.path.append('/workspaces/aksjeradarv6')

from app import create_app
from app.extensions import db

def migrate_database():
    """Add missing columns to users table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if reports_used_this_month column exists
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='reports_used_this_month';
            """))
            
            if not result.fetchone():
                print("Adding reports_used_this_month column...")
                db.session.execute(db.text("""
                    ALTER TABLE users 
                    ADD COLUMN reports_used_this_month INTEGER DEFAULT 0;
                """))
                
            # Check if last_reset_date column exists  
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='last_reset_date';
            """))
            
            if not result.fetchone():
                print("Adding last_reset_date column...")
                db.session.execute(db.text("""
                    ALTER TABLE users 
                    ADD COLUMN last_reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                """))
                
            # Check if is_admin column exists
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='is_admin';
            """))
            
            if not result.fetchone():
                print("Adding is_admin column...")
                db.session.execute(db.text("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
                """))
                
            db.session.commit()
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_database()
