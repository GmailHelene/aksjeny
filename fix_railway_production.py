#!/usr/bin/env python3
"""
Fix Railway Production Database
This script will be run directly on Railway to add missing columns
"""

import os
import sys
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_railway_production():
    """Fix Railway production database by adding missing columns"""
    
    # Check if we're in Railway environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not found - not in Railway environment")
        return False
    
    logger.info("🚀 FIXING RAILWAY PRODUCTION DATABASE")
    logger.info("=" * 50)
    
    try:
        import psycopg2
        
        # Parse database URL
        result = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        cursor = conn.cursor()
        logger.info("✅ Connected to Railway PostgreSQL database")
        
        # Check existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND table_schema = 'public'
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"📋 Found {len(existing_columns)} existing columns")
        
        # Define missing columns to add
        missing_columns = [
            ('reset_token', 'VARCHAR(100)'),
            ('reset_token_expires', 'TIMESTAMP'),
            ('language', 'VARCHAR(10) DEFAULT \'no\''),
            ('notification_settings', 'TEXT'),
            ('two_factor_enabled', 'BOOLEAN DEFAULT FALSE'),
            ('two_factor_secret', 'VARCHAR(32)'),
            ('email_verified', 'BOOLEAN DEFAULT TRUE'),
            ('is_locked', 'BOOLEAN DEFAULT FALSE'),
            ('last_login', 'TIMESTAMP'),
            ('login_count', 'INTEGER DEFAULT 0')
        ]
        
        # Add missing columns
        added_count = 0
        for column_name, column_def in missing_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    conn.commit()
                    logger.info(f"✅ Added column: {column_name}")
                    added_count += 1
                except Exception as e:
                    logger.error(f"❌ Error adding column {column_name}: {e}")
                    conn.rollback()
            else:
                logger.info(f"✅ Column {column_name} already exists")
        
        logger.info(f"🎉 Migration completed! Added {added_count} columns")
        
        # Test user lookup
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ('helene721@gmail.com',))
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.info("✅ User lookup test successful")
        else:
            logger.info("ℹ️ Test user not found - creating...")
            
            # Create test user
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash('aksjeradar2024')
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, created_at, 
                                 is_admin, email_verified, language, has_subscription) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            """, ('helene721', 'helene721@gmail.com', password_hash, True, True, 'no', True))
            
            conn.commit()
            logger.info("✅ Test user created")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Railway production database fix completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_railway_production()
    sys.exit(0 if success else 1)
