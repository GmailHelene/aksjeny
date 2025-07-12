#!/usr/bin/env python3
"""
Script to ensure exempt users are properly configured with full access
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_exempt_users():
    """Ensure exempt users have full access"""
    print("🔧 Setting up exempt users...")
    
    try:
        from app import create_app
        from app.extensions import db
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        from datetime import datetime, timedelta
        
        app = create_app()
        
        with app.app_context():
            exempt_users = [
                {
                    'email': 'helene721@gmail.com',
                    'username': 'helene_luxus',
                    'password': 'aksjeradar2024'
                },
                {
                    'email': 'helene@luxushair.com', 
                    'username': 'helene_luxus_admin',
                    'password': 'aksjeradar2024'
                },
                {
                    'email': 'eiriktollan.berntsen@gmail.com',
                    'username': 'eiriktollan',
                    'password': 'aksjeradar2024'
                },
                {
                    'email': 'tonjekit91@gmail.com',
                    'username': 'tonjekit91',
                    'password': 'aksjeradar2024'
                }
            ]
            
            for user_data in exempt_users:
                user = User.query.filter_by(email=user_data['email']).first()
                
                if not user:
                    # Create new user
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=generate_password_hash(user_data['password']),
                        is_active=True,
                        subscription_type='lifetime',
                        subscription_start=datetime.utcnow(),
                        subscription_end=datetime.utcnow() + timedelta(days=36500),  # 100 years
                        trial_start=datetime.utcnow(),
                        trial_end=datetime.utcnow() + timedelta(days=36500),
                        is_admin=True
                    )
                    db.session.add(user)
                    print(f"✅ Created exempt user: {user_data['email']}")
                else:
                    # Update existing user
                    user.is_active = True
                    user.subscription_type = 'lifetime'
                    user.subscription_start = datetime.utcnow()
                    user.subscription_end = datetime.utcnow() + timedelta(days=36500)
                    user.trial_start = datetime.utcnow()
                    user.trial_end = datetime.utcnow() + timedelta(days=36500)
                    user.is_admin = True
                    # Update password if needed
                    user.password_hash = generate_password_hash(user_data['password'])
                    print(f"✅ Updated exempt user: {user_data['email']}")
            
            db.session.commit()
            print("🎉 All exempt users configured successfully!")
            
            # Verify access control
            from app.utils.access_control import EXEMPT_EMAILS
            print(f"\n📋 Exempt emails in access control: {EXEMPT_EMAILS}")
            
            for user_data in exempt_users:
                if user_data['email'] in EXEMPT_EMAILS:
                    print(f"✅ {user_data['email']} is in exempt list")
                else:
                    print(f"❌ {user_data['email']} NOT in exempt list")
    
    except Exception as e:
        print(f"❌ Error setting up exempt users: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_exempt_users()
