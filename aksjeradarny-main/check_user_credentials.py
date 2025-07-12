#!/usr/bin/env python3
"""
Check user credentials in database
"""
import sys
import os
sys.path.append('/workspaces/aksjeradarny')

from app import create_app
from app.models.user import User

def check_user_credentials():
    app = create_app()
    
    with app.app_context():
        # Check if the user exists
        test_email = "helene721@gmail.com"
        test_username = "helene721"
        
        print(f"Looking for user with email: {test_email}")
        user_by_email = User.query.filter_by(email=test_email).first()
        
        print(f"Looking for user with username: {test_username}")
        user_by_username = User.query.filter_by(username=test_username).first()
        
        # Try the combined query that the login function uses
        user_combined = User.query.filter(
            (User.username == test_email) | 
            (User.email == test_email)
        ).first()
        
        if user_by_email:
            print(f"✅ Found user by email: {user_by_email.username} ({user_by_email.email})")
            print(f"   ID: {user_by_email.id}")
            print(f"   Has subscription: {getattr(user_by_email, 'has_subscription', 'N/A')}")
            print(f"   Is admin: {getattr(user_by_email, 'is_admin', 'N/A')}")
            
            # Test password
            test_password = "Soda2001??"
            if user_by_email.check_password(test_password):
                print(f"✅ Password is correct for {test_password}")
            else:
                print(f"❌ Password is wrong for {test_password}")
                
                # Try other possible passwords
                other_passwords = ["Soda2001??", "soda2001??", "Soda2001", "helene721"]
                for pwd in other_passwords:
                    if user_by_email.check_password(pwd):
                        print(f"✅ Correct password is: {pwd}")
                        break
                else:
                    print("❌ None of the tested passwords work")
        else:
            print("❌ No user found by email")
            
        if user_by_username:
            print(f"✅ Found user by username: {user_by_username.username} ({user_by_username.email})")
        else:
            print("❌ No user found by username")
            
        if user_combined:
            print(f"✅ Combined query found: {user_combined.username} ({user_combined.email})")
        else:
            print("❌ Combined query found no user")
            
        # List all users to see what we have
        print("\n--- All users in database ---")
        all_users = User.query.all()
        for user in all_users:
            print(f"  {user.id}: {user.username} ({user.email})")

if __name__ == "__main__":
    check_user_credentials()
