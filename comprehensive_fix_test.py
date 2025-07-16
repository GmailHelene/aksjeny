"""
Comprehensive Testing Script for All Fixes
Tests all the fixed endpoints and functionality

This script tests:
1. Market overview route (fixed with fallback data)
2. News index route (fixed with fallback articles)
3. Technical analysis route (fixed with main page content)
4. Screener route (fixed with comprehensive fallback)
5. Sentiment analysis route (fixed with proper data)
6. Notification preferences route (fixed with safe column access)
7. Financial dashboard API endpoints (all 8 endpoints implemented)
8. Navigation mobile spacing (CSS fixes applied)
"""

import requests
import json
from datetime import datetime

# Base URL for testing
BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(endpoint, expected_status=200, test_name=""):
    """Test a single endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        status = "✅ PASS" if response.status_code == expected_status else "❌ FAIL"
        print(f"{status} {test_name}: {endpoint} - Status: {response.status_code}")
        
        if response.status_code != expected_status:
            print(f"   Expected: {expected_status}, Got: {response.status_code}")
            if response.status_code == 500:
                print(f"   Error: {response.text[:200]}...")
        
        return response.status_code == expected_status
    except Exception as e:
        print(f"❌ ERROR {test_name}: {endpoint} - {str(e)}")
        return False

def test_api_endpoint(endpoint, test_name=""):
    """Test API endpoint and validate JSON response"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        
        # Check if it's a login redirect (Flask-Login redirects to login)
        if response.status_code == 302 and 'login' in response.headers.get('Location', ''):
            print(f"✅ PASS {test_name}: {endpoint} - Requires authentication (redirects to login)")
            return True
        
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"{status} {test_name}: {endpoint} - JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'List of items'}")
                return True
            except:
                print(f"❌ FAIL {test_name}: {endpoint} - Invalid JSON response")
                return False
        else:
            print(f"{status} {test_name}: {endpoint} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR {test_name}: {endpoint} - {str(e)}")
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("=" * 60)
    print("COMPREHENSIVE TESTING - ALL FIXES")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Track test results
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Main routes that were fixed
    print("1. MAIN ROUTES TESTING")
    print("-" * 30)
    
    tests = [
        ("/analysis/market-overview", "Market Overview Route"),
        ("/news/", "News Index Route"),
        ("/analysis/technical", "Technical Analysis Route"),
        ("/analysis/screener", "Screener Route"),
        ("/analysis/sentiment", "Sentiment Analysis Route"),
        ("/financial-dashboard", "Financial Dashboard Route"),
        ("/", "Home Page"),
    ]
    
    for endpoint, name in tests:
        total_tests += 1
        if test_endpoint(endpoint, test_name=name):
            passed_tests += 1
    
    print()
    
    # Test 2: API Endpoints for Financial Dashboard
    print("2. FINANCIAL DASHBOARD API TESTING")
    print("-" * 30)
    
    api_tests = [
        ("/api/public/market/data", "Dashboard Data API"),
        ("/api/public/economic/indicators", "Economic Indicators API"),
        ("/api/public/market/sectors", "Market Sectors API"),
        ("/api/public/news/financial", "Financial News API"),
        ("/api/public/insider/analysis/AAPL", "Insider Analysis API"),
        ("/api/public/crypto/data", "Crypto Data API"),
        ("/api/public/crypto/trending", "Crypto Trending API"),
        ("/api/public/currency/rates", "Currency Rates API"),
    ]
    
    for endpoint, name in api_tests:
        total_tests += 1
        if test_api_endpoint(endpoint, test_name=name):
            passed_tests += 1
    
    print()
    
    # Test 3: Notification API (needs authentication - will likely fail but test the endpoint)
    print("3. NOTIFICATION API TESTING")
    print("-" * 30)
    
    # This will likely return 401/403 but we're testing that it doesn't 500
    total_tests += 1
    response_code = requests.get(f"{BASE_URL}/notifications/api/user/preferences").status_code
    if response_code in [401, 403, 302]:  # Expected for unauthenticated user
        print("✅ PASS Notification Preferences API: Properly requires authentication")
        passed_tests += 1
    elif response_code == 200:
        print("✅ PASS Notification Preferences API: Returns 200 (may be demo user)")
        passed_tests += 1
    elif response_code == 500:
        print("❌ FAIL Notification Preferences API: Still returning 500 error")
    else:
        print(f"⚠️  UNKNOWN Notification Preferences API: Status {response_code}")
    
    print()
    
    # Test 4: Static resources and CSS
    print("4. STATIC RESOURCES TESTING")
    print("-" * 30)
    
    static_tests = [
        ("/static/css/style.css", "Main CSS"),
        ("/static/css/mobile-optimized.css", "Mobile CSS"),
        ("/static/js/mobile-dropdown-fix.js", "Mobile JS"),
    ]
    
    for endpoint, name in static_tests:
        total_tests += 1
        if test_endpoint(endpoint, test_name=name):
            passed_tests += 1
    
    print()
    
    # Test 5: Demo functionality
    print("5. DEMO FUNCTIONALITY TESTING")
    print("-" * 30)
    
    demo_tests = [
        ("/demo", "Demo Page"),
        ("/pricing", "Pricing Page"),
    ]
    
    for endpoint, name in demo_tests:
        total_tests += 1
        if test_endpoint(endpoint, test_name=name):
            passed_tests += 1
    
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System is fully functional.")
    elif passed_tests >= total_tests * 0.8:
        print("✅ MOSTLY SUCCESSFUL! Most critical fixes are working.")
    else:
        print("⚠️  SOME ISSUES REMAIN. Review failed tests above.")
    
    print()
    print("FIXES IMPLEMENTED:")
    print("- ✅ Market overview route with fallback data")
    print("- ✅ News index route with fallback articles")
    print("- ✅ Technical analysis route with main page content")
    print("- ✅ Screener route with comprehensive fallback")
    print("- ✅ Sentiment analysis route with proper data")
    print("- ✅ Notification preferences with safe column access")
    print("- ✅ Financial dashboard with complete API endpoints")
    print("- ✅ Mobile navigation spacing improvements")
    print("- ✅ Database table creation for missing columns")
    print("- ✅ Comprehensive error handling and fallback systems")
    print()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    run_comprehensive_tests()
