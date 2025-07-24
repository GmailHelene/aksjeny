#!/usr/bin/env python3
"""
Test access control system to verify security
"""
import requests
import sys

def test_access_control():
    base_url = "https://aksjeradar.trade"
    
    print("🔒 TESTING ACCESS CONTROL SYSTEM")
    print("=" * 50)
    
    # Test endpoints that should redirect unauthenticated users to demo
    protected_endpoints = [
        "/portfolio",
        "/search",
        "/prices", 
        "/analysis/",
        "/pro-tools/",
        "/stocks/",
        "/insider-trading/",
        "/advanced-analytics/",
        "/market-intel/"
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'AccessControlTest/1.0'
    })
    
    print("Testing unauthenticated access to protected endpoints...")
    print()
    
    for endpoint in protected_endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}", allow_redirects=False)
            
            print(f"🔍 {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 302:
                location = response.headers.get('Location', '')
                if '/demo' in location:
                    print(f"   ✅ SECURE - Redirects to demo: {location}")
                elif '/login' in location:
                    print(f"   ⚠️  LOGIN REDIRECT: {location}")
                else:
                    print(f"   ❌ UNEXPECTED REDIRECT: {location}")
            elif response.status_code == 200:
                print(f"   ❌ SECURITY BREACH - Allows unauthenticated access!")
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                
            print()
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            print()
    
    # Test demo page accessibility
    print("Testing demo page accessibility...")
    try:
        response = session.get(f"{base_url}/demo")
        if response.status_code == 200:
            print("✅ Demo page accessible without authentication")
        else:
            print(f"❌ Demo page not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Demo page error: {e}")
    
    print()
    print("🏁 Access control test completed!")

if __name__ == '__main__':
    test_access_control()
