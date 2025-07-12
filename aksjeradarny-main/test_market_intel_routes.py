#!/usr/bin/env python3
"""
Quick test for market-intel routes
"""
import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

def test_market_intel_routes():
    """Test market-intel routes"""
    print("🔍 Testing Market Intel Routes")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        client = app.test_client()
        
        # Test routes
        routes_to_test = [
            ('/market-intel/', 'Market Intel Index'),
            ('/market-intel/insider-trading', 'Insider Trading'),
            ('/market-intel/insider-trading?ticker=EQNR.OL', 'Insider Trading with ticker'),
        ]
        
        for route, description in routes_to_test:
            print(f"\n📋 Testing: {description}")
            print(f"🔗 Route: {route}")
            
            try:
                response = client.get(route, follow_redirects=True)
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS")
                elif response.status_code in [301, 302, 303]:
                    print(f"🔄 REDIRECT to: {response.headers.get('Location', 'Unknown')}")
                else:
                    print(f"❌ FAILED: {response.status_code}")
                    if hasattr(response, 'data'):
                        print(f"📄 Response length: {len(response.data)} bytes")
                        # Check if it's a 404 error page
                        if b'Beklager vi fant ikke siden' in response.data:
                            print("🚨 404 Error: Page not found")
                        
            except Exception as e:
                print(f"❌ ERROR: {e}")
        
        # Check registered routes
        print(f"\n📋 All routes containing 'market':")
        with app.app_context():
            for rule in app.url_map.iter_rules():
                if 'market' in rule.rule.lower():
                    print(f"  {rule.endpoint}: {rule.rule}")
                    
    except Exception as e:
        print(f"❌ Failed to create app or test routes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_market_intel_routes()
