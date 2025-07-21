#!/usr/bin/env python3
"""
Test script for endpoint access control
"""
import requests
import sys

BASE_URL = "http://localhost:5000"

def test_endpoint(path, expected_redirect=None):
    """Test an endpoint and check if it redirects correctly"""
    print(f"\n🔍 Testing: {path}")
    
    try:
        # Make request without following redirects
        response = requests.get(f"{BASE_URL}{path}", allow_redirects=False)
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"   ↳ 302 Redirect to: {redirect_location}")
            
            if expected_redirect and expected_redirect in redirect_location:
                print(f"   ✅ Correctly redirected to {expected_redirect}")
                return True
            elif expected_redirect:
                print(f"   ❌ Expected redirect to {expected_redirect}, got {redirect_location}")
                return False
            else:
                print(f"   ⚠️  Unexpected redirect to {redirect_location}")
                return False
                
        elif response.status_code == 200:
            print(f"   ✅ 200 OK - Accessible without redirect")
            return True if not expected_redirect else False
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection error - server not running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Testing endpoint redirects for unauthenticated users...")
    
    # Test endpoints that should redirect to demo
    test_cases = [
        ("/stocks", "/demo"),
        ("/stocks/list", "/demo"),
        ("/stocks/list/oslo", "/demo"),
        ("/stocks/details/EQNR", "/demo"),
        ("/analysis", "/demo"),
        ("/analysis/ai", "/demo"),
        ("/portfolio", "/demo"),
    ]
    
    # Test endpoints that should be accessible without auth
    open_endpoints = [
        ("/", None),  # Homepage should be accessible
        ("/demo", None),  # Demo should be accessible
        ("/login", None),  # Login should be accessible
        ("/register", None),  # Register should be accessible
        ("/pricing", None),  # Pricing should be accessible
    ]
    
    passed = 0
    total = 0
    
    print("\n📋 Testing protected endpoints (should redirect to /demo):")
    for path, expected_redirect in test_cases:
        total += 1
        if test_endpoint(path, expected_redirect):
            passed += 1
    
    print("\n📋 Testing open endpoints (should be accessible):")
    for path, expected_redirect in open_endpoints:
        total += 1
        if test_endpoint(path, expected_redirect):
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Access control is working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the endpoint configurations.")
        sys.exit(1)

if __name__ == "__main__":
    main()
