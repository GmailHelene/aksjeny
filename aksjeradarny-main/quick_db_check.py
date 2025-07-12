#!/usr/bin/env python3
"""
Simple database check and fix script
"""

import os
import sys
sys.path.append('/workspaces/aksjeradarv6')

def quick_db_check():
    """Quick database check"""
    try:
        from app import create_app
        from app.extensions import db
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # Try to query a user to see if columns are missing
            try:
                user = User.query.first()
                print(f"✅ Database connection OK")
                if user:
                    print(f"✅ Found user: {user.email}")
                    # Try to access the problematic columns
                    try:
                        reports = user.reports_used_this_month
                        admin = user.is_admin
                        reset_date = user.last_reset_date
                        print(f"✅ All columns accessible")
                    except AttributeError as e:
                        print(f"⚠️ Column issue: {e}")
                else:
                    print("ℹ️ No users found in database")
                    
                # Create tables if they don't exist
                db.create_all()
                print("✅ Database tables created/verified")
                
            except Exception as e:
                print(f"❌ Database query error: {e}")
                # Try to create all tables
                try:
                    db.create_all()
                    print("✅ Database tables recreated")
                except Exception as e2:
                    print(f"❌ Failed to create tables: {e2}")
                
    except Exception as e:
        print(f"❌ App creation failed: {e}")

if __name__ == "__main__":
    quick_db_check()
