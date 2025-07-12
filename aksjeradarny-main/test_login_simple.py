#!/usr/bin/env python3
"""
Test login functionality
"""
import sys
import os

# Add the project root to Python path
project_root = '/workspaces/aksjeradarv5'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.models.user import User

def test_login():
    """Test login credentials"""
    app = create_app()
    
    with app.app_context():
        email = "helene721@gmail.com"
        password = "Soda2001??"
        
        print(f"Testing login for: {email}")
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"❌ User not found: {email}")
            return
            
        print(f"✅ User found: {user.username} ({user.email})")
        
        # Test password
        if user.check_password(password):
            print(f"✅ Password is correct!")
        else:
            print(f"❌ Password is incorrect!")
            
        # Also test with username
        user_by_username = User.query.filter_by(username=user.username).first()
        if user_by_username and user_by_username.check_password(password):
            print(f"✅ Login with username '{user.username}' works!")
        else:
            print(f"❌ Login with username '{user.username}' failed!")

if __name__ == '__main__':
    test_login()
