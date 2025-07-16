#!/usr/bin/env python3
"""
Script to create tonje and eirik users with lifetime access
"""
import sys
sys.path.insert(0, '/workspaces/aksjeny')

from app import create_app, db
from app.models.user import User
from datetime import datetime

def create_users():
    app = create_app()
    with app.app_context():
        # Create tonje user
        tonje = User.query.filter_by(username='tonje').first()
        if not tonje:
            tonje = User(
                username='tonje',
                email='tonje@aksjeradar.trade',
                has_subscription=True,
                subscription_type='lifetime',
                subscription_start=datetime.utcnow(),
                subscription_end=None
            )
            tonje.set_password('aksjeradar2024')
            db.session.add(tonje)
            print("✓ Created tonje user with lifetime access")
        else:
            tonje.has_subscription = True
            tonje.subscription_type = 'lifetime'
            tonje.subscription_start = datetime.utcnow()
            tonje.subscription_end = None
            print("✓ Updated tonje user to lifetime access")
        
        # Create eirik user
        eirik = User.query.filter_by(username='eirik').first()
        if not eirik:
            eirik = User(
                username='eirik',
                email='eirik@aksjeradar.trade',
                has_subscription=True,
                subscription_type='lifetime',
                subscription_start=datetime.utcnow(),
                subscription_end=None
            )
            eirik.set_password('aksjeradar2024')
            db.session.add(eirik)
            print("✓ Created eirik user with lifetime access")
        else:
            eirik.has_subscription = True
            eirik.subscription_type = 'lifetime'
            eirik.subscription_start = datetime.utcnow()
            eirik.subscription_end = None
            print("✓ Updated eirik user to lifetime access")
        
        # Commit changes
        db.session.commit()
        print("All users created/updated successfully!")

if __name__ == '__main__':
    create_users()
