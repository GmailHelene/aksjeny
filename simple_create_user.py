#!/usr/bin/env python3
"""
Simple script to create a test user for testing logged-in functionality
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_test_user():
    app = create_app()
    
    with app.app_context():
        try:
            # Create test user
            test_user = User.query.filter_by(username='testuser').first()
            if not test_user:
                test_user = User(
                    username='testuser',
                    email='test@aksjeradar.no',
                    password_hash=generate_password_hash('test123'),
                    is_admin=False,
                    email_verified=True,
                    has_subscription=True,
                    subscription_type='pro',
                    subscription_start=datetime.utcnow(),
                    subscription_end=datetime.utcnow() + timedelta(days=30)
                )
                db.session.add(test_user)
                print("✅ Created test user: testuser / test123")
            else:
                # Update existing user to ensure they have subscription
                test_user.has_subscription = True
                test_user.subscription_type = 'pro'
                test_user.subscription_start = datetime.utcnow()
                test_user.subscription_end = datetime.utcnow() + timedelta(days=30)
                print("✅ Updated test user with pro subscription")
            
            db.session.commit()
            print("✅ Test user ready for login testing")
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_test_user()
    sys.exit(0 if success else 1)
