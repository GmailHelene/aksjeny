#!/usr/bin/env python3
"""
Comprehensive test of all critical functionality
"""

import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

def test_pricing_and_exempts():
    print("🔍 Testing Critical Functionality")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        client = app.test_client()
        
        # 1. Test pricing page
        print("\n📋 Testing: Pricing Page")
        response = client.get('/pricing/')
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            checks = [
                ("Gratis Demo", "Free tier present"),
                ("Basic", "Basic tier present"), 
                ("kr 199", "Basic pricing shown"),
                ("kr 399", "Pro pricing shown"),
                ("Oppgrader til", "Upgrade buttons present")
            ]
            
            for check, description in checks:
                if check in content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
        else:
            print(f"❌ Pricing page failed: {response.status_code}")
        
        # 2. Check exempt emails
        print(f"\n📋 Testing: Exempt Emails")
        with app.app_context():
            from app.utils.access_control import EXEMPT_EMAILS
            print(f"Exempt emails found: {EXEMPT_EMAILS}")
            
            # Check if users exist
            from app.models.user import User
            for email in EXEMPT_EMAILS:
                user = User.query.filter_by(email=email).first()
                if user:
                    print(f"✅ {email}: User exists, subscription={user.has_subscription}")
                else:
                    print(f"❌ {email}: User not found")
        
        # 3. Check subscription flow
        print(f"\n📋 Testing: Subscription Flow") 
        
        # Test subscription page
        response = client.get('/subscription')
        print(f"Subscription page: {response.status_code}")
        
        # Test pricing endpoints
        pricing_routes = ['/pricing/', '/pricing/upgrade/basic']
        for route in pricing_routes:
            response = client.get(route)
            print(f"{route}: {response.status_code}")
                    
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pricing_and_exempts()
