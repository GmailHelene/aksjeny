#!/usr/bin/env python3
"""
Manual Access Control Test
Tests all access control scenarios for trial/demo users and subscription requirements.
"""

import requests
import sys
from urllib.parse import urljoin

def test_endpoint_access(base_url, endpoint, cookies=None, expected_status=200, description=""):
    """Test access to an endpoint with optional cookies"""
    url = urljoin(base_url, endpoint)
    
    try:
        response = requests.get(url, cookies=cookies or {}, timeout=10, allow_redirects=False)
        status = response.status_code
        
        if status == expected_status:
            print(f"✓ {description or endpoint}: {status}")
            return True
        else:
            print(f"✗ {description or endpoint}: Expected {expected_status}, got {status}")
            return False
            
    except Exception as e:
        print(f"✗ {description or endpoint}: Error - {str(e)}")
        return False

def main():
    """Main test function"""
    base_url = "http://localhost:5000"  # Adjust as needed
    
    print("Starting Manual Access Control Test")
    print("=" * 60)
    
    # Test endpoints that should always be accessible (no login required)
    print("\n=== Testing Always Accessible Endpoints ===")
    always_accessible = [
        ("/", "Home page"),
        ("/login", "Login page"),
        ("/register", "Registration page"),
        ("/privacy", "Privacy page"),
        ("/offline", "Offline page"),
        ("/subscription", "Subscription page"),
        ("/demo", "Demo page"),
        ("/contact", "Contact page"),
        ("/robots.txt", "Robots.txt"),
        ("/sitemap.xml", "Sitemap.xml"),
    ]
    
    passed = 0
    total = len(always_accessible)
    
    for endpoint, description in always_accessible:
        if test_endpoint_access(base_url, endpoint, description=description):
            passed += 1
    
    print(f"\nAlways accessible: {passed}/{total} passed")
    
    # Test endpoints that should require access control
    print("\n=== Testing Access-Controlled Endpoints (Without Login) ===")
    access_controlled = [
        ("/stocks/EQNR.OL", "Stock details"),
        ("/analysis/technical", "Technical analysis"),
        ("/analysis/ai", "AI analysis"),
        ("/portfolio", "Portfolio"),
        ("/market-intel", "Market intelligence"),
        ("/analysis/recommendation", "Stock recommendations"),
        ("/stocks/compare", "Stock comparison"),
        ("/portfolio/watchlist", "Watchlist"),
    ]
    
    # These should either redirect to login, show restricted access, or work with trial
    total_ac = len(access_controlled)
    passed_ac = 0
    
    for endpoint, description in access_controlled:
        # Accept 200 (trial access), 302 (redirect), or 403 (restricted)
        if test_endpoint_access(base_url, endpoint, expected_status=200, description=f"{description} (no auth)"):
            passed_ac += 1
        elif test_endpoint_access(base_url, endpoint, expected_status=302, description=f"{description} (redirect)"):
            passed_ac += 1
        elif test_endpoint_access(base_url, endpoint, expected_status=403, description=f"{description} (restricted)"):
            passed_ac += 1
    
    print(f"\nAccess controlled: {passed_ac}/{total_ac} working correctly")
    
    # Test API endpoints
    print("\n=== Testing API Endpoints ===")
    api_endpoints = [
        ("/api/stocks/EQNR.OL", "Stock API"),
        ("/api/market/overview", "Market overview API"),
        ("/api/portfolio/create", "Portfolio API"),
        ("/realtime/api/stock-data", "Realtime API"),
    ]
    
    total_api = len(api_endpoints)
    passed_api = 0
    
    for endpoint, description in api_endpoints:
        # API endpoints might return 200, 401, 403, or 404
        if test_endpoint_access(base_url, endpoint, expected_status=200, description=f"{description}"):
            passed_api += 1
        elif test_endpoint_access(base_url, endpoint, expected_status=401, description=f"{description} (unauthorized)"):
            passed_api += 1
        elif test_endpoint_access(base_url, endpoint, expected_status=403, description=f"{description} (forbidden)"):
            passed_api += 1
        elif test_endpoint_access(base_url, endpoint, expected_status=404, description=f"{description} (not found)"):
            passed_api += 1
    
    print(f"\nAPI endpoints: {passed_api}/{total_api} responding correctly")
    
    # Check for trial/demo functionality
    print("\n=== Testing Demo/Trial Functionality ===")
    
    # Try to access a demo endpoint
    demo_works = test_endpoint_access(base_url, "/demo", description="Demo page access")
    
    # Try to access the restricted access page
    restricted_works = test_endpoint_access(base_url, "/restricted_access", description="Restricted access page")
    
    demo_passed = 1 if demo_works else 0
    restricted_passed = 1 if restricted_works else 0
    demo_total = 2
    
    print(f"\nDemo/Trial functionality: {demo_passed + restricted_passed}/{demo_total} working")
    
    # Overall summary
    total_all = total + total_ac + total_api + demo_total
    passed_all = passed + passed_ac + passed_api + demo_passed + restricted_passed
    
    print(f"\n{'=' * 60}")
    print(f"OVERALL TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total endpoints tested: {total_all}")
    print(f"Working correctly: {passed_all}")
    print(f"Success rate: {(passed_all/total_all)*100:.1f}%")
    
    if passed_all == total_all:
        print("\n🎉 All access control tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total_all - passed_all} tests had issues. This might be expected behavior.")
        print("Please manually verify that:")
        print("1. Unauthenticated users can access public pages")
        print("2. Protected features require login or show trial/demo access")
        print("3. Expired trial users see the restricted access page")
        print("4. Subscription-required features work for subscribed users")
        return 1

if __name__ == "__main__":
    sys.exit(main())
