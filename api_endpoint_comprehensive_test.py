"""
Comprehensive API endpoint testing
Test all API routes for functionality and error handling
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints systematically"""
    
    base_url = "http://localhost:5000"
    test_results = {
        'total_tested': 0,
        'successful': 0,
        'failed': 0,
        'errors': []
    }
    
    # List of API endpoints to test
    api_endpoints = [
        # Main API routes
        {'url': '/api/trial-status', 'method': 'GET', 'auth_required': False},
        {'url': '/api/dashboard/data', 'method': 'GET', 'auth_required': True},
        {'url': '/api/economic/indicators', 'method': 'GET', 'auth_required': False},
        {'url': '/api/market/sectors', 'method': 'GET', 'auth_required': False},
        {'url': '/api/news/financial', 'method': 'GET', 'auth_required': False},
        {'url': '/api/crypto/data', 'method': 'GET', 'auth_required': False},
        {'url': '/api/crypto/trending', 'method': 'GET', 'auth_required': False},
        {'url': '/api/currency/rates', 'method': 'GET', 'auth_required': False},
        
        # Stock API routes
        {'url': '/api/search?q=AAPL', 'method': 'GET', 'auth_required': False},
        {'url': '/api/stock/AAPL', 'method': 'GET', 'auth_required': False},
        {'url': '/api/stock/AAPL/history', 'method': 'GET', 'auth_required': False},
        
        # News API routes
        {'url': '/api/latest', 'method': 'GET', 'auth_required': False},
        {'url': '/api/market-summary', 'method': 'GET', 'auth_required': False},
        {'url': '/api/market-overview', 'method': 'GET', 'auth_required': False},
        {'url': '/api/trending', 'method': 'GET', 'auth_required': False},
        {'url': '/api/sources', 'method': 'GET', 'auth_required': False},
        
        # Analysis API routes
        {'url': '/api/analysis/indicators', 'method': 'GET', 'auth_required': False},
        {'url': '/api/analysis/signals', 'method': 'GET', 'auth_required': False},
        {'url': '/api/market-summary', 'method': 'GET', 'auth_required': False},
        
        # Notification API routes (require auth)
        {'url': '/api/unread-count', 'method': 'GET', 'auth_required': True},
        {'url': '/api/notifications', 'method': 'GET', 'auth_required': True},
        {'url': '/api/user/preferences', 'method': 'GET', 'auth_required': True},
        
        # Market data API routes
        {'url': '/api/markets/summary', 'method': 'GET', 'auth_required': False},
        {'url': '/api/stocks/popular', 'method': 'GET', 'auth_required': False}
    ]
    
    print(f"🔄 Testing {len(api_endpoints)} API endpoints...")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    for endpoint in api_endpoints:
        test_results['total_tested'] += 1
        url = base_url + endpoint['url']
        
        try:
            # Make request based on method
            if endpoint['method'] == 'GET':
                response = requests.get(url, timeout=10)
            elif endpoint['method'] == 'POST':
                response = requests.post(url, timeout=10)
            else:
                continue
            
            # Check response
            if response.status_code == 200:
                test_results['successful'] += 1
                status = "✅ SUCCESS"
            elif response.status_code == 401 and endpoint['auth_required']:
                test_results['successful'] += 1
                status = "✅ AUTH_REQUIRED (Expected 401)"
            elif response.status_code == 404:
                test_results['failed'] += 1
                status = "❌ NOT_FOUND"
                test_results['errors'].append(f"{endpoint['url']}: 404 Not Found")
            elif response.status_code == 500:
                test_results['failed'] += 1
                status = "❌ SERVER_ERROR"
                test_results['errors'].append(f"{endpoint['url']}: 500 Server Error")
            else:
                test_results['failed'] += 1
                status = f"⚠️ STATUS_{response.status_code}"
                test_results['errors'].append(f"{endpoint['url']}: Status {response.status_code}")
            
            print(f"{status:<30} {endpoint['method']} {endpoint['url']}")
            
        except requests.exceptions.ConnectionError:
            test_results['failed'] += 1
            print(f"❌ CONNECTION_ERROR      {endpoint['method']} {endpoint['url']}")
            test_results['errors'].append(f"{endpoint['url']}: Connection Error (Server not running?)")
            
        except requests.exceptions.Timeout:
            test_results['failed'] += 1
            print(f"❌ TIMEOUT               {endpoint['method']} {endpoint['url']}")
            test_results['errors'].append(f"{endpoint['url']}: Request Timeout")
            
        except Exception as e:
            test_results['failed'] += 1
            print(f"❌ ERROR                 {endpoint['method']} {endpoint['url']} - {str(e)}")
            test_results['errors'].append(f"{endpoint['url']}: {str(e)}")
    
    # Print summary
    print("=" * 60)
    print("📊 API ENDPOINT TEST SUMMARY")
    print("=" * 60)
    print(f"Total tested: {test_results['total_tested']}")
    print(f"Successful:   {test_results['successful']} ✅")
    print(f"Failed:       {test_results['failed']} ❌")
    
    success_rate = (test_results['successful'] / test_results['total_tested']) * 100
    print(f"Success rate: {success_rate:.1f}%")
    
    if test_results['errors']:
        print("\n❌ ERRORS FOUND:")
        for error in test_results['errors']:
            print(f"  • {error}")
    
    return test_results

if __name__ == "__main__":
    print("🚀 Starting comprehensive API endpoint testing...")
    results = test_api_endpoints()
    
    if results['failed'] == 0:
        print("\n🎉 All API endpoints are working correctly!")
    else:
        print(f"\n⚠️ Found {results['failed']} issues that need to be fixed.")
        print("These endpoints should be investigated and fixed as part of the systematic bug fixing process.")
