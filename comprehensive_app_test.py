#!/usr/bin/env python3
"""
Comprehensive Aksjeradar Application Test Suite
Tests all endpoints, URLs, access control, styling, and functionality
"""

import sys
import os
import time
import requests
import json
from datetime import datetime
from pathlib import Path

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

class TestColors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{TestColors.BOLD}{TestColors.BLUE}{'='*60}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.WHITE}{text.center(60)}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.BLUE}{'='*60}{TestColors.END}\n")

def print_section(text):
    print(f"\n{TestColors.BOLD}{TestColors.CYAN}{'-'*40}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.YELLOW}{text}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.CYAN}{'-'*40}{TestColors.END}")

def print_result(test_name, success, details=""):
    status = f"{TestColors.GREEN}✓ PASS{TestColors.END}" if success else f"{TestColors.RED}✗ FAIL{TestColors.END}"
    print(f"{status} {test_name}")
    if details:
        print(f"    {TestColors.WHITE}{details}{TestColors.END}")

class AksjeradarTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print_result(test_name, success, details)

    def test_server_availability(self):
        """Test if the server is running and responding"""
        print_section("🌐 Server Availability Test")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_result("Server Health Check", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_result("Server Health Check", False, f"Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_result("Server Health Check", False, f"Connection failed: {str(e)}")
            return False

    def test_public_endpoints(self):
        """Test public endpoints that should be accessible without login"""
        print_section("🌍 Public Endpoints Test")
        
        public_endpoints = [
            ('/', 'Homepage'),
            ('/demo', 'Demo Page'),
            ('/pricing', 'Pricing Page'),
            ('/register', 'Registration Page'),
            ('/login', 'Login Page'),
            ('/about', 'About Page'),
            ('/contact', 'Contact Page'),
            ('/gdpr', 'GDPR Page'),
            ('/forgot-password', 'Forgot Password Page'),
            ('/health', 'Health Check'),
            ('/robots.txt', 'Robots.txt'),
            ('/sitemap.xml', 'Sitemap'),
        ]
        
        for endpoint, name in public_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                success = response.status_code in [200, 302]  # 302 for redirects is OK
                details = f"Status: {response.status_code}"
                
                # Check for specific error patterns (exclude JavaScript error handling)
                if response.status_code == 200:
                    content = response.text.lower()
                    if ('traceback' in content or '500 internal server error' in content or 
                        'error 500' in content or 'application error' in content):
                        success = False
                        details += " - Contains server error content"
                
                self.log_result(f"Public Endpoint: {name}", success, details)
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"Public Endpoint: {name}", False, f"Request failed: {str(e)}")

    def test_demo_functionality(self):
        """Test demo functionality for unauthenticated users"""
        print_section("🎮 Demo Functionality Test")
        
        demo_endpoints = [
            ('/demo', 'Demo Main Page'),
            ('/demo/stocks', 'Demo Stocks'),
            ('/demo/portfolio', 'Demo Portfolio'),
            ('/demo/analysis', 'Demo Analysis'),
            ('/api/demo/stocks', 'Demo API Stocks'),
            ('/api/demo/market-data', 'Demo API Market Data'),
        ]
        
        for endpoint, name in demo_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                
                if response.status_code == 200:
                    # Check for demo-specific content
                    content = response.text.lower()
                    if 'demo' in content or 'test' in content:
                        details += " - Contains demo content"
                    
                self.log_result(f"Demo Endpoint: {name}", success, details)
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"Demo Endpoint: {name}", False, f"Request failed: {str(e)}")

    def test_authenticated_endpoints(self):
        """Test endpoints that require authentication"""
        print_section("🔐 Authenticated Endpoints Test")
        
        # Try to access protected endpoints without authentication
        protected_endpoints = [
            ('/dashboard', 'Dashboard'),
            ('/portfolio', 'Portfolio'),
            ('/watchlist', 'Watchlist'),
            ('/analysis', 'Analysis'),
            ('/notifications', 'Notifications'),
            ('/settings', 'Settings'),
            ('/api/portfolio', 'API Portfolio'),
            ('/api/watchlist', 'API Watchlist'),
            ('/api/user/profile', 'API User Profile'),
        ]
        
        for endpoint, name in protected_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                # Should redirect to login (302) or return 401/403
                success = response.status_code in [302, 401, 403]
                details = f"Status: {response.status_code} (expects redirect or auth error)"
                
                if response.status_code == 302:
                    location = response.headers.get('Location', '')
                    if 'login' in location.lower():
                        details += " - Correctly redirects to login"
                    else:
                        details += f" - Redirects to: {location}"
                
                self.log_result(f"Protected Endpoint: {name}", success, details)
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"Protected Endpoint: {name}", False, f"Request failed: {str(e)}")

    def test_api_endpoints(self):
        """Test API endpoints and their responses"""
        print_section("🔗 API Endpoints Test")
        
        api_endpoints = [
            ('/api/health', 'API Health'),
            ('/api/status', 'API Status'),
            ('/api/demo/stocks', 'Demo API Stocks'),
            ('/api/demo/market-summary', 'Demo API Market Summary'),
        ]
        
        for endpoint, name in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                
                if response.status_code == 200:
                    try:
                        # Try to parse JSON response
                        data = response.json()
                        details += f" - Valid JSON response with {len(data)} items" if isinstance(data, (list, dict)) else " - Valid JSON response"
                    except:
                        details += " - Non-JSON response"
                
                self.log_result(f"API Endpoint: {name}", success, details)
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"API Endpoint: {name}", False, f"Request failed: {str(e)}")

    def test_static_files(self):
        """Test static file serving"""
        print_section("📁 Static Files Test")
        
        static_files = [
            ('/static/css/style.css', 'Main CSS'),
            ('/static/js/main.js', 'Main JavaScript'),
            ('/static/js/demo.js', 'Demo JavaScript'),
            ('/static/js/portfolio.js', 'Portfolio JavaScript'),
            ('/static/images/logo.png', 'Logo Image'),
        ]
        
        for endpoint, name in static_files:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    details += f" - Content-Type: {content_type}"
                
                self.log_result(f"Static File: {name}", success, details)
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"Static File: {name}", False, f"Request failed: {str(e)}")

    def test_error_pages(self):
        """Test error page handling"""
        print_section("❌ Error Pages Test")
        
        # Test 404 page
        try:
            response = self.session.get(f"{self.base_url}/nonexistent-page", timeout=10)
            success = response.status_code == 404
            details = f"Status: {response.status_code}"
            
            if response.status_code == 404:
                content = response.text.lower()
                if 'not found' in content or '404' in content:
                    details += " - Contains 404 error message"
            
            self.log_result("404 Error Page", success, details)
            
        except requests.exceptions.RequestException as e:
            self.log_result("404 Error Page", False, f"Request failed: {str(e)}")

    def test_security_headers(self):
        """Test security headers"""
        print_section("🔒 Security Headers Test")
        
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            headers = response.headers
            
            security_checks = [
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', ['DENY', 'SAMEORIGIN']),
                ('X-XSS-Protection', '1; mode=block'),
                ('Strict-Transport-Security', None),  # Just check if present
            ]
            
            for header, expected in security_checks:
                if header in headers:
                    if expected is None:
                        self.log_result(f"Security Header: {header}", True, f"Present: {headers[header]}")
                    elif isinstance(expected, list):
                        success = headers[header] in expected
                        self.log_result(f"Security Header: {header}", success, f"Value: {headers[header]}")
                    else:
                        success = headers[header] == expected
                        self.log_result(f"Security Header: {header}", success, f"Value: {headers[header]}")
                else:
                    self.log_result(f"Security Header: {header}", False, "Missing")
                    
        except requests.exceptions.RequestException as e:
            self.log_result("Security Headers Test", False, f"Request failed: {str(e)}")

    def test_subscription_flow(self):
        """Test subscription and payment flow"""
        print_section("💳 Subscription Flow Test")
        
        subscription_endpoints = [
            ('/subscription', 'Subscription Page'),
            ('/pricing', 'Pricing Page'),
            ('/stripe/create-checkout-session', 'Stripe Checkout Creation'),
            ('/stripe/success', 'Payment Success Page'),
            ('/stripe/cancel', 'Payment Cancel Page'),
        ]
        
        for endpoint, name in subscription_endpoints:
            try:
                if 'create-checkout-session' in endpoint:
                    # POST request for checkout session
                    response = self.session.post(f"{self.base_url}{endpoint}", 
                                               data={'price_id': 'test'}, timeout=10)
                else:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                success = response.status_code in [200, 302, 401, 403]  # Various valid responses
                details = f"Status: {response.status_code}"
                
                self.log_result(f"Subscription: {name}", success, details)
                
            except requests.exceptions.RequestException as e:
                self.log_result(f"Subscription: {name}", False, f"Request failed: {str(e)}")

    def check_styling_issues(self):
        """Check for common styling issues"""
        print_section("🎨 Styling Issues Check")
        
        try:
            # Check main page for styling issues
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Common styling issues
                styling_checks = [
                    ('white text on white background', 'color: white' in content and 'background: white' in content),
                    ('missing CSS', 'style.css' not in content),
                    ('broken images', 'img' in content and 'alt=""' in content),
                    ('inline styles', 'style=' in content),
                ]
                
                for issue, condition in styling_checks:
                    self.log_result(f"Styling Check: {issue}", not condition, 
                                  "Issue detected" if condition else "No issues found")
            
            # Check CSS file
            css_response = self.session.get(f"{self.base_url}/static/css/style.css", timeout=10)
            if css_response.status_code == 200:
                self.log_result("CSS File Loading", True, "CSS file loads successfully")
            else:
                self.log_result("CSS File Loading", False, f"CSS file status: {css_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("Styling Check", False, f"Request failed: {str(e)}")

    def run_all_tests(self):
        """Run all test suites"""
        print_header("🧪 AKSJERADAR COMPREHENSIVE TEST SUITE")
        
        start_time = time.time()
        
        # Run all test suites
        if self.test_server_availability():
            self.test_public_endpoints()
            self.test_demo_functionality()
            self.test_authenticated_endpoints()
            self.test_api_endpoints()
            self.test_static_files()
            self.test_error_pages()
            self.test_security_headers()
            self.test_subscription_flow()
            self.check_styling_issues()
        else:
            print(f"\n{TestColors.RED}❌ Server is not available. Cannot run further tests.{TestColors.END}")
            return False
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = sum(1 for result in self.test_results if not result['success'])
        total = len(self.test_results)
        
        print_header("📊 TEST SUMMARY")
        print(f"{TestColors.BOLD}Total Tests: {total}{TestColors.END}")
        print(f"{TestColors.GREEN}Passed: {passed}{TestColors.END}")
        print(f"{TestColors.RED}Failed: {failed}{TestColors.END}")
        print(f"{TestColors.BLUE}Duration: {duration:.2f} seconds{TestColors.END}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"{TestColors.BOLD}Success Rate: {success_rate:.1f}%{TestColors.END}")
        
        # Save detailed results
        self.save_results()
        
        return failed == 0

    def save_results(self):
        """Save test results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(self.test_results),
                    'passed': sum(1 for r in self.test_results if r['success']),
                    'failed': sum(1 for r in self.test_results if not r['success']),
                    'results': self.test_results
                }, f, indent=2)
            
            print(f"\n{TestColors.CYAN}📁 Detailed results saved to: {filename}{TestColors.END}")
            
        except Exception as e:
            print(f"\n{TestColors.YELLOW}⚠️  Could not save results: {str(e)}{TestColors.END}")


def main():
    """Main test runner"""
    print(f"{TestColors.BOLD}{TestColors.PURPLE}")
    print("🔍 AKSJERADAR APPLICATION TESTER")
    print("Testing all endpoints, access control, and functionality")
    print(f"{TestColors.END}")
    
    # Check if server should be started
    tester = AksjeradarTester()
    
    # Run comprehensive tests
    success = tester.run_all_tests()
    
    if success:
        print(f"\n{TestColors.GREEN}{TestColors.BOLD}🎉 ALL TESTS PASSED! 🎉{TestColors.END}")
        return 0
    else:
        print(f"\n{TestColors.RED}{TestColors.BOLD}❌ SOME TESTS FAILED ❌{TestColors.END}")
        return 1


if __name__ == "__main__":
    exit(main())
