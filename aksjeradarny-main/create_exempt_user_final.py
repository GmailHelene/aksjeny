#!/usr/bin/env python3
"""
Simple user verification and creation script
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def main():
    app = create_app()
    
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(email='tonjekit91@gmail.com').first()
        
        if user:
            print("✅ User tonjekit91@gmail.com already exists")
            print(f"   Admin: {user.is_admin}")
            print(f"   Subscription: {user.subscription_type}")
            return
        
        # Create the user
        password_hash = generate_password_hash('aksjeradar2024')
        
        new_user = User(
            username='tonjekit91',
            email='tonjekit91@gmail.com',
            password_hash=password_hash,
            has_subscription=True,
            subscription_type='lifetime',
            subscription_start=datetime.utcnow(),
            subscription_end=datetime.utcnow() + timedelta(days=36500),  # 100 years
            is_admin=True,
            trial_used=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        print("✅ User tonjekit91@gmail.com created successfully")
        print("   Email: tonjekit91@gmail.com")
        print("   Password: aksjeradar2024")
        print("   Admin: True")
        print("   Subscription: lifetime")

if __name__ == "__main__":
    main()
