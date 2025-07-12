#!/usr/bin/env python3
"""
Test password reset token generation and verification
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models.user import User
from itsdangerous import URLSafeTimedSerializer

app = create_app()
with app.app_context():
    print("=== PASSWORD RESET TOKEN TEST ===")
    
    # Test user
    user = User.query.filter_by(email="helene721@gmail.com").first()
    if not user:
        print("User not found!")
        exit(1)
    
    # Generate token
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(user.email, salt='password-reset-salt')
    print(f"Generated token: {token}")
    
    # Verify token
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
        print(f"Token verified successfully for email: {email}")
        
        # Test the URL format
        from flask import url_for
        reset_url = url_for('main.reset_password', token=token, _external=True)
        print(f"Reset URL: {reset_url}")
        
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
