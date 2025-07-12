#!/usr/bin/env python3
"""
Test script to verify all the fixed endpoints are working correctly
"""
import requests
import json

def test_endpoint(method, url, description, expected_status=200, json_data=None):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            if json_data:
                response = requests.post(url, json=json_data, timeout=10)
            else:
                response = requests.post(url, timeout=10)
        
        status_ok = response.status_code == expected_status
        status_symbol = "✅" if status_ok else "❌"
        
        print(f"{status_symbol} {description}: {response.status_code} (expected {expected_status})")
        
        if not status_ok and response.status_code != expected_status:
            print(f"   Response: {response.text[:200]}...")
        elif response.status_code == 200 and 'api' in url:
            # For API endpoints, show the JSON response
            try:
                json_resp = response.json()
                print(f"   Response: {json.dumps(json_resp, ensure_ascii=False)[:100]}...")
            except:
                pass
                
        return status_ok
    except Exception as e:
        print(f"❌ {description}: Error - {str(e)[:100]}...")
        return False

def main():
    print("=== AKSJERADAR ENDPOINT VERIFICATION ===")
    print("Testing all the fixed endpoints...\n")
    
    base_url = "http://localhost:5001"
    
    # Test cases: (method, endpoint, description, expected_status, json_data)
    test_cases = [
        # Fixed endpoints
        ('GET', f'{base_url}/stocks/search?q=EQNR', 'Stock search page', 200),
        ('GET', f'{base_url}/api/search?q=EQNR', 'Stock search API', 200),
        ('GET', f'{base_url}/portfolio/add/EQNR', 'Quick add to portfolio (should redirect)', 302),
        ('POST', f'{base_url}/api/portfolio/add', 'Portfolio add API (no auth)', 401, {'ticker': 'EQNR'}),
        ('POST', f'{base_url}/api/watchlist/add', 'Watchlist add API (no auth)', 401, {'ticker': 'EQNR'}),
        
        # Additional tests
        ('GET', f'{base_url}/stocks/details/INVALID_TICKER', 'Invalid ticker (should redirect)', 302),
        ('GET', f'{base_url}/portfolio/view/99999', 'Non-existent portfolio (should redirect)', 302),
        ('GET', f'{base_url}/stocks/details/EQNR.OL', 'Valid stock details', 200),
        ('GET', f'{base_url}/', 'Homepage', 200),
        ('GET', f'{base_url}/stocks/', 'Stocks index', 200),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for method, url, desc, expected, *json_data in test_cases:
        json_payload = json_data[0] if json_data else None
        if test_endpoint(method, url, desc, expected, json_payload):
            passed += 1
    
    print(f"\n=== RESULTS ===")
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All endpoints are working correctly!")
    else:
        print(f"⚠️  {total-passed} endpoints still need attention")
    
    return passed == total

if __name__ == '__main__':
    main()
