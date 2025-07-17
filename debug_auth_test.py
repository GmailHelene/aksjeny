#!/usr/bin/env python3
"""
Test only the specific failing endpoints to identify the authentication issue
"""
import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

try:
    from app import create_app
    
    app = create_app('testing')
    
    print("Testing specific failing endpoints...")
    
    with app.test_client() as client:
        # Test the endpoints that were redirecting to login
        endpoints_to_test = [
            '/api/crypto/trending',
            '/api/economic/indicators', 
            '/api/market/sectors'
        ]
        
        for endpoint in endpoints_to_test:
            print(f"\n🔗 Testing {endpoint}")
            try:
                response = client.get(endpoint)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = json.loads(response.data)
                        print(f"✅ Success: {data.get('success', 'No success field')}")
                    except:
                        print(f"✅ Response received but not JSON")
                elif response.status_code == 302:
                    print(f"❌ Redirect (likely to login)")
                    print(f"Location: {response.headers.get('Location', 'No location header')}")
                else:
                    print(f"❌ Status {response.status_code}")
                    print(f"Response: {response.data.decode()[:200]}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
        # Test access control decorators
        print(f"\n🔍 Testing with app context...")
        with app.app_context():
            print(f"App name: {app.name}")
            print(f"Testing mode: {app.config.get('TESTING', False)}")
            print(f"CSRF enabled: {app.config.get('WTF_CSRF_ENABLED', True)}")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
