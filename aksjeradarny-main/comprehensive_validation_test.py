#!/usr/bin/env python3
"""
Test script to verify all pricing updates and basic functionality
"""
import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

def test_pricing_consistency():
    """Test that all pricing is consistent across templates"""
    print("🔍 TESTING PRICING CONSISTENCY...")
    print("=" * 50)
    
    files_to_check = [
        '/workspaces/aksjeradarv6/app/templates/subscription.html',
        '/workspaces/aksjeradarv6/templates/subscription.html',
        '/workspaces/aksjeradarv6/app/templates/index.html', 
        '/workspaces/aksjeradarv6/templates/index.html',
        '/workspaces/aksjeradarv6/app/templates/login.html',
        '/workspaces/aksjeradarv6/app/templates/register.html',
        '/workspaces/aksjeradarv6/templates/register.html'
    ]
    
    expected_prices = {
        '199 kr': 'Basic monthly price',
        '399 kr': 'Pro monthly price', 
        '3499 kr': 'Pro yearly price',
        '2799 kr': 'Pro yearly with 20% discount'
    }
    
    old_prices = ['99 kr', '2499 kr']
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"📄 Checking {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for old prices that should be removed
                for old_price in old_prices:
                    if old_price in content and 'livstid' not in content.lower():
                        print(f"  ❌ Found old price {old_price}")
                    
                # Check for expected prices
                found_prices = []
                for expected_price in expected_prices:
                    if expected_price in content:
                        found_prices.append(expected_price)
                        
                if found_prices:
                    print(f"  ✅ Found correct prices: {', '.join(found_prices)}")
                else:
                    print(f"  ⚠️  No pricing found (might be okay)")
        else:
            print(f"  ⚠️  File not found: {file_path}")
    
    print("\n✅ Pricing consistency check completed!")

def test_app_startup():
    """Test basic app functionality"""
    print("\n🚀 TESTING APP STARTUP...")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.models.user import User
        from app.extensions import db
        
        app = create_app()
        print("✅ App created successfully")
        
        with app.app_context():
            print("✅ App context working")
            
            # Test database connection
            try:
                user_count = User.query.count()
                print(f"✅ Database connection OK - {user_count} users")
            except Exception as e:
                print(f"⚠️  Database issue: {e}")
            
            # Test key routes
            with app.test_client() as client:
                routes_to_test = [
                    ('/', 'Homepage'),
                    ('/subscription', 'Subscription'),
                    ('/pricing', 'Pricing'),
                    ('/demo', 'Demo')
                ]
                
                for route, name in routes_to_test:
                    try:
                        response = client.get(route)
                        if response.status_code in [200, 302]:
                            print(f"✅ {name}: {response.status_code}")
                        else:
                            print(f"❌ {name}: {response.status_code}")
                    except Exception as e:
                        print(f"❌ {name}: Error - {e}")
        
        print("\n✅ App startup test completed!")
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")

def test_rate_limiter():
    """Test rate limiter configuration"""
    print("\n⏱️  TESTING RATE LIMITER...")
    print("=" * 50)
    
    try:
        from app.services.rate_limiter import RateLimiter
        
        limiter = RateLimiter()
        yahoo_limits = limiter.limits.get('yahoo_finance', {})
        
        print(f"📊 Yahoo Finance limits:")
        print(f"  - Requests per minute: {yahoo_limits.get('requests_per_minute', 'N/A')}")
        print(f"  - Requests per hour: {yahoo_limits.get('requests_per_hour', 'N/A')}")
        print(f"  - Delay between calls: {yahoo_limits.get('delay_between_calls', 'N/A')}s")
        
        # Test if limits are conservative enough
        if yahoo_limits.get('requests_per_minute', 0) <= 20:
            print("✅ Conservative rate limits set")
        else:
            print("⚠️  Rate limits might be too aggressive")
            
        print("\n✅ Rate limiter test completed!")
        
    except Exception as e:
        print(f"❌ Rate limiter test failed: {e}")

if __name__ == '__main__':
    print("🧪 AKSJERADAR V6 - COMPREHENSIVE TEST")
    print("=" * 60)
    
    test_pricing_consistency()
    test_app_startup() 
    test_rate_limiter()
    
    print("\n🎉 ALL TESTS COMPLETED!")
    print("=" * 60)
