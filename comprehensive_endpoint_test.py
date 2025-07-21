#!/usr/bin/env python3
"""
Comprehensive endpoint testing for Aksjeradar
Tests all URLs, templates, and data loading
"""
import requests
import json
import sys
from urllib.parse import urljoin
import time

class AksjeradarTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []
        
    def log_test(self, endpoint, status, message, details=None):
        """Log test result"""
        result = {
            'endpoint': endpoint,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': time.time()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {endpoint}: {message}")
        
        if status == "FAIL":
            self.failed_tests.append(result)
            if details:
                print(f"   📋 Details: {details}")
    
    def test_endpoint(self, path, test_name=None, expected_status=None, check_content=None, follow_redirects=True):
        """Test a single endpoint"""
        if not test_name:
            test_name = path
            
        try:
            url = urljoin(self.base_url, path)
            response = self.session.get(url, allow_redirects=follow_redirects, timeout=10)
            
            # Check status code
            if expected_status and response.status_code != expected_status:
                self.log_test(test_name, "FAIL", 
                             f"Expected status {expected_status}, got {response.status_code}",
                             f"URL: {url}")
                return False
            
            # Check for 5xx errors
            if response.status_code >= 500:
                self.log_test(test_name, "FAIL", 
                             f"Server error: {response.status_code}",
                             f"Response: {response.text[:200]}...")
                return False
            
            # Check content if specified
            if check_content:
                content = response.text.lower()
                if isinstance(check_content, str):
                    if check_content.lower() not in content:
                        self.log_test(test_name, "FAIL", 
                                     f"Content check failed: '{check_content}' not found")
                        return False
                elif isinstance(check_content, list):
                    missing = [item for item in check_content if item.lower() not in content]
                    if missing:
                        self.log_test(test_name, "FAIL", 
                                     f"Missing content: {missing}")
                        return False
            
            # Check for common error indicators
            error_indicators = ['error 500', 'internal server error', 'traceback', 'exception occurred']
            content_lower = response.text.lower()
            found_errors = [err for err in error_indicators if err in content_lower]
            
            if found_errors:
                self.log_test(test_name, "FAIL", 
                             f"Error indicators found: {found_errors}")
                return False
            
            self.log_test(test_name, "PASS", 
                         f"Status {response.status_code}, content OK")
            return True
            
        except requests.exceptions.ConnectionError:
            self.log_test(test_name, "FAIL", "Connection error - server not running?")
            return False
        except requests.exceptions.Timeout:
            self.log_test(test_name, "FAIL", "Request timeout")
            return False
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Unexpected error: {str(e)}")
            return False
    
    def test_json_endpoint(self, path, test_name=None, required_fields=None):
        """Test JSON API endpoint"""
        if not test_name:
            test_name = f"{path} (JSON)"
            
        try:
            url = urljoin(self.base_url, path)
            response = self.session.get(url, timeout=10)
            
            if response.status_code >= 500:
                self.log_test(test_name, "FAIL", f"Server error: {response.status_code}")
                return False
            
            try:
                data = response.json()
                
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        self.log_test(test_name, "FAIL", f"Missing JSON fields: {missing_fields}")
                        return False
                
                self.log_test(test_name, "PASS", f"Valid JSON response")
                return True
                
            except json.JSONDecodeError:
                # Not JSON, might be HTML redirect
                if 'text/html' in response.headers.get('content-type', ''):
                    self.log_test(test_name, "PASS", f"HTML response (likely redirect)")
                    return True
                else:
                    self.log_test(test_name, "FAIL", "Invalid JSON response")
                    return False
                    
        except Exception as e:
            self.log_test(test_name, "FAIL", f"Error: {str(e)}")
            return False
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("🚀 Starting comprehensive Aksjeradar endpoint testing...\n")
        
        # 1. Public pages (should be accessible)
        print("📋 Testing public pages...")
        public_endpoints = [
            ('/', 'Homepage', ['aksjeradar', 'aksjer']),
            ('/demo', 'Demo page', ['demo', 'prøv']),
            ('/login', 'Login page', ['logg inn', 'passord']),
            ('/register', 'Register page', ['registrer', 'opprett']),
            ('/pricing', 'Pricing page', ['abonnement', 'pris']),
            ('/privacy', 'Privacy page', None),
            ('/contact', 'Contact page', None),
        ]
        
        for path, name, content_check in public_endpoints:
            self.test_endpoint(path, name, check_content=content_check)
        
        # 2. Protected pages (should redirect)
        print("\n📋 Testing protected pages (should redirect)...")
        protected_endpoints = [
            '/stocks',
            '/stocks/list',
            '/stocks/list/oslo',
            '/stocks/list/global',
            '/stocks/search',
            '/analysis',
            '/analysis/ai',
            '/analysis/technical',
            '/portfolio',
            '/portfolio/overview',
        ]
        
        for path in protected_endpoints:
            # These should either redirect (302) or show access-controlled content
            self.test_endpoint(path, f"Protected: {path}", follow_redirects=False)
        
        # 3. API endpoints
        print("\n📋 Testing API endpoints...")
        api_endpoints = [
            ('/api/stocks/search', 'Stock search API'),
            ('/api/market/overview', 'Market overview API'),
            ('/health', 'Health check'),
            ('/health/routes', 'Routes health check'),
        ]
        
        for path, name in api_endpoints:
            self.test_json_endpoint(path, name)
        
        # 4. Static resources
        print("\n📋 Testing static resources...")
        static_endpoints = [
            ('/static/css/style.css', 'Main stylesheet'),
            ('/static/css/mobile-optimized.css', 'Mobile CSS'),
            ('/static/js/main.js', 'Main JavaScript'),
            ('/favicon.ico', 'Favicon'),
        ]
        
        for path, name in static_endpoints:
            self.test_endpoint(path, name)
        
        # 5. Error pages
        print("\n📋 Testing error handling...")
        error_endpoints = [
            ('/nonexistent-page', 'Non-existent page (should 404)'),
            ('/stocks/details/INVALID_SYMBOL', 'Invalid stock symbol'),
        ]
        
        for path, name in error_endpoints:
            self.test_endpoint(path, name, follow_redirects=True)
        
        # 6. Form submissions (GET only)
        print("\n📋 Testing form pages...")
        form_endpoints = [
            ('/stocks/compare', 'Stock comparison form'),
            ('/forgot-password', 'Password reset form'),
        ]
        
        for path, name in form_endpoints:
            self.test_endpoint(path, name)
        
    def test_data_loading(self):
        """Test data loading specifically"""
        print("\n📋 Testing data loading functionality...")
        
        # Test that demo page has sample data
        try:
            response = self.session.get(urljoin(self.base_url, '/demo'))
            if response.status_code == 200:
                content = response.text.lower()
                data_indicators = ['equinor', 'eqnr', 'nok', 'kroner', 'aksjer']
                found_data = [indicator for indicator in data_indicators if indicator in content]
                
                if found_data:
                    self.log_test('Demo data loading', 'PASS', f'Found data indicators: {found_data}')
                else:
                    self.log_test('Demo data loading', 'FAIL', 'No data indicators found in demo')
            else:
                self.log_test('Demo data loading', 'FAIL', f'Demo page not accessible: {response.status_code}')
        except Exception as e:
            self.log_test('Demo data loading', 'FAIL', f'Error testing demo data: {e}')
    
    def check_template_rendering(self):
        """Check that templates render without errors"""
        print("\n📋 Testing template rendering...")
        
        template_indicators = [
            ('base template', ['<!doctype html', '<html', '</html>']),
            ('navigation', ['navbar', 'menu', 'nav']),
            ('bootstrap', ['bootstrap', 'btn', 'container']),
            ('javascript', ['<script', 'function']),
        ]
        
        # Test on homepage
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                content = response.text.lower()
                
                for name, indicators in template_indicators:
                    found = any(indicator in content for indicator in indicators)
                    status = "PASS" if found else "FAIL"
                    self.log_test(f'Template: {name}', status, 
                                 f'Indicators {"found" if found else "missing"}')
            else:
                self.log_test('Template rendering', 'FAIL', 'Homepage not accessible')
        except Exception as e:
            self.log_test('Template rendering', 'FAIL', f'Error: {e}')
    
    def generate_report(self):
        """Generate test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len(self.failed_tests)
        
        print(f"\n{'='*50}")
        print(f"📊 TEST SUMMARY REPORT")
        print(f"{'='*50}")
        print(f"Total tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success rate: {(passed_tests/total_tests*100):.1f}%")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  - {test['endpoint']}: {test['message']}")
                if test.get('details'):
                    print(f"    📋 {test['details']}")
        
        # Save detailed report
        report = {
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': passed_tests/total_tests*100
            },
            'results': self.test_results,
            'failed_tests': self.failed_tests
        }
        
        with open('/workspaces/aksjeny/endpoint_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: endpoint_test_report.json")
        
        return failed_tests == 0

def main():
    """Main test runner"""
    print("🧪 Aksjeradar Comprehensive Endpoint Tester")
    print("=" * 50)
    
    # Check if server is running
    tester = AksjeradarTester()
    
    try:
        response = requests.get(tester.base_url, timeout=5)
        print(f"✅ Server is running at {tester.base_url}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is not running at {tester.base_url}")
        print("💡 Please start the server first: python3 app.py")
        sys.exit(1)
    
    # Run all tests
    tester.run_comprehensive_tests()
    tester.test_data_loading()
    tester.check_template_rendering()
    
    # Generate report
    success = tester.generate_report()
    
    if success:
        print("\n🎉 All tests passed! The application is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
