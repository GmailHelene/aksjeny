#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

from app import create_app
from app.extensions import db
from app.models.user import User

def test_login():
    """Test login functionality"""
    app = create_app()
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        print(f"🔍 Found {len(users)} users in database")
        
        for user in users:
            print(f"\n👤 User: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Has password: {'Yes' if hasattr(user, 'password_hash') and user.password_hash else 'No'}")
            
            # Test with the password we set
            if hasattr(user, 'password_hash') and user.password_hash:
                print(f"   Password hash: {user.password_hash[:20]}...")
                
                # Test the password
                test_password = "aksjeradar2024"
                if user.check_password(test_password):
                    print(f"   ✅ Login test PASSED with password: {test_password}")
                else:
                    print(f"   ❌ Login test FAILED with password: {test_password}")
            else:
                print(f"   ⚠️ No password hash found")

if __name__ == "__main__":
    test_login()
