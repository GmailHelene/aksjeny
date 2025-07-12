#!/usr/bin/env python3
"""
Check and fix Helene's user access
"""
import sys
import os

# Add the project root to Python path
project_root = '/workspaces/aksjeradarv5'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.models.user import User
from app.extensions import db
from datetime import datetime

def check_Helene_access():
    """Check and ensure Helene has proper access"""
    app = create_app()
    
    with app.app_context():
        email = "helene@luxushair.com"
        
        print(f"Checking user: {email}")
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"✅ User found: {user.username} ({user.email})")
            print(f"Has subscription: {user.has_subscription}")
            print(f"Subscription type: {user.subscription_type}")
            print(f"Is admin: {user.is_admin}")
            
            # Test common passwords
            test_passwords = ['aksjeradar2024', 'defaultpassword123', 'Soda2001??']
            password_found = None
            
            for pwd in test_passwords:
                if user.check_password(pwd):
                    password_found = pwd
                    print(f"✅ Current password: {pwd}")
                    break
            
            if not password_found:
                print("❌ Password not found among common ones")
                
            # Ensure proper access
            user.has_subscription = True
            user.subscription_type = 'lifetime'
            user.subscription_start = datetime.utcnow()
            user.subscription_end = None
            user.is_admin = True
            
            # Set standard password if needed
            if not password_found:
                user.set_password('aksjeradar2024')
                print("🔧 Set password to: aksjeradar2024")
            
            try:
                db.session.commit()
                print("✅ User access updated successfully!")
            except Exception as e:
                print(f"❌ Error updating user: {e}")
                db.session.rollback()
                
        else:
            print(f"❌ User not found. Creating new user...")
            
            # Create new user
            username = email.split('@')[0].replace('.', '')  # Remove dots
            user = User(
                username=username,
                email=email,
                has_subscription=True,
                subscription_type='lifetime',
                subscription_start=datetime.utcnow(),
                subscription_end=None,
                is_admin=True
            )
            user.set_password('aksjeradar2024')
            
            try:
                db.session.add(user)
                db.session.commit()
                print(f"✅ User created successfully!")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Password: aksjeradar2024")
            except Exception as e:
                print(f"❌ Error creating user: {e}")
                db.session.rollback()

if __name__ == '__main__':
    check_Helene_access()
