#!/usr/bin/env python3
"""
Debug login issues by checking user credentials and fixing access control
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user

def debug_login_issues():
    """Debug login problems and fix access control"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 DEBUGGING LOGIN ISSUES\n")
        
        # Check all users and their password hashes
        users = User.query.all()
        
        if not users:
            print("❌ No users found in database!")
            return
            
        print(f"Found {len(users)} users:")
        print("-" * 50)
        
        test_password = "aksjeradar2024"
        
        for user in users:
            print(f"\n👤 User: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Has password_hash: {'Yes' if user.password_hash else 'No'}")
            print(f"   Hash length: {len(user.password_hash) if user.password_hash else 0}")
            
            if user.password_hash:
                # Test password
                is_valid = check_password_hash(user.password_hash, test_password)
                print(f"   Password '{test_password}' valid: {is_valid}")
                
                if not is_valid:
                    print(f"   🔧 FIXING password for {user.email}")
                    user.password_hash = generate_password_hash(test_password)
                    print(f"   ✅ Password updated")
                    
            else:
                print(f"   🔧 ADDING password for {user.email}")
                user.password_hash = generate_password_hash(test_password)
                print(f"   ✅ Password set")
                
            # Check subscription status
            print(f"   Has subscription: {user.has_subscription}")
            print(f"   Subscription type: {user.subscription_type}")
            
            # Update exempt users
            exempt_emails = {'helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com', 'tonjekit91@gmail.com'}
            if user.email in exempt_emails:
                print(f"   🌟 EXEMPT USER - updating subscription")
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                
        try:
            db.session.commit()
            print(f"\n✅ All users updated successfully!")
        except Exception as e:
            print(f"\n❌ Error updating users: {e}")
            db.session.rollback()
            
        print(f"\n🔑 Test credentials:")
        print(f"   Email: helene721@gmail.com")
        print(f"   Password: {test_password}")

if __name__ == '__main__':
    debug_login_issues()
