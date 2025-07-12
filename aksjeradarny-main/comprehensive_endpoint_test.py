#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing for Aksjeradar
Tests all endpoints for availability, correct status codes, and redirect logic
"""

import requests
import sys
import json
import time
from urllib.parse import urljoin
from typing import List, Dict, Tuple
import re

class EndpointTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Aksjeradar-Endpoint-Tester/1.0'
        })
        self.results = []
        
    def test_endpoint(self, endpoint: str, method: str = 'GET', 
                     expected_status: int = 200, 
                     data: dict = None,
                     headers: dict = None,
                     auth_required: bool = False,
                     demo_accessible: bool = True) -> Dict:
        """Test a single endpoint"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            # Prepare request
            req_headers = self.session.headers.copy()
            if headers:
                req_headers.update(headers)
                
            # Make request
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = self.session.get(url, headers=req_headers, timeout=10, allow_redirects=True)
            elif method.upper() == 'POST':
                response = self.session.post(url, data=data, headers=req_headers, timeout=10, allow_redirects=True)
            else:
                response = self.session.request(method, url, data=data, headers=req_headers, timeout=10, allow_redirects=True)
                
            response_time = time.time() - start_time
            
            # Analyze response
            result = {
                'endpoint': endpoint,
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'response_time': round(response_time * 1000, 2),  # in ms
                'success': response.status_code == expected_status,
                'content_type': response.headers.get('Content-Type', ''),
                'content_length': len(response.content) if response.content else 0,
                'redirected': len(response.history) > 0,
                'final_url': response.url,
                'auth_required': auth_required,
                'demo_accessible': demo_accessible
            }
            
            # Check for common issues
            issues = []
            
            # Check for 404s when expecting 200
            if expected_status == 200 and response.status_code == 404:
                issues.append("404 Not Found - endpoint may not exist")
                
            # Check for 500 errors
            if response.status_code >= 500:
                issues.append(f"Server error: {response.status_code}")
                
            # Check for slow responses
            if response_time > 5:  # 5 seconds
                issues.append(f"Slow response: {response_time:.2f}s")
                
            # Check content type for HTML endpoints
            if endpoint.endswith('/') or not '.' in endpoint.split('/')[-1]:
                if 'text/html' not in result['content_type'] and response.status_code == 200:
                    issues.append("Expected HTML content type")
                    
            # Check for empty responses when content expected
            if response.status_code == 200 and result['content_length'] < 100:
                if 'json' not in result['content_type']:
                    issues.append("Suspiciously small response")
                    
            result['issues'] = issues
            result['has_issues'] = len(issues) > 0
            
        except requests.exceptions.Timeout:
            result = {
                'endpoint': endpoint,
                'url': url,
                'method': method,
                'status_code': 'TIMEOUT',
                'expected_status': expected_status,
                'response_time': 10000,  # timeout time
                'success': False,
                'issues': ['Request timeout'],
                'has_issues': True
            }
            
        except requests.exceptions.ConnectionError:
            result = {
                'endpoint': endpoint,
                'url': url,
                'method': method,
                'status_code': 'CONNECTION_ERROR',
                'expected_status': expected_status,
                'response_time': 0,
                'success': False,
                'issues': ['Connection error - server may not be running'],
                'has_issues': True
            }
            
        except Exception as e:
            result = {
                'endpoint': endpoint,
                'url': url,
                'method': method,
                'status_code': 'ERROR',
                'expected_status': expected_status,
                'response_time': 0,
                'success': False,
                'issues': [f'Unexpected error: {str(e)}'],
                'has_issues': True
            }
            
        self.results.append(result)
        return result
        
    def test_auth_endpoint_with_demo_user(self, endpoint: str) -> Dict:
        """Test endpoint with demo user credentials to check demo access"""
        # Test without auth first
        result_no_auth = self.test_endpoint(endpoint, expected_status=302)  # Should redirect to login
        
        # Test with demo user (if we can simulate it)
        demo_headers = {
            'X-Demo-User': 'true',  # If the app supports this header
        }
        result_demo = self.test_endpoint(endpoint, headers=demo_headers, expected_status=200)
        
        return {
            'no_auth': result_no_auth,
            'demo_access': result_demo
        }
        
    def run_comprehensive_test(self) -> List[Dict]:
        """Run comprehensive tests on all known endpoints"""
        
        print("🔍 Starting comprehensive endpoint testing...")
        print(f"🌐 Base URL: {self.base_url}")
        print()
        
        # Define all endpoints to test
        endpoints = [
            # Main pages
            {'endpoint': '/', 'desc': 'Home page'},
            {'endpoint': '/stocks', 'desc': 'Stocks overview'},
            {'endpoint': '/stocks/', 'desc': 'Stocks overview (trailing slash)'},
            {'endpoint': '/analysis', 'desc': 'Analysis page', 'auth_required': True},
            {'endpoint': '/portfolio', 'desc': 'Portfolio page', 'auth_required': True},
            {'endpoint': '/portfolio/', 'desc': 'Portfolio page (trailing slash)', 'auth_required': True},
            {'endpoint': '/portfolio/advanced', 'desc': 'Advanced portfolio', 'auth_required': True},
            
            # Authentication
            {'endpoint': '/login', 'desc': 'Login page'},
            {'endpoint': '/register', 'desc': 'Registration page'},
            {'endpoint': '/logout', 'desc': 'Logout', 'method': 'POST', 'expected_status': 302},
            
            # Pricing and features
            {'endpoint': '/pricing', 'desc': 'Pricing page'},
            {'endpoint': '/pricing/', 'desc': 'Pricing page (trailing slash)'},
            {'endpoint': '/demo', 'desc': 'Demo page'},
            {'endpoint': '/features', 'desc': 'Features overview'},
            {'endpoint': '/features/', 'desc': 'Features overview (trailing slash)'},
            {'endpoint': '/features/analyst-recommendations', 'desc': 'Analyst recommendations feature'},
            {'endpoint': '/features/social-sentiment', 'desc': 'Social sentiment feature'},
            {'endpoint': '/features/ai-predictions', 'desc': 'AI predictions feature'},
            
            # Stock details (test with known Norwegian stock)
            {'endpoint': '/stocks/details/EQNR.OL', 'desc': 'Equinor stock details'},
            {'endpoint': '/stocks/details/DNB.OL', 'desc': 'DNB stock details'},
            {'endpoint': '/stocks/details/TEL.OL', 'desc': 'Telenor stock details'},
            
            # API endpoints
            {'endpoint': '/api/stocks/search', 'desc': 'Stock search API'},
            {'endpoint': '/api/stocks/search?q=EQNR', 'desc': 'Stock search API with query'},
            {'endpoint': '/api/market-data', 'desc': 'Market data API'},
            {'endpoint': '/api/market-data/', 'desc': 'Market data API (trailing slash)'},
            {'endpoint': '/api/market-data/realtime', 'desc': 'Realtime market data API'},
            {'endpoint': '/api/stocks/EQNR.OL', 'desc': 'Single stock API'},
            {'endpoint': '/api/stocks/EQNR.OL/history', 'desc': 'Stock history API'},
            
            # Market intelligence
            {'endpoint': '/market-intel', 'desc': 'Market intelligence'},
            {'endpoint': '/market-intel/', 'desc': 'Market intelligence (trailing slash)'},
            {'endpoint': '/market-intel/sectors', 'desc': 'Sector analysis'},
            {'endpoint': '/market-intel/trends', 'desc': 'Market trends'},
            
            # User profile and settings
            {'endpoint': '/profile', 'desc': 'User profile', 'auth_required': True},
            {'endpoint': '/settings', 'desc': 'User settings', 'auth_required': True},
            {'endpoint': '/notifications', 'desc': 'Notifications', 'auth_required': True},
            
            # Legal and info pages
            {'endpoint': '/privacy', 'desc': 'Privacy policy'},
            {'endpoint': '/terms', 'desc': 'Terms of service'},
            {'endpoint': '/about', 'desc': 'About page'},
            {'endpoint': '/contact', 'desc': 'Contact page'},
            {'endpoint': '/help', 'desc': 'Help page'},
            
            # SEO/Blog (if exists)
            {'endpoint': '/blog', 'desc': 'Blog'},
            {'endpoint': '/news', 'desc': 'News'},
            
            # PWA and offline
            {'endpoint': '/offline', 'desc': 'Offline page'},
            {'endpoint': '/manifest.json', 'desc': 'PWA manifest'},
            {'endpoint': '/service-worker.js', 'desc': 'Service worker'},
            
            # Static assets (test a few)
            {'endpoint': '/static/css/style.css', 'desc': 'Main CSS file'},
            {'endpoint': '/static/js/main.js', 'desc': 'Main JS file'},
            {'endpoint': '/static/favicon.ico', 'desc': 'Favicon'},
            {'endpoint': '/static/images/logo.png', 'desc': 'Logo image'},
            
            # Admin (should be protected)
            {'endpoint': '/admin', 'desc': 'Admin panel', 'expected_status': 302},
            {'endpoint': '/admin/', 'desc': 'Admin panel (trailing slash)', 'expected_status': 302},
        ]
        
        # Test each endpoint
        total_tests = len(endpoints)
        passed_tests = 0
        failed_tests = 0
        
        for i, test_config in enumerate(endpoints, 1):
            endpoint = test_config['endpoint']
            desc = test_config.get('desc', endpoint)
            method = test_config.get('method', 'GET')
            expected_status = test_config.get('expected_status', 200)
            auth_required = test_config.get('auth_required', False)
            
            print(f"📋 [{i:3d}/{total_tests}] Testing {desc}")
            print(f"    🔗 {method} {endpoint}")
            
            result = self.test_endpoint(
                endpoint=endpoint,
                method=method,
                expected_status=expected_status,
                auth_required=auth_required
            )
            
            # Print result
            if result['success'] and not result.get('has_issues', False):
                print(f"    ✅ Success ({result['status_code']}) - {result['response_time']}ms")
                passed_tests += 1
            else:
                print(f"    ❌ Failed ({result.get('status_code', 'ERROR')})")
                if result.get('issues'):
                    for issue in result['issues']:
                        print(f"       🔸 {issue}")
                failed_tests += 1
                
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
            
        print()
        print("📊 Test Summary:")
        print(f"    ✅ Passed: {passed_tests}")
        print(f"    ❌ Failed: {failed_tests}")
        print(f"    📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        return self.results
        
    def generate_report(self, filename: str = "endpoint_test_report.json"):
        """Generate detailed report"""
        report = {
            'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'total_tests': len(self.results),
            'passed_tests': len([r for r in self.results if r['success'] and not r.get('has_issues', False)]),
            'failed_tests': len([r for r in self.results if not r['success'] or r.get('has_issues', False)]),
            'results': self.results,
            'issues_summary': self._get_issues_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Detailed report saved to: {filename}")
        return report
        
    def _get_issues_summary(self) -> Dict:
        """Get summary of all issues found"""
        issues_count = {}
        for result in self.results:
            if result.get('has_issues'):
                for issue in result.get('issues', []):
                    issues_count[issue] = issues_count.get(issue, 0) + 1
                    
        return issues_count
        
    def print_failed_endpoints(self):
        """Print detailed info about failed endpoints"""
        failed = [r for r in self.results if not r['success'] or r.get('has_issues', False)]
        
        if not failed:
            print("🎉 All endpoints passed!")
            return
            
        print("\n🚨 Failed Endpoints Details:")
        print("=" * 50)
        
        for result in failed:
            print(f"\n❌ {result['endpoint']}")
            print(f"   Status: {result.get('status_code', 'Unknown')}")
            print(f"   Expected: {result['expected_status']}")
            print(f"   URL: {result.get('url', 'Unknown')}")
            
            if result.get('issues'):
                print("   Issues:")
                for issue in result['issues']:
                    print(f"     • {issue}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive endpoint testing for Aksjeradar')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL to test (default: http://localhost:5000)')
    parser.add_argument('--output', default='endpoint_test_report.json',
                       help='Output file for detailed report')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Create tester and run tests
    tester = EndpointTester(args.url)
    
    try:
        results = tester.run_comprehensive_test()
        
        # Generate report
        tester.generate_report(args.output)
        
        # Print failed endpoints
        tester.print_failed_endpoints()
        
        # Exit with error code if any tests failed
        failed_count = len([r for r in results if not r['success'] or r.get('has_issues', False)])
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} endpoints have issues. Check the report for details.")
            sys.exit(1)
        else:
            print("\n🎉 All endpoints are working correctly!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
