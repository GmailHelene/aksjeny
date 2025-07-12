#!/usr/bin/env python3
"""
Script to fix user login and password reset issues
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
from werkzeug.security import generate_password_hash

def fix_user_issues():
    """Fix user login and password reset issues"""
    app = create_app()
    
    with app.app_context():
        # Test user email
        email = "helene721@gmail.com"
        password = "Soda2001??"
        
        print(f"Looking for user with email: {email}")
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"User found: {user.username} ({user.email})")
            print(f"Current password hash: {user.password_hash}")
            print(f"Has subscription: {user.has_subscription}")
            print(f"Is admin: {user.is_admin}")
            
            # Update password
            print(f"\nUpdating password to: {password}")
            user.set_password(password)
            
            # Ensure user has proper permissions
            user.has_subscription = True
            user.subscription_type = 'lifetime'
            user.is_admin = True
            
            try:
                db.session.commit()
                print("✅ User updated successfully!")
                
                # Test password
                if user.check_password(password):
                    print("✅ Password verification successful!")
                else:
                    print("❌ Password verification failed!")
                    
            except Exception as e:
                print(f"❌ Error updating user: {e}")
                db.session.rollback()
        else:
            print(f"❌ User not found. Creating new user...")
            
            # Create new user
            username = email.split('@')[0]
            user = User(
                username=username,
                email=email,
                has_subscription=True,
                subscription_type='lifetime',
                is_admin=True
            )
            user.set_password(password)
            
            try:
                db.session.add(user)
                db.session.commit()
                print(f"✅ User created successfully!")
                print(f"Username: {user.username}")
                print(f"Email: {user.email}")
                print(f"Password: {password}")
            except Exception as e:
                print(f"❌ Error creating user: {e}")
                db.session.rollback()

if __name__ == '__main__':
    fix_user_issues()
