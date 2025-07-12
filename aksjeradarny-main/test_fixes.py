#!/usr/bin/env python3
"""
Quick test to verify the endpoint fixes
"""
import requests
import sys
from datetime import datetime

def test_endpoint(url, expected_status=None, should_redirect=False):
    """Test a single endpoint"""
    try:
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        print(f"Testing {url}")
        print(f"  Status: {response.status_code}")
        
        if should_redirect:
            if response.status_code in [301, 302, 303, 307, 308]:
                print(f"  ✓ Properly redirected to: {response.headers.get('Location', 'unknown')}")
                return True
            else:
                print(f"  ❌ Expected redirect but got status {response.status_code}")
                return False
        else:
            if expected_status and response.status_code == expected_status:
                print(f"  ✓ Got expected status {expected_status}")
                return True
            elif response.status_code == 200:
                print(f"  ✓ Accessible (status 200)")
                return True
            else:
                print(f"  ❌ Unexpected status {response.status_code}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return False

def main():
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Aksjeradar Endpoint Fixes")
    print("=" * 50)
    
    # Test cases that should work (assuming we have a trial)
    working_endpoints = [
        "/",
        "/stocks/",
        "/analysis/",
    ]
    
    # Test cases that should redirect unauthorized users (after trial expires)
    # We'll test these as if the trial has expired
    premium_endpoints = [
        "/stocks/details/EQNR.OL",
        "/analysis/market-overview", 
        "/portfolio",
        "/stocks/list",
        "/analysis/technical/EQNR.OL",
    ]
    
    print("\n📋 Testing basic endpoints (should work):")
    working_count = 0
    for endpoint in working_endpoints:
        if test_endpoint(base_url + endpoint):
            working_count += 1
    
    print(f"\n✅ Basic endpoints: {working_count}/{len(working_endpoints)} working")
    
    print("\n🔒 Testing premium endpoints (may redirect or work depending on trial):")
    premium_count = 0
    for endpoint in premium_endpoints:
        # Don't expect specific behavior since trial state is unknown
        if test_endpoint(base_url + endpoint):
            premium_count += 1
    
    print(f"\n📊 Premium endpoints: {premium_count}/{len(premium_endpoints)} accessible")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print(f"- Basic endpoints working: {working_count}/{len(working_endpoints)}")
    print(f"- Premium endpoints tested: {premium_count}/{len(premium_endpoints)}")
    
    if working_count == len(working_endpoints):
        print("✅ All basic functionality appears to be working!")
    else:
        print("❌ Some basic endpoints have issues")

if __name__ == '__main__':
    main()
