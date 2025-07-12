"""
Emergency production fix - Add missing database columns
This should be deployed to fix the production database schema
"""

from flask import Flask
from app import create_app
from app.extensions import db
from sqlalchemy import text

def fix_production_database():
    """Fix production database schema"""
    app = create_app()
    
    with app.app_context():
        try:
            # Add missing columns with PostgreSQL syntax
            db.session.execute(text("""
                DO $$ 
                BEGIN
                    -- Add reports_used_this_month if not exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='reports_used_this_month') THEN
                        ALTER TABLE users ADD COLUMN reports_used_this_month INTEGER DEFAULT 0;
                    END IF;
                    
                    -- Add last_reset_date if not exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='last_reset_date') THEN
                        ALTER TABLE users ADD COLUMN last_reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                    END IF;
                    
                    -- Add is_admin if not exists
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name='users' AND column_name='is_admin') THEN
                        ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
                    END IF;
                END $$;
            """))
            
            db.session.commit()
            
            # Update exempt users
            db.session.execute(text("""
                UPDATE users 
                SET 
                    is_admin = TRUE,
                    has_subscription = TRUE,
                    reports_used_this_month = 0,
                    last_reset_date = CURRENT_TIMESTAMP
                WHERE email IN (
                    'tonjekit91@gmail.com',
                    'helene721@gmail.com', 
                    'helene@luxushair.com',
                    'eiriktollan.berntsen@gmail.com'
                );
            """))
            
            db.session.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
            db.session.rollback()

# Auto-run migration on import
if __name__ != "__main__":
    try:
        fix_production_database()
    except:
        pass  # Fail silently if migration can't run
