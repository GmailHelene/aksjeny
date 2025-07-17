#!/usr/bin/env python3
"""
API endpoint test using Flask test client
"""
import sys
import os
import json

# Add the app directory to the path  
sys.path.insert(0, os.path.abspath('.'))

def test_api_endpoints():
    try:
        from app import create_app
        
        # Create test app
        app = create_app('testing')
        client = app.test_client()
        
        print("Testing API endpoints...")
        
        # Test endpoints that should work without authentication
        endpoints_to_test = [
            '/api/crypto/trending',
            '/api/economic/indicators', 
            '/api/market/sectors',
            '/api/stocks/search',
            '/api/stocks/search?q=EQNR',
            '/api/market-data'
        ]
        
        for endpoint in endpoints_to_test:
            print(f"\n🔗 Testing {endpoint}")
            try:
                response = client.get(endpoint)
                if response.status_code == 200:
                    data = json.loads(response.data)
                    if data.get('success'):
                        print(f"✅ {endpoint} - OK")
                    else:
                        print(f"⚠️  {endpoint} - No success flag")
                elif response.status_code == 401:
                    print(f"🔒 {endpoint} - Authentication required")
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    print(f"   Response: {response.data.decode()[:200]}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")
        
        print("\n✅ API endpoint tests completed!")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_api_endpoints()
