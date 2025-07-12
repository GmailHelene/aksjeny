#!/usr/bin/env python3
"""
Script to ensure exempt users always have active subscriptions.
Run this script to automatically set the exempt emails to have lifetime subscriptions.
"""

from app import create_app
from app.extensions import db
from app.models.user import User
from datetime import datetime

EXEMPT_EMAILS = {'helene@luxushair.com', 'helene@luxushair.com' , 'helene721@gmail.com'}

def ensure_exempt_users_have_subscriptions():
    """Ensure exempt users always have active subscriptions"""
    app = create_app()
    with app.app_context():
        for email in EXEMPT_EMAILS:
            user = User.query.filter_by(email=email).first()
            if user:
                # Update subscription details
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                user.subscription_start = datetime.utcnow()
                user.subscription_end = None  # Lifetime has no end
                user.is_admin = True
                print(f"Updated subscription for {email}")
            else:
                # Create user if doesn't exist
                username = email.split('@')[0]
                user = User(
                    username=username,
                    email=email,
                    has_subscription=True,
                    subscription_type='lifetime',
                    subscription_start=datetime.utcnow(),
                    subscription_end=None,
                    is_admin=True
                )
                user.set_password('defaultpassword123')  # They should change this
                db.session.add(user)
                print(f"Created user with subscription for {email}")
        
        db.session.commit()
        print("All exempt users now have active lifetime subscriptions.")

if __name__ == '__main__':
    ensure_exempt_users_have_subscriptions()
