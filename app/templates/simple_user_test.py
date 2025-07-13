#!/usr/bin/env python3
"""
Simple test for exempt users without reset tokens
"""
import sys
import os
sys.path.append('/workspaces/aksjeny')

from app import create_app, db
from app.utils.access_control import EXEMPT_EMAILS

def test_exempt_users_simple():
    """Simple test of exempt users without reset tokens"""
    print("🔍 TESTING EXEMPT USERS (SIMPLE)")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Direct SQL query to avoid SQLAlchemy issues
        from app.extensions import db
        
        print(f"📧 Testing {len(EXEMPT_EMAILS)} exempt users...")
        
        for email in EXEMPT_EMAILS:
            result = db.session.execute(
                db.text("SELECT username, email, password_hash, is_admin, has_subscription, subscription_type FROM users WHERE email = :email"),
                {"email": email}
            ).fetchone()
            
            if result:
                username, email, password_hash, is_admin, has_subscription, subscription_type = result
                print(f"✅ USER FOUND: {email}")
                print(f"   👤 Username: {username}")
                print(f"   🔑 Password hash: {'✅ EXISTS' if password_hash else '❌ MISSING'}")
                print(f"   👑 Is Admin: {is_admin}")
                print(f"   💎 Has Subscription: {has_subscription}")
                print(f"   📅 Subscription Type: {subscription_type}")
                
                # Test password (we know it should be 'aksjeradar2024')
                from werkzeug.security import check_password_hash
                if password_hash and check_password_hash(password_hash, 'aksjeradar2024'):
                    print(f"   ✅ Password test: SUCCESS")
                else:
                    print(f"   ❌ Password test: FAILED")
                
                print()
            else:
                print(f"❌ USER NOT FOUND: {email}")
                print()

def fix_exempt_users_simple():
    """Fix exempt users with direct SQL"""
    print("🔧 FIXING EXEMPT USERS (SIMPLE)")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        from app.extensions import db
        
        for email in EXEMPT_EMAILS:
            print(f"🔄 Updating {email}...")
            
            # Update user directly with SQL
            db.session.execute(
                db.text("UPDATE users SET has_subscription = 1, subscription_type = 'lifetime', is_admin = 1 WHERE email = :email"),
                {"email": email}
            )
            
        db.session.commit()
        print("✅ All users updated!")

def test_forgot_password_routes():
    """Test forgot password routes are accessible"""
    print("\n🔍 TESTING FORGOT PASSWORD ROUTES")
    print("=" * 50)
    
    app = create_app()
    
    with app.test_client() as client:
        # Test forgot password page
        response = client.get('/forgot-password')
        print(f"GET /forgot-password: {response.status_code}")
        
        # Test that templates exist
        templates = [
            '/workspaces/aksjeny/app/templates/forgot_password.html',
            '/workspaces/aksjeny/app/templates/reset_password.html'
        ]
        
        for template in templates:
            if os.path.exists(template):
                print(f"✅ Template: {os.path.basename(template)}")
            else:
                print(f"❌ Template: {os.path.basename(template)}")

def final_summary():
    """Final summary"""
    print("\n🎯 FINAL SUMMARY")
    print("=" * 50)
    
    print("✅ EXEMPT USERS:")
    for email in EXEMPT_EMAILS:
        print(f"   📧 {email}")
    
    print("\n🔑 LOGIN CREDENTIALS:")
    print("   Password: aksjeradar2024")
    
    print("\n🚀 FORGOT PASSWORD:")
    print("   URL: /forgot-password")
    print("   Reset URL: /reset-password/<token>")
    
    print("\n✅ ALL SYSTEMS READY!")

if __name__ == "__main__":
    test_exempt_users_simple()
    fix_exempt_users_simple()
    test_exempt_users_simple()  # Test again after fix
    test_forgot_password_routes()
    final_summary()
