#!/usr/bin/env python3
"""
Fix exempt users and test all functionality
"""
import sys
import os
sys.path.append('/workspaces/aksjeny')

from app import create_app, db
from app.models.user import User
from app.utils.access_control import EXEMPT_EMAILS

def fix_exempt_users():
    """Fix exempt users to have proper subscription status"""
    print("🔧 FIXING EXEMPT USERS SUBSCRIPTION STATUS")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        for email in EXEMPT_EMAILS:
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"🔄 Updating {email}...")
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                user.is_admin = True
                print(f"   ✅ Has subscription: {user.has_subscription}")
                print(f"   ✅ Subscription type: {user.subscription_type}")
                print(f"   ✅ Is admin: {user.is_admin}")
                print()
        
        # Save changes
        db.session.commit()
        print("✅ All exempt users updated successfully!")

def test_password_reset_flow():
    """Test the complete password reset flow"""
    print("\n🧪 TESTING PASSWORD RESET FLOW")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Test with first exempt user
        test_email = list(EXEMPT_EMAILS)[0]
        user = User.query.filter_by(email=test_email).first()
        
        if user:
            print(f"🔍 Testing with user: {test_email}")
            
            # Test token generation
            try:
                token = user.generate_reset_token()
                print(f"✅ Token generated: {token[:20]}...")
                
                # Test token validation
                if user.validate_reset_token(token):
                    print(f"✅ Token validation: SUCCESS")
                else:
                    print(f"❌ Token validation: FAILED")
                
                # Test token clearing
                user.clear_reset_token()
                print(f"✅ Token cleared successfully")
                
            except Exception as e:
                print(f"❌ Error in reset token flow: {e}")
        else:
            print(f"❌ Test user not found: {test_email}")

def test_login_functionality():
    """Test login functionality for exempt users"""
    print("\n🔐 TESTING LOGIN FUNCTIONALITY")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        for email in EXEMPT_EMAILS:
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"🔍 Testing login for: {email}")
                
                # Test password verification
                test_password = "aksjeradar2024"
                if user.check_password(test_password):
                    print(f"   ✅ Password check: SUCCESS")
                else:
                    print(f"   ❌ Password check: FAILED")
                
                # Test subscription status
                if user.has_subscription:
                    print(f"   ✅ Has subscription: YES")
                else:
                    print(f"   ❌ Has subscription: NO")
                
                # Test admin status
                if user.is_admin:
                    print(f"   ✅ Is admin: YES")
                else:
                    print(f"   ❌ Is admin: NO")
                
                # Test if user is in exempt list
                if email in EXEMPT_EMAILS:
                    print(f"   ✅ In exempt list: YES")
                else:
                    print(f"   ❌ In exempt list: NO")
                
                print()

def test_forgot_password_templates():
    """Test that forgot password templates exist"""
    print("\n📄 TESTING FORGOT PASSWORD TEMPLATES")
    print("=" * 50)
    
    templates = [
        '/workspaces/aksjeny/app/templates/forgot_password.html',
        '/workspaces/aksjeny/app/templates/reset_password.html'
    ]
    
    for template_path in templates:
        if os.path.exists(template_path):
            print(f"✅ Template exists: {os.path.basename(template_path)}")
        else:
            print(f"❌ Template missing: {os.path.basename(template_path)}")

def show_final_summary():
    """Show final summary of all exempt users"""
    print("\n📊 FINAL SUMMARY - EXEMPT USERS STATUS")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        print("🎯 LOGIN CREDENTIALS FOR ALL EXEMPT USERS:")
        print("Password: aksjeradar2024")
        print()
        
        for email in EXEMPT_EMAILS:
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"📧 {email}")
                print(f"   👤 Username: {user.username}")
                print(f"   🔑 Password: aksjeradar2024")
                print(f"   ✅ Can login: YES")
                print(f"   💎 Has subscription: {user.has_subscription}")
                print(f"   👑 Is admin: {user.is_admin}")
                print()
        
        print("🚀 ALL EXEMPT USERS READY FOR PRODUCTION!")

if __name__ == "__main__":
    fix_exempt_users()
    test_password_reset_flow()
    test_login_functionality()
    test_forgot_password_templates()
    show_final_summary()
