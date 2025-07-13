#!/usr/bin/env python3
"""
Production database migration script
Adds missing columns to users table in production
"""

import os
import sys
from datetime import datetime

def migrate_production_database():
    """Migrate production database to add missing columns"""
    
    print("🚀 PRODUCTION DATABASE MIGRATION")
    print("=" * 50)
    
    try:
        # Import after setting up the app context
        sys.path.append('/app' if os.path.exists('/app') else '.')
        
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        app = create_app()
        
        with app.app_context():
            print("✅ Connected to production database")
            
            # Check current schema
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
            """))
            
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"📊 Existing columns: {len(existing_columns)}")
            
            # Define required columns with their SQL
            required_columns = {
                'reports_used_this_month': 'ALTER TABLE users ADD COLUMN reports_used_this_month INTEGER DEFAULT 0',
                'last_reset_date': 'ALTER TABLE users ADD COLUMN last_reset_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'is_admin': 'ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE'
            }
            
            # Add missing columns
            added_count = 0
            for column_name, sql_command in required_columns.items():
                if column_name not in existing_columns:
                    try:
                        db.session.execute(text(sql_command))
                        print(f"✅ Added column: {column_name}")
                        added_count += 1
                    except Exception as e:
                        print(f"⚠️ Column {column_name} might already exist: {e}")
                else:
                    print(f"ℹ️ Column {column_name} already exists")
            
            # Commit changes
            if added_count > 0:
                db.session.commit()
                print(f"\n💾 Committed {added_count} column additions")
            
            # Verify final schema
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY column_name
            """))
            
            final_columns = [row[0] for row in result.fetchall()]
            print(f"\n📋 Final schema ({len(final_columns)} columns):")
            for col in sorted(final_columns):
                print(f"   - {col}")
            
            # Update exempt users with correct values
            print("\n👑 Updating exempt users...")
            exempt_emails = [
                'tonjekit91@gmail.com',
                'helene721@gmail.com', 
                'helene@luxushair.com',
                'eiriktollan.berntsen@gmail.com'
            ]
            
            for email in exempt_emails:
                try:
                    db.session.execute(text("""
                        UPDATE users 
                        SET 
                            is_admin = TRUE,
                            has_subscription = TRUE,
                            reports_used_this_month = 0,
                            last_reset_date = CURRENT_TIMESTAMP
                        WHERE email = :email
                    """), {'email': email})
                    print(f"✅ Updated exempt user: {email}")
                except Exception as e:
                    print(f"⚠️ Error updating {email}: {e}")
            
            db.session.commit()
            
            print("\n" + "=" * 50)
            print("🎯 MIGRATION COMPLETE!")
            print("✅ Production database schema updated")
            print("✅ Exempt users configured")
            print("🚀 Login should now work in production!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = migrate_production_database()
    if success:
        print("\n🎉 Migration successful!")
    else:
        print("\n💥 Migration failed!")
        sys.exit(1)
