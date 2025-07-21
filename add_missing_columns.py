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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_columns():
    """Add missing columns to users table"""
    
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🔧 Adding missing database columns...")
            
            # List of columns to add with their SQL definitions
            columns_to_add = [
                'reset_token VARCHAR(100)',
                'reset_token_expires TIMESTAMP',
                'language VARCHAR(10) DEFAULT \'no\'',
                'notification_settings TEXT',
                'two_factor_enabled BOOLEAN DEFAULT FALSE',
                'two_factor_secret VARCHAR(32)',
                'email_verified BOOLEAN DEFAULT TRUE',
                'is_locked BOOLEAN DEFAULT FALSE',
                'last_login TIMESTAMP',
                'login_count INTEGER DEFAULT 0'
            ]
            
            for column_def in columns_to_add:
                column_name = column_def.split()[0]
                try:
                    # Use SQLAlchemy's text() for raw SQL execution
                    sql = f'ALTER TABLE users ADD COLUMN {column_def}'
                    db.session.execute(text(sql))
                    db.session.commit()
                    logger.info(f"✅ Added column: {column_name}")
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                        logger.info(f"ℹ️ Column {column_name} already exists")
                    else:
                        logger.warning(f"⚠️ Could not add column {column_name}: {e}")
                    db.session.rollback()
            
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
