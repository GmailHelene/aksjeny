#!/usr/bin/env python3
"""
Script to create or update test users for login testing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, db
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_users():
    app = create_app()
    
    with app.app_context():
        print("Creating/updating test users...")
        
        # Check for helene user - use existing one if found
        helene = User.query.filter_by(username='helene').first()
        if not helene:
            helene = User.query.filter_by(email='helene721@gmail.com').first()
        
        if not helene:
            print("Creating new helene user...")
            helene = User(
                username='helene',
                email='helene721@gmail.com',
                password_hash=generate_password_hash('password123'),
                created_at=datetime.utcnow(),
                has_subscription=False,
                subscription_type='free',
                trial_used=False,
                reports_used_this_month=0,
                last_reset_date=datetime.utcnow(),
                is_admin=True,
                language='no',
                notification_settings=None,
                two_factor_enabled=False,
                two_factor_secret=None,
                email_verified=True,
                is_locked=False,
                last_login=None,
                login_count=0
            )
            db.session.add(helene)
            db.session.commit()
            print("✅ Created helene user")
        else:
            print(f"✅ Found existing helene user: {helene.username} ({helene.email})")
        
        # Check for eirik user
        eirik = User.query.filter_by(username='eirik').first()
        if not eirik:
            eirik = User.query.filter_by(email='eirik@testuser.com').first()
        
        if not eirik:
            print("Creating new eirik user...")
            eirik = User(
                username='eirik',
                email='eirik@testuser.com',
                password_hash=generate_password_hash('password123'),
                created_at=datetime.utcnow(),
                has_subscription=False,
                subscription_type='free',
                trial_used=False,
                reports_used_this_month=0,
                last_reset_date=datetime.utcnow(),
                is_admin=True,
                language='no',
                notification_settings=None,
                two_factor_enabled=False,
                two_factor_secret=None,
                email_verified=True,
                is_locked=False,
                last_login=None,
                login_count=0
            )
            db.session.add(eirik)
            db.session.commit()
            print("✅ Created eirik user")
        else:
            print(f"✅ Found existing eirik user: {eirik.username} ({eirik.email})")
        
        # Verify both users
        print("\nVerifying users...")
        all_users = User.query.all()
        for user in all_users:
            print(f"User: {user.username} ({user.email}) - Admin: {user.is_admin}")
        
        print("\n✅ All users created/verified successfully!")
        print("Login credentials:")
        print("- helene: password123")
        print("- eirik: password123")

if __name__ == '__main__':
    create_test_users()
