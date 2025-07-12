#!/usr/bin/env python3
"""
Script to test password reset functionality
"""
import sys
import os

# Add the project root to Python path
project_root = '/workspaces/aksjeradarv5'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.models.user import User
from app.extensions import db
from itsdangerous import URLSafeTimedSerializer
from flask import url_for

def test_password_reset():
    """Test password reset token generation and verification"""
    app = create_app()
    
    with app.app_context():
        email = "helene721@gmail.com"
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return
            
        print(f"✅ User found: {user.username} ({user.email})")
        
        # Test token generation
        def generate_reset_token(user, expires_sec=3600):
            s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            return s.dumps(user.email, salt='password-reset-salt')

        def verify_reset_token(token, expires_sec=3600):
            s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            try:
                email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
                print(f"Token verified for email: {email}")
                return User.query.filter_by(email=email).first()
            except Exception as e:
                print(f"Token verification failed: {e}")
                return None
        
        # Generate token
        token = generate_reset_token(user)
        print(f"Generated token: {token}")
        
        # Generate reset URL
        with app.test_request_context():
            reset_url = url_for('main.reset_password', token=token, _external=True)
            print(f"Reset URL: {reset_url}")
        
        # Test token verification
        verified_user = verify_reset_token(token)
        if verified_user:
            print(f"✅ Token verification successful for: {verified_user.email}")
        else:
            print("❌ Token verification failed")
            
        # Test with the actual token from the email log
        email_token = "ImhlbGVuZTcyMUBnbWFpbC5jb20i.aF8kpg.LPjf2ibR9oEMfTJIikc7P7AikvM"
        print(f"\nTesting email token: {email_token}")
        verified_user_email = verify_reset_token(email_token)
        if verified_user_email:
            print(f"✅ Email token verification successful for: {verified_user_email.email}")
        else:
            print("❌ Email token verification failed")

if __name__ == '__main__':
    test_password_reset()
