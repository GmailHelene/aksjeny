#!/usr/bin/env python3
"""
Add missing database columns using proper SQLAlchemy methods
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text
import logging
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def add_missing_columns():
    """Add missing columns to users table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🔧 Adding missing database columns...")
            
            db_url = os.getenv('DATABASE_URL') or RAILWAY_DATABASE_URL
            
            # Columns that should exist
            required_columns = [
                ("password", "VARCHAR(255)"),
                ("username", "VARCHAR(100)"),
                ("created_at", "TIMESTAMP DEFAULT NOW()"),
                ("reset_token", "VARCHAR(255)"),
                ("reset_token_expires", "TIMESTAMP")
            ]
            
            try:
                conn = psycopg2.connect(db_url)
                cursor = conn.cursor()
                
                for col_name, col_type in required_columns:
                    try:
                        # Try to add the column
                        cursor.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type};")
                        logger.info(f"✅ Added/verified column: {col_name}")
                    except Exception as e:
                        logger.warning(f"⚠️ Issue with column {col_name}: {e}")
                
                conn.commit()
                logger.info("\n✅ All required columns added!")
                
                # Verify the structure
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position;
                """)
                
                columns = cursor.fetchall()
                logger.info(f"\n📋 Updated users table structure ({len(columns)} columns):")
                for col_name, col_type in columns:
                    logger.info(f"  - {col_name}: {col_type}")
                
            except Exception as e:
                logger.error(f"❌ Error adding columns: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

            logger.info("🎉 Database column migration completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during column migration: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = add_missing_columns()
    sys.exit(0 if success else 1)
