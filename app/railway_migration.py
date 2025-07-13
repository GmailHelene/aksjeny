#!/usr/bin/env python3
"""
Railway production migration - simpler version
This can be run directly in Railway's environment
"""

import os
import sys

# Set up environment for Railway
if '/app' not in sys.path:
    sys.path.insert(0, '/app')

def railway_migration():
    print("🚀 RAILWAY PRODUCTION MIGRATION")
    print("=" * 40)
    
    try:
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("✅ Connected to Railway database")
            
            # Simple column additions with error handling
            migrations = [
                ("reports_used_this_month", "ALTER TABLE users ADD COLUMN IF NOT EXISTS reports_used_this_month INTEGER DEFAULT 0"),
                ("last_reset_date", "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("is_admin", "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE")
            ]
            
            for column_name, sql in migrations:
                try:
                    db.session.execute(text(sql))
                    print(f"✅ {column_name} column added/verified")
                except Exception as e:
                    print(f"ℹ️ {column_name}: {str(e)[:50]}...")
            
            # Commit schema changes
            db.session.commit()
            print("💾 Schema changes committed")
            
            # Update exempt users
            exempt_updates = """
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
            )
            """
            
            try:
                result = db.session.execute(text(exempt_updates))
                db.session.commit()
                print(f"✅ Updated {result.rowcount} exempt users")
            except Exception as e:
                print(f"⚠️ Exempt user update: {e}")
            
            print("\n🎯 RAILWAY MIGRATION COMPLETE!")
            return True
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

if __name__ == "__main__":
    railway_migration()
