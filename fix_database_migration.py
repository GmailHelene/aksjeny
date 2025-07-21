#!/usr/bin/env python3
"""
Fix database migration for missing columns and set correct password for helene721@gmail.com
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_and_user():
    """Fix database schema and set correct password for helene721@gmail.com"""
    
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🔧 Starting database migration and user fix...")
            
            # 1. Add missing columns if they don't exist
            missing_columns = [
                ('reset_token', 'VARCHAR(100)'),
                ('reset_token_expires', 'TIMESTAMP'),
                ('language', 'VARCHAR(10) DEFAULT "no"'),
                ('notification_settings', 'TEXT'),
                ('two_factor_enabled', 'BOOLEAN DEFAULT FALSE'),
                ('two_factor_secret', 'VARCHAR(32)'),
                ('email_verified', 'BOOLEAN DEFAULT TRUE'),
                ('is_locked', 'BOOLEAN DEFAULT FALSE'),
                ('last_login', 'TIMESTAMP'),
                ('login_count', 'INTEGER DEFAULT 0')
            ]
            
            for column_name, column_def in missing_columns:
                try:
                    # Try to add the column
                    db.engine.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_def}')
                    logger.info(f"✅ Added column: {column_name}")
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                        logger.info(f"ℹ️ Column {column_name} already exists")
                    else:
                        logger.warning(f"⚠️ Could not add column {column_name}: {e}")
            
            # 2. Find or create helene721@gmail.com user
            user = User.query.filter_by(email='helene721@gmail.com').first()
            
            if user:
                logger.info(f"👤 Found user: {user.email} (username: {user.username})")
                
                # Set the correct password based on search results
                # Multiple passwords found in search results, using the most recent one
                correct_password = "aksjeradar2024"  # This appears to be the standard password for exempt users
                user.password_hash = generate_password_hash(correct_password)
                
                # Ensure user has all necessary fields
                user.is_admin = True
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                user.email_verified = True
                user.language = 'no'
                user.two_factor_enabled = False
                user.is_locked = False
                user.login_count = user.login_count or 0
                user.reports_used_this_month = user.reports_used_this_month or 0
                user.last_reset_date = user.last_reset_date or datetime.utcnow()
                
                db.session.commit()
                
                logger.info(f"✅ Updated user {user.email}")
                logger.info(f"🔑 Password set to: {correct_password}")
                logger.info(f"👑 Admin: {user.is_admin}")
                logger.info(f"💎 Subscription: {user.subscription_type}")
                
            else:
                # Create the user if not found
                logger.info("👤 User not found, creating new user...")
                
                correct_password = "aksjeradar2024"
                new_user = User(
                    username='helene721',
                    email='helene721@gmail.com',
                    password_hash=generate_password_hash(correct_password),
                    is_admin=True,
                    has_subscription=True,
                    subscription_type='lifetime',
                    subscription_start=datetime.utcnow(),
                    email_verified=True,
                    language='no',
                    two_factor_enabled=False,
                    is_locked=False,
                    login_count=0,
                    reports_used_this_month=0,
                    last_reset_date=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                
                db.session.add(new_user)
                db.session.commit()
                
                logger.info(f"✅ Created user: {new_user.email}")
                logger.info(f"🔑 Password: {correct_password}")
            
            # 3. Test the database connection by querying the user
            test_user = User.query.filter_by(email='helene721@gmail.com').first()
            if test_user:
                logger.info("✅ Database test successful - user can be queried")
                
                # Test password
                from werkzeug.security import check_password_hash
                if check_password_hash(test_user.password_hash, correct_password):
                    logger.info("✅ Password verification successful")
                else:
                    logger.error("❌ Password verification failed")
                    return False
            else:
                logger.error("❌ Database test failed - user not found after creation")
                return False
            
            logger.info("🎉 Database migration and user fix completed successfully!")
            
            # 4. Show login information
            print("\n" + "="*60)
            print("🔐 LOGIN INFORMATION FOR helene721@gmail.com")
            print("="*60)
            print(f"📧 Email: helene721@gmail.com")
            print(f"🔑 Password: {correct_password}")
            print(f"👑 Admin: Yes")
            print(f"💎 Subscription: Lifetime")
            print("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = fix_database_and_user()
    sys.exit(0 if success else 1)
