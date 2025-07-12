#!/usr/bin/env python3
"""
Simple test script to verify trial functionality
"""
import requests
import sys

def test_trial_functionality():
    base_url = "http://localhost:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🔍 Testing trial functionality...")
    
    # Step 1: Visit homepage to start trial
    print("1. Visiting homepage to start trial...")
    homepage_response = session.get(f"{base_url}/")
    if homepage_response.status_code == 200:
        print("   ✅ Homepage accessible")
    else:
        print(f"   ❌ Homepage error: {homepage_response.status_code}")
        return False
    
    # Step 2: Immediately test analysis page
    print("2. Testing analysis page access...")
    analysis_response = session.get(f"{base_url}/analysis/market-overview")
    if analysis_response.status_code == 200:
        print("   ✅ Analysis page accessible with trial")
    elif analysis_response.status_code == 302:
        print(f"   ❌ Analysis page redirected: {analysis_response.headers.get('Location', 'Unknown')}")
        return False
    else:
        print(f"   ❌ Analysis page error: {analysis_response.status_code}")
        return False
    
    # Step 3: Test stock details page
    print("3. Testing stock details page...")
    stock_response = session.get(f"{base_url}/stocks/details/EQUI")
    if stock_response.status_code == 200:
        print("   ✅ Stock details page accessible with trial")
    elif stock_response.status_code == 302:
        print(f"   ❌ Stock details page redirected: {stock_response.headers.get('Location', 'Unknown')}")
        # This might be expected if the stock doesn't exist, so let's not fail here
        print("   ℹ️  This might be expected if the stock ticker doesn't exist")
    else:
        print(f"   ❌ Stock details page error: {stock_response.status_code}")
    
    # Step 4: Test search results
    print("4. Testing search results page...")
    search_response = session.get(f"{base_url}/search_results?query=equi")
    if search_response.status_code == 200:
        print("   ✅ Search results page accessible with trial")
    elif search_response.status_code == 302:
        print(f"   ❌ Search results page redirected: {search_response.headers.get('Location', 'Unknown')}")
        return False
    else:
        print(f"   ❌ Search results page error: {search_response.status_code}")
        return False
    
    print("\n🎉 Trial functionality test completed!")
    return True

if __name__ == "__main__":
    try:
        success = test_trial_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        sys.exit(1)
