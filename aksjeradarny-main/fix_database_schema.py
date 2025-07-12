#!/usr/bin/env python3
"""
Database migration script to fix schema issues
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def fix_database_schema():
    """Fix database schema issues"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Fixing database schema...")
            
            # Drop and recreate tables with correct schema
            print("Dropping problematic tables...")
            
            # Check if tip_type column exists in stock_tips
            try:
                result = db.session.execute(text("PRAGMA table_info(stock_tips)"))
                columns = [row[1] for row in result.fetchall()]
                print(f"Current stock_tips columns: {columns}")
                
                if 'tip_type' not in columns:
                    print("Adding missing tip_type column...")
                    db.session.execute(text("ALTER TABLE stock_tips ADD COLUMN tip_type VARCHAR(10)"))
                    
                if 'confidence' not in columns:
                    print("Adding missing confidence column...")
                    db.session.execute(text("ALTER TABLE stock_tips ADD COLUMN confidence VARCHAR(10)"))
                    
                if 'analysis' not in columns:
                    print("Adding missing analysis column...")
                    db.session.execute(text("ALTER TABLE stock_tips ADD COLUMN analysis TEXT"))
                    
            except Exception as e:
                print(f"Error checking stock_tips table: {e}")
            
            # Recreate all tables to ensure schema is correct
            print("Recreating database tables...")
            db.create_all()
            
            db.session.commit()
            print("✅ Database schema fixed successfully!")
            
        except Exception as e:
            print(f"❌ Error fixing database schema: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_database_schema()
