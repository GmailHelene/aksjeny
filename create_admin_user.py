#!/usr/bin/env python3
"""
Create admin user with permanent demo access
"""
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create admin user with permanent demo access"""
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(email='admin@aksjeradar.trade').first()
        if admin_user:
            print("Admin user already exists, updating subscription...")
        else:
            print("Creating new admin user...")
            # Create admin user
            admin_user = User(
                email='admin@aksjeradar.trade',
                username='aksjeradar_admin',
                password_hash=generate_password_hash('AksjeRadar2024!'),
                created_at=datetime.utcnow(),
                is_admin=True,
                has_subscription=True,
                subscription_type='lifetime',
                subscription_start=datetime.utcnow(),
                subscription_end=None,  # Never expires for lifetime
                trial_used=False,  # No need for trial
                trial_start=None
            )
            db.session.add(admin_user)
            db.session.flush()  # Get the user ID
        
        # Update existing admin user to ensure proper permissions
        admin_user.is_admin = True
        admin_user.has_subscription = True
        admin_user.subscription_type = 'lifetime'
        admin_user.subscription_start = datetime.utcnow()
        admin_user.subscription_end = None  # Never expires
        admin_user.trial_used = False
        admin_user.trial_start = None
        
        # Commit changes
        db.session.commit()
        
        print(f"✅ Admin user created/updated successfully!")
        print(f"📧 Email: admin@aksjeradar.trade")
        print(f"🔑 Password: AksjeRadar2024!")
        print(f"🎯 Role: admin")
        print(f"💎 Subscription: Lifetime (never expires)")
        print(f"🆔 User ID: {admin_user.id}")
        print(f"📊 Active subscription: {admin_user.has_active_subscription()}")
        print(f"🔐 Admin status: {admin_user.is_admin}")
        
        return admin_user

if __name__ == '__main__':
    try:
        create_admin_user()
        print("\n🎉 Admin user setup complete!")
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        import traceback
        traceback.print_exc()
