#!/usr/bin/env python3
"""
Railway Database Migration Script
Run this on Railway to add missing database columns
"""

import os
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_railway_database():
    """Add missing columns to Railway PostgreSQL database"""
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not found")
        logger.error("   This script must be run in Railway production environment")
        return False
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        logger.info("🚀 Starting Railway database migration...")
        
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
            ORDER BY column_name
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"📋 Found {len(existing_columns)} existing columns")
        
        # Define columns that must exist
        required_columns = [
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
        for column_name, column_def in required_columns:
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
        
        # Verify helene721@gmail.com user exists with correct password
        from werkzeug.security import generate_password_hash
        
        cursor.execute("SELECT id FROM users WHERE email = %s", ('helene721@gmail.com',))
        user_exists = cursor.fetchone()
        
        if user_exists:
            # Update password to ensure it's correct
            password_hash = generate_password_hash('aksjeradar2024')
            cursor.execute("""
                UPDATE users 
                SET password_hash = %s, is_admin = TRUE, email_verified = TRUE 
                WHERE email = %s
            """, (password_hash, 'helene721@gmail.com'))
            conn.commit()
            logger.info("✅ Updated helene721@gmail.com password and admin status")
        else:
            # Create the user
            password_hash = generate_password_hash('aksjeradar2024')
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, created_at, 
                                 is_admin, email_verified, language, has_subscription,
                                 subscription_type, login_count, reports_used_this_month) 
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s)
            """, ('helene721', 'helene721@gmail.com', password_hash, True, True, 'no', 
                  True, 'lifetime', 0, 0))
            conn.commit()
            logger.info("✅ Created helene721@gmail.com user with admin privileges")
        
        cursor.close()
        conn.close()
        
        logger.info(f"🎉 Railway migration completed successfully!")
        logger.info(f"   Added {added_count} new columns")
        logger.info("")
        logger.info("🔐 Login credentials:")
        logger.info("   Email: helene721@gmail.com")
        logger.info("   Password: aksjeradar2024")
        
        return True
        
    except ImportError:
        logger.error("❌ psycopg2 not available - cannot connect to PostgreSQL")
        logger.error("   Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_railway_database()
    sys.exit(0 if success else 1)
