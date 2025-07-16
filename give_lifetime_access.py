#!/usr/bin/env python3
"""
Script to give lifetime access to specific users
"""
import sys
sys.path.insert(0, '/workspaces/aksjeny')

from app import create_app, db
from app.models.user import User
from datetime import datetime, timedelta

def give_lifetime_access():
    app = create_app()
    with app.app_context():
        # List of users to give lifetime access
        users_to_update = [
            'tonje',
            'eirik',
            'helene721@gmail.com'  # Add the main user too
        ]
        
        for user_identifier in users_to_update:
            # Try to find user by username or email
            user = User.query.filter(
                (User.username == user_identifier) | 
                (User.email == user_identifier)
            ).first()
            
            if user:
                # Give lifetime subscription
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                user.subscription_start = datetime.utcnow()
                user.subscription_end = None  # Lifetime has no end
                
                print(f"✓ Updated {user.username or user.email} to lifetime access")
            else:
                print(f"✗ User {user_identifier} not found")
        
        # Commit changes
        db.session.commit()
        print("All changes committed successfully!")

if __name__ == '__main__':
    give_lifetime_access()
