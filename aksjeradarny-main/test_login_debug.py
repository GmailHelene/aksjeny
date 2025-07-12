#!/usr/bin/env python3
"""
Debug script to test login functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()
with app.app_context():
    print("=== LOGIN DEBUG TEST ===")
    
    # Test the user you mentioned
    test_email = "helene721@gmail.com"
    user = User.query.filter_by(email=test_email).first()
    
    if user:
        print(f"User found: {user.email}")
        print(f"Username: {user.username}")
        print(f"Has password hash: {bool(user.password_hash)}")
        print(f"Is admin: {user.is_admin}")
        print(f"Has subscription: {user.has_subscription}")
        
        # Test password checking
        test_passwords = ['aksjeradar2024', 'Soda2001??', 'dittnyevalgtepw']
        
        for pwd in test_passwords:
            result = user.check_password(pwd)
            print(f"Password '{pwd}': {'✓' if result else '✗'}")
            
    else:
        print(f"No user found with email: {test_email}")
        
        # Show all users
        all_users = User.query.all()
        print(f"\nAll users in database ({len(all_users)}):")
        for u in all_users:
            print(f"- {u.email} (username: {u.username})")
