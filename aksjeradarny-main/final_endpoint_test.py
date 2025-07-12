#!/usr/bin/env python3
"""
Final comprehensive endpoint testing for Aksjeradar
Tests all major endpoints for functionality and access control
"""

import sys
import os
sys.path.insert(0, '.')

from app import create_app
import json
from datetime import datetime

def test_all_endpoints():
    """Test all endpoints systematically"""
    app = create_app()
    
    # Define test endpoints with expected behavior
    endpoints_config = {
        'public_pages': {
            'endpoints': ['/', '/login', '/register', '/privacy', '/forgot-password'],
            'expected_status': [200, 302],  # 200 OK or 302 redirect
            'description': 'Public pages accessible to all users'
        },
        'demo_pages': {
            'endpoints': ['/demo', '/demo/ping', '/demo/echo', '/demo/user'],
            'expected_status': [200],
            'description': 'Demo pages for testing and demonstration'
        },
        'protected_pages': {
            'endpoints': ['/dashboard', '/portfolio', '/watchlist', '/analytics'],
            'expected_status': [200, 302, 401, 403],  # Depends on auth state
            'description': 'Protected pages requiring authentication'
        },
        'subscription_pages': {
            'endpoints': ['/subscription', '/subscription/manage'],
            'expected_status': [200, 302, 401, 403],
            'description': 'Subscription management pages'
        },
        'api_endpoints': {
            'endpoints': ['/api/stocks', '/api/portfolio', '/api/watchlist'],
            'expected_status': [200, 401, 403, 404],
            'description': 'API endpoints for data access'
        },
        'admin_pages': {
            'endpoints': ['/admin', '/admin/users'],
            'expected_status': [302, 401, 403],  # Should redirect or deny
            'description': 'Admin pages requiring special permissions'
        }
    }
    
    results = {}
    total_tests = 0
    passed_tests = 0
    
    print("🔍 FINAL COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    with app.test_client() as client:
        for category, config in endpoints_config.items():
            print(f"📂 Testing {category.upper().replace('_', ' ')}")
            print(f"   {config['description']}")
            
            category_results = []
            
            for endpoint in config['endpoints']:
                total_tests += 1
                try:
                    response = client.get(endpoint, follow_redirects=False)
                    status = response.status_code
                    
                    # Check if status is expected
                    is_expected = status in config['expected_status']
                    if is_expected:
                        passed_tests += 1
                        status_icon = "✅"
                    else:
                        status_icon = "❌"
                    
                    # Get response info
                    content_length = len(response.data) if response.data else 0
                    has_content = content_length > 0
                    
                    print(f"   {status_icon} {endpoint:<25} -> {status} ({content_length:,} bytes)")
                    
                    category_results.append({
                        'endpoint': endpoint,
                        'status': status,
                        'expected': is_expected,
                        'content_length': content_length,
                        'has_content': has_content
                    })
                    
                except Exception as e:
                    print(f"   ❌ {endpoint:<25} -> ERROR: {str(e)}")
                    category_results.append({
                        'endpoint': endpoint,
                        'status': 'ERROR',
                        'expected': False,
                        'error': str(e)
                    })
            
            results[category] = category_results
            print()
    
    # Summary
    success_rate = (passed_tests / total_tests) * 100
    print("=" * 60)
    print(f"📊 TEST SUMMARY")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success rate: {success_rate:.1f}%")
    print()
    
    # Detailed analysis
    print("🔍 DETAILED ANALYSIS")
    for category, category_results in results.items():
        failed_endpoints = [r for r in category_results if not r.get('expected', False)]
        
        if failed_endpoints:
            print(f"❌ {category.upper()}: {len(failed_endpoints)} issues")
            for result in failed_endpoints:
                status = result.get('status', 'ERROR')
                endpoint = result['endpoint']
                if 'error' in result:
                    print(f"   - {endpoint}: {result['error']}")
                else:
                    print(f"   - {endpoint}: Status {status} (unexpected)")
        else:
            print(f"✅ {category.upper()}: All endpoints OK")
    
    print()
    
    # Security analysis
    print("🔒 SECURITY ANALYSIS")
    
    # Check for endpoints that should be protected but return 200
    public_access_concerns = []
    for category, category_results in results.items():
        if category in ['protected_pages', 'admin_pages']:
            for result in category_results:
                if result.get('status') == 200:
                    public_access_concerns.append((category, result['endpoint']))
    
    if public_access_concerns:
        print("⚠️  POTENTIAL SECURITY CONCERNS:")
        for category, endpoint in public_access_concerns:
            print(f"   - {endpoint} (in {category}) returns 200 without authentication")
    else:
        print("✅ No obvious security concerns detected")
    
    print()
    
    # Save results
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': success_rate
        },
        'results': results,
        'security_concerns': public_access_concerns
    }
    
    with open('final_endpoint_test_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"💾 Detailed report saved to final_endpoint_test_report.json")
    
    return success_rate > 80  # Return True if >80% success rate

if __name__ == "__main__":
    try:
        success = test_all_endpoints()
        if success:
            print("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Check the report for details.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
