#!/usr/bin/env python3
"""
Test script for exempt users and forgot password functionality
"""
import sys
import os
sys.path.append('/workspaces/aksjeny')

from app import create_app, db
from app.models.user import User
from app.utils.access_control import EXEMPT_EMAILS

def test_exempt_users():
    """Test that exempt users can login without issues"""
    print("🔍 TESTING EXEMPT USERS LOGIN")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        print(f"📧 Exempt emails defined: {EXEMPT_EMAILS}")
        print()
        
        for email in EXEMPT_EMAILS:
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"✅ USER FOUND: {email}")
                print(f"   👤 Username: {user.username}")
                print(f"   🔑 Password hash exists: {bool(user.password_hash)}")
                print(f"   👑 Is Admin: {user.is_admin}")
                print(f"   💎 Has Subscription: {user.has_subscription}")
                print(f"   📅 Subscription Type: {user.subscription_type}")
                print(f"   🔓 Is Active: {user.is_active if hasattr(user, 'is_active') else 'No is_active field'}")
                
                # Test password verification
                test_password = "aksjeradar2024"
                if user.check_password(test_password):
                    print(f"   ✅ Password verification: SUCCESS")
                else:
                    print(f"   ❌ Password verification: FAILED")
                    
                print()
            else:
                print(f"❌ USER NOT FOUND: {email}")
                print()
        
        # Test specific user creation if missing
        missing_users = []
        for email in EXEMPT_EMAILS:
            user = User.query.filter_by(email=email).first()
            if not user:
                missing_users.append(email)
        
        if missing_users:
            print(f"🚨 MISSING USERS: {missing_users}")
            print("Run create_missing_users.py to create them")
        else:
            print("✅ ALL EXEMPT USERS EXIST")

def test_forgot_password():
    """Test forgot password functionality"""
    print("\n🔍 TESTING FORGOT PASSWORD FUNCTIONALITY")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Check if forgot password templates exist
        template_files = [
            '/workspaces/aksjeny/app/templates/forgot_password.html',
            '/workspaces/aksjeny/app/templates/reset_password.html'
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                print(f"✅ Template exists: {template_file}")
            else:
                print(f"❌ Template missing: {template_file}")
        
        # Test reset token generation for exempt users
        print("\n🔗 Testing reset token generation:")
        for email in EXEMPT_EMAILS:
            user = User.query.filter_by(email=email).first()
            if user:
                try:
                    # Check if user has reset token methods
                    if hasattr(user, 'generate_reset_token'):
                        token = user.generate_reset_token()
                        print(f"✅ {email}: Reset token generated successfully")
                        
                        # Test token validation
                        if hasattr(user, 'validate_reset_token'):
                            if user.validate_reset_token(token):
                                print(f"✅ {email}: Reset token validation successful")
                            else:
                                print(f"❌ {email}: Reset token validation failed")
                        else:
                            print(f"⚠️ {email}: No validate_reset_token method")
                    else:
                        print(f"❌ {email}: No generate_reset_token method")
                except Exception as e:
                    print(f"❌ {email}: Error generating token: {e}")
            else:
                print(f"❌ {email}: User not found")

def test_login_endpoints():
    """Test login endpoints are working"""
    print("\n🔍 TESTING LOGIN ENDPOINTS")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Test app routes
        print("📋 Available routes:")
        for rule in app.url_map.iter_rules():
            if 'login' in rule.rule or 'password' in rule.rule or 'auth' in rule.rule:
                print(f"   {rule.rule} -> {rule.endpoint}")
        
        # Test URL generation
        try:
            from flask import url_for
            login_url = url_for('main.login')
            print(f"✅ Login URL: {login_url}")
            
            forgot_url = url_for('main.forgot_password')
            print(f"✅ Forgot Password URL: {forgot_url}")
            
            reset_url = url_for('main.reset_password', token='test-token')
            print(f"✅ Reset Password URL: {reset_url}")
        except Exception as e:
            print(f"❌ Error generating URLs: {e}")

if __name__ == "__main__":
    test_exempt_users()
    test_forgot_password()
    test_login_endpoints()
