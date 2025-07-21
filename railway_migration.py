#!/usr/bin/env python3
"""
One-time Railway database migration script
This will be run on Railway to add missing columns
"""

import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_railway_migration():
    """Run the database migration on Railway"""
    try:
        from app import create_app, db
        from sqlalchemy import text
        from app.models.user import User
        
        logger.info("🚀 Starting Railway database migration...")
        
        app = create_app()
        
        with app.app_context():
            logger.info("📋 Checking database columns...")
            
            # Check existing columns using PostgreSQL syntax
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND table_schema = 'public'
            """))
            
            existing_columns = [row[0] for row in result]
            logger.info(f"Found {len(existing_columns)} existing columns")
            
            missing_columns = []
            
            # Check reset_token
            if 'reset_token' not in existing_columns:
                logger.info("Adding reset_token column...")
                db.session.execute(text('ALTER TABLE users ADD COLUMN reset_token VARCHAR(100)'))
                missing_columns.append('reset_token')
                logger.info("✅ reset_token column added")
            else:
                logger.info("✅ reset_token column already exists")
            
            # Check reset_token_expires  
            if 'reset_token_expires' not in existing_columns:
                logger.info("Adding reset_token_expires column...")
                db.session.execute(text('ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP'))
                missing_columns.append('reset_token_expires')
                logger.info("✅ reset_token_expires column added")
            else:
                logger.info("✅ reset_token_expires column already exists")
            
            # Commit changes
            if missing_columns:
                db.session.commit()
                logger.info(f"✅ Successfully added {len(missing_columns)} missing columns: {missing_columns}")
            else:
                logger.info("✅ All columns already exist - no changes needed")
            
            # Test user lookup
            logger.info("🧪 Testing user lookup...")
            test_user = User.query.filter(
                (User.username == 'eirik') | (User.email == 'eirik')
            ).first()
            
            if test_user:
                logger.info(f"✅ Successfully found user: {test_user.username} ({test_user.email})")
            else:
                logger.info("ℹ️ User 'eirik' not found - will create users next")
                
            return True
            
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.session.rollback()
        return False

def create_initial_users():
    """Create initial test users"""
    try:
        from app import create_app, db
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        
        logger.info("👥 Creating initial users...")
        
        app = create_app()
        
        with app.app_context():
            # User 1: helen721
            helen_user = User.query.filter(
                (User.username == 'helen721') | (User.email == 'helen721@gmail.com')
            ).first()
            
            if not helen_user:
                logger.info("Creating user: helen721...")
                helen_user = User(
                    username='helen721',
                    email='helen721@gmail.com',
                    password_hash=generate_password_hash('721'),
                    is_admin=True,
                    email_verified=True,
                    subscription_type='lifetime',
                    has_subscription=True
                )
                db.session.add(helen_user)
                logger.info("✅ helen721 created (admin, lifetime)")
            else:
                logger.info(f"✅ helen721 already exists ({helen_user.email})")
            
            # User 2: eirik  
            eirik_user = User.query.filter(
                (User.username == 'eirik') | (User.email == 'eirik@test.no')
            ).first()
            
            if not eirik_user:
                logger.info("Creating user: eirik...")
                eirik_user = User(
                    username='eirik',
                    email='eirik@test.no',
                    password_hash=generate_password_hash('test123'),
                    is_admin=False,
                    email_verified=True,
                    subscription_type='monthly',
                    has_subscription=True
                )
                db.session.add(eirik_user)
                logger.info("✅ eirik created (monthly subscription)")
            else:
                logger.info(f"✅ eirik already exists ({eirik_user.email})")
            
            db.session.commit()
            
            # Show all users
            all_users = User.query.all()
            logger.info(f"📊 Total users: {len(all_users)}")
            for user in all_users:
                admin_status = "👑 Admin" if user.is_admin else "👤 User"
                sub_status = f"{user.subscription_type}" if user.has_subscription else "free"
                logger.info(f"   - {user.username} ({user.email}) - {admin_status} - {sub_status}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating users: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.session.rollback()
        return False

if __name__ == '__main__':
    logger.info("🚀 RAILWAY DATABASE MIGRATION")
    logger.info("=" * 50)
    
    # Step 1: Fix database columns
    migration_success = run_railway_migration()
    
    if migration_success:
        logger.info("✅ Database migration completed successfully!")
        
        # Step 2: Create users
        user_creation_success = create_initial_users()
        
        if user_creation_success:
            logger.info("✅ User creation completed successfully!")
            logger.info("🎉 Railway setup complete!")
            logger.info("")
            logger.info("🎯 Login Instructions:")
            logger.info("   Username: helen721 | Password: 721")
            logger.info("   Username: eirik    | Password: test123")
        else:
            logger.error("❌ User creation failed!")
    else:
        logger.error("❌ Database migration failed!")
        
    logger.info("Migration script finished.")
