#!/usr/bin/env python3
"""
Comprehensive endpoint and functionality testing for Aksjeradar
Tests all endpoints with different user types: demo, premium, admin
"""
import os
import sys
import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import uuid
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("comprehensive_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Color:
    """Terminal color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

class AksjeradarComprehensiveTester:
    """Comprehensive tester for all Aksjeradar functionality"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            "demo_user": {"passed": [], "failed": [], "warnings": []},
            "premium_user": {"passed": [], "failed": [], "warnings": []},
            "admin_user": {"passed": [], "failed": [], "warnings": []},
            "public": {"passed": [], "failed": [], "warnings": []}
        }
        self.csrf_token = None
        self.current_user_type = None
        
        # Test users with unique IDs
        unique_id = uuid.uuid4().hex[:8]
        self.test_users = {
            "demo": {
                "email": f"demo_user_{unique_id}@test.com",
                "password": "DemoTest123!",
                "subscription_type": "free"
            },
            "premium": {
                "email": f"premium_user_{unique_id}@test.com", 
                "password": "PremiumTest123!",
                "subscription_type": "premium"
            },
            "admin": {
                "email": f"admin_user_{unique_id}@test.com",
                "password": "AdminTest123!",
                "subscription_type": "admin"
            }
        }
        
        # All endpoints to test
        self.endpoints = self._get_all_endpoints()
        
    def _get_all_endpoints(self):
        """Get comprehensive list of all endpoints to test"""
        return {
            "public_pages": [
                "/",
                "/demo",
                "/ai-explained", 
                "/pricing",
                "/pricing/",
                "/contact",
                "/privacy",
                "/terms",
                "/about"
            ],
            "auth_pages": [
                "/login",
                "/register",
                "/forgot-password",
                "/reset-password"
            ],
            "protected_pages": [
                "/portfolio",
                "/portfolio/",
                "/analysis",
                "/analysis/",
                "/stocks",
                "/stocks/",
                "/watchlist",
                "/dashboard",
                "/account/settings",
                "/account/subscription"
            ],
            "premium_pages": [
                "/analysis/advanced",
                "/analysis/ai",
                "/analysis/prediction",
                "/portfolio/analytics",
                "/market-intel",
                "/market-intel/",
                "/market-intel/insider-trading",
                "/market-intel/earnings-calendar",
                "/market-intel/sector-analysis",
                "/market-intel/economic-indicators"
            ],
            "admin_pages": [
                "/admin",
                "/admin/users",
                "/admin/analytics",
                "/admin/system"
            ],
            "api_endpoints": [
                "/api/health",
                "/api/version",
                "/api/trial-status",
                "/api/dashboard/data",
                "/api/economic/indicators",
                "/api/market/sectors",
                "/api/news/financial",
                "/api/crypto/data",
                "/api/crypto/trending",
                "/api/currency/rates",
                "/api/stocks/search",
                "/api/stocks/search?q=AAPL",
                "/api/market-data",
                "/api/market-overview",
                "/api/latest",
                "/api/trending"
            ],
            "premium_api": [
                "/api/analysis/advanced",
                "/api/portfolio/analytics",
                "/api/notifications",
                "/api/user/preferences",
                "/api/market-intel/data",
                "/api/ai/predictions"
            ],
            "subscription_endpoints": [
                "/subscription",
                "/subscription/create-checkout-session",
                "/subscription/success",
                "/subscription/cancel",
                "/subscription/webhook"
            ]
        }
    
    def print_header(self, message):
        """Print formatted header"""
        print(f"\n{Color.BLUE}{Color.BOLD}{'='*80}{Color.ENDC}")
        print(f"{Color.BLUE}{Color.BOLD}{message.center(80)}{Color.ENDC}")
        print(f"{Color.BLUE}{Color.BOLD}{'='*80}{Color.ENDC}\n")
    
    def print_section(self, message):
        """Print formatted section"""
        print(f"\n{Color.YELLOW}{'-'*60}{Color.ENDC}")
        print(f"{Color.YELLOW}{message}{Color.ENDC}")
        print(f"{Color.YELLOW}{'-'*60}{Color.ENDC}")
    
    def log_result(self, user_type, test_name, status, details=""):
        """Log test result"""
        result_data = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if status == "PASS":
            self.test_results[user_type]["passed"].append(result_data)
            icon = f"{Color.GREEN}✅{Color.ENDC}"
        elif status == "FAIL":
            self.test_results[user_type]["failed"].append(result_data)
            icon = f"{Color.RED}❌{Color.ENDC}"
        else:
            self.test_results[user_type]["warnings"].append(result_data)
            icon = f"{Color.YELLOW}⚠️{Color.ENDC}"
        
        print(f"{icon} {user_type.upper()}: {test_name} - {details}")
    
    def make_request(self, method, endpoint, expected_status=200, **kwargs):
        """Make HTTP request"""
        url = urljoin(self.base_url, endpoint)
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=10, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, timeout=10, **kwargs)
            else:
                response = self.session.request(method, url, timeout=10, **kwargs)
            
            return response, response.status_code == expected_status
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None, False
    
    def extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                return csrf_input.get('value')
        except Exception as e:
            logger.error(f"Failed to extract CSRF token: {e}")
        return None
    
    def create_test_users(self):
        """Create test users via API if possible"""
        self.print_section("Creating Test Users")
        
        try:
            # Try to import app and create users directly
            from app import create_app
            from app.extensions import db
            from app.models.user import User
            
            app = create_app()
            with app.app_context():
                for user_type, user_data in self.test_users.items():
                    # Check if user already exists
                    existing_user = User.query.filter_by(email=user_data['email']).first()
                    if existing_user:
                        db.session.delete(existing_user)
                        db.session.commit()
                    
                    # Create new user
                    user = User(
                        email=user_data['email'],
                        username=user_data['email'].split('@')[0],
                        is_active=True
                    )
                    user.set_password(user_data['password'])
                    
                    # Set subscription based on type
                    if user_type == "demo":
                        user.subscription_type = "free"
                        user.has_subscription = False
                        user.trial_start = datetime.utcnow()
                    elif user_type == "premium":
                        user.subscription_type = "premium"
                        user.has_subscription = True
                        user.subscription_start_date = datetime.utcnow()
                        user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
                    elif user_type == "admin":
                        user.subscription_type = "premium"
                        user.has_subscription = True
                        user.is_admin = True
                        user.subscription_start_date = datetime.utcnow()
                        user.subscription_end_date = datetime.utcnow() + timedelta(days=365)
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    self.log_result("public", f"Create {user_type} user", "PASS", f"Created: {user_data['email']}")
            
        except Exception as e:
            logger.error(f"Failed to create test users directly: {e}")
            # Fall back to registration via web interface
            self._create_users_via_web()
    
    def _create_users_via_web(self):
        """Create test users via web registration"""
        for user_type, user_data in self.test_users.items():
            try:
                # Get registration page
                response, _ = self.make_request('GET', '/register')
                if not response:
                    continue
                
                csrf_token = self.extract_csrf_token(response.text)
                if not csrf_token:
                    continue
                
                # Register user
                registration_data = {
                    'email': user_data['email'],
                    'password': user_data['password'],
                    'password2': user_data['password'],
                    'csrf_token': csrf_token
                }
                
                response, success = self.make_request('POST', '/register', 
                                                    data=registration_data, 
                                                    allow_redirects=True)
                
                if success or (response and "success" in response.text.lower()):
                    self.log_result("public", f"Register {user_type} user", "PASS", 
                                  f"Registered: {user_data['email']}")
                else:
                    self.log_result("public", f"Register {user_type} user", "FAIL", 
                                  f"Failed to register: {user_data['email']}")
                    
            except Exception as e:
                self.log_result("public", f"Register {user_type} user", "FAIL", str(e))
    
    def login_user(self, user_type):
        """Login as specific user type"""
        if user_type not in self.test_users:
            return False
        
        user_data = self.test_users[user_type]
        
        try:
            # Get login page
            response, _ = self.make_request('GET', '/login')
            if not response:
                return False
            
            csrf_token = self.extract_csrf_token(response.text)
            if not csrf_token:
                return False
            
            # Login
            login_data = {
                'email': user_data['email'],
                'password': user_data['password'],
                'csrf_token': csrf_token
            }
            
            response, success = self.make_request('POST', '/login', 
                                                data=login_data, 
                                                allow_redirects=True)
            
            if success or (response and any(indicator in response.text.lower() 
                                          for indicator in ["dashboard", "welcome", "logged in"])):
                self.current_user_type = user_type
                self.log_result(user_type, "Login", "PASS", f"Logged in as {user_type}")
                return True
            else:
                self.log_result(user_type, "Login", "FAIL", f"Failed to login as {user_type}")
                return False
                
        except Exception as e:
            self.log_result(user_type, "Login", "FAIL", str(e))
            return False
    
    def logout_user(self):
        """Logout current user"""
        try:
            response, success = self.make_request('GET', '/logout', allow_redirects=True)
            if success or (response and "login" in response.url.lower()):
                user_type = self.current_user_type or "unknown"
                self.log_result(user_type, "Logout", "PASS", "Successfully logged out")
                self.current_user_type = None
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def test_public_endpoints(self):
        """Test public endpoints that should work for everyone"""
        self.print_section("Testing Public Endpoints")
        
        for endpoint in self.endpoints["public_pages"]:
            response, success = self.make_request('GET', endpoint)
            
            if success:
                self.log_result("public", f"Public page: {endpoint}", "PASS", "Accessible")
            else:
                status_code = response.status_code if response else "No response"
                self.log_result("public", f"Public page: {endpoint}", "FAIL", f"Status: {status_code}")
        
        # Test auth pages
        for endpoint in self.endpoints["auth_pages"]:
            response, success = self.make_request('GET', endpoint)
            
            if success:
                self.log_result("public", f"Auth page: {endpoint}", "PASS", "Accessible")
            else:
                status_code = response.status_code if response else "No response"
                self.log_result("public", f"Auth page: {endpoint}", "FAIL", f"Status: {status_code}")
    
    def test_api_endpoints(self, user_type="public"):
        """Test API endpoints"""
        self.print_section(f"Testing API Endpoints ({user_type})")
        
        for endpoint in self.endpoints["api_endpoints"]:
            response, success = self.make_request('GET', endpoint)
            
            if success:
                # Try to parse JSON
                try:
                    data = response.json()
                    self.log_result(user_type, f"API: {endpoint}", "PASS", "Valid JSON response")
                except:
                    self.log_result(user_type, f"API: {endpoint}", "WARN", "Non-JSON response")
            else:
                status_code = response.status_code if response else "No response"
                if status_code == 401 and user_type == "public":
                    self.log_result(user_type, f"API: {endpoint}", "PASS", "Correctly requires auth")
                else:
                    self.log_result(user_type, f"API: {endpoint}", "FAIL", f"Status: {status_code}")
    
    def test_protected_endpoints(self, user_type):
        """Test protected endpoints that require login"""
        self.print_section(f"Testing Protected Endpoints ({user_type})")
        
        for endpoint in self.endpoints["protected_pages"]:
            response, success = self.make_request('GET', endpoint)
            
            if success:
                self.log_result(user_type, f"Protected: {endpoint}", "PASS", "Accessible")
            else:
                status_code = response.status_code if response else "No response"
                if status_code in [302, 401] and user_type == "demo":
                    self.log_result(user_type, f"Protected: {endpoint}", "WARN", "May require premium")
                else:
                    self.log_result(user_type, f"Protected: {endpoint}", "FAIL", f"Status: {status_code}")
    
    def test_premium_endpoints(self, user_type):
        """Test premium endpoints"""
        self.print_section(f"Testing Premium Endpoints ({user_type})")
        
        for endpoint in self.endpoints["premium_pages"]:
            response, success = self.make_request('GET', endpoint)
            
            if success:
                self.log_result(user_type, f"Premium: {endpoint}", "PASS", "Accessible")
            else:
                status_code = response.status_code if response else "No response"
                if status_code in [302, 403] and user_type == "demo":
                    self.log_result(user_type, f"Premium: {endpoint}", "PASS", "Correctly restricted")
                else:
                    self.log_result(user_type, f"Premium: {endpoint}", "FAIL", f"Status: {status_code}")
        
        # Test premium API endpoints
        for endpoint in self.endpoints["premium_api"]:
            response, success = self.make_request('GET', endpoint)
            
            if success:
                self.log_result(user_type, f"Premium API: {endpoint}", "PASS", "Accessible")
            else:
                status_code = response.status_code if response else "No response"
                if status_code in [401, 403] and user_type == "demo":
                    self.log_result(user_type, f"Premium API: {endpoint}", "PASS", "Correctly restricted")
                else:
                    self.log_result(user_type, f"Premium API: {endpoint}", "FAIL", f"Status: {status_code}")
    
    def test_admin_endpoints(self, user_type):
        """Test admin endpoints"""
        self.print_section(f"Testing Admin Endpoints ({user_type})")
        
        for endpoint in self.endpoints["admin_pages"]:
            response, success = self.make_request('GET', endpoint)
            
            if success:
                self.log_result(user_type, f"Admin: {endpoint}", "PASS", "Accessible")
            else:
                status_code = response.status_code if response else "No response"
                if status_code in [302, 403] and user_type != "admin":
                    self.log_result(user_type, f"Admin: {endpoint}", "PASS", "Correctly restricted")
                else:
                    self.log_result(user_type, f"Admin: {endpoint}", "FAIL", f"Status: {status_code}")
    
    def test_subscription_flow(self, user_type):
        """Test subscription functionality"""
        self.print_section(f"Testing Subscription Flow ({user_type})")
        
        for endpoint in self.endpoints["subscription_endpoints"]:
            if endpoint == "/subscription/webhook":
                continue  # Skip webhook testing
            
            response, success = self.make_request('GET', endpoint)
            
            if success:
                self.log_result(user_type, f"Subscription: {endpoint}", "PASS", "Accessible")
            else:
                status_code = response.status_code if response else "No response"
                self.log_result(user_type, f"Subscription: {endpoint}", "FAIL", f"Status: {status_code}")
    
    def test_user_workflow(self, user_type):
        """Test complete user workflow"""
        self.print_section(f"Testing Complete User Workflow ({user_type})")
        
        if not self.login_user(user_type):
            self.log_result(user_type, "User workflow", "FAIL", "Could not login")
            return
        
        # Test basic functionality
        self.test_api_endpoints(user_type)
        self.test_protected_endpoints(user_type)
        
        # Test premium functionality
        if user_type in ["premium", "admin"]:
            self.test_premium_endpoints(user_type)
        else:
            self.test_premium_endpoints(user_type)  # Should be restricted
        
        # Test admin functionality
        self.test_admin_endpoints(user_type)
        
        # Test subscription flow
        self.test_subscription_flow(user_type)
        
        # Logout
        self.logout_user()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        self.print_header("COMPREHENSIVE TEST REPORT")
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_warnings = 0
        
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        print()
        
        # Report by user type
        for user_type, results in self.test_results.items():
            passed = len(results["passed"])
            failed = len(results["failed"])
            warnings = len(results["warnings"])
            total = passed + failed + warnings
            
            total_tests += total
            total_passed += passed
            total_failed += failed
            total_warnings += warnings
            
            if total > 0:
                success_rate = (passed / total) * 100
                print(f"\n{Color.BOLD}{user_type.upper()} USER TESTS:{Color.ENDC}")
                print(f"  Total: {total}")
                print(f"  Passed: {Color.GREEN}{passed}{Color.ENDC} ({success_rate:.1f}%)")
                print(f"  Failed: {Color.RED}{failed}{Color.ENDC}")
                print(f"  Warnings: {Color.YELLOW}{warnings}{Color.ENDC}")
                
                if failed > 0:
                    print(f"  {Color.RED}Failed tests:{Color.ENDC}")
                    for test in results["failed"][:5]:  # Show first 5 failures
                        print(f"    - {test['test']}: {test['details']}")
        
        # Overall summary
        print(f"\n{Color.BOLD}OVERALL SUMMARY:{Color.ENDC}")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {Color.GREEN}{total_passed}{Color.ENDC}")
        print(f"Failed: {Color.RED}{total_failed}{Color.ENDC}")
        print(f"Warnings: {Color.YELLOW}{total_warnings}{Color.ENDC}")
        
        if total_tests > 0:
            overall_success_rate = (total_passed / total_tests) * 100
            print(f"Overall success rate: {overall_success_rate:.1f}%")
            
            if overall_success_rate >= 90:
                print(f"\n{Color.GREEN}🎉 EXCELLENT! System is working very well.{Color.ENDC}")
            elif overall_success_rate >= 80:
                print(f"\n{Color.YELLOW}✅ GOOD! System is mostly functional with minor issues.{Color.ENDC}")
            elif overall_success_rate >= 70:
                print(f"\n{Color.YELLOW}⚠️ FAIR! System has some issues that should be addressed.{Color.ENDC}")
            else:
                print(f"\n{Color.RED}❌ POOR! System has significant issues that need immediate attention.{Color.ENDC}")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "test_results": self.test_results,
            "summary": {
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_warnings": total_warnings,
                "success_rate": overall_success_rate if total_tests > 0 else 0
            }
        }
        
        with open('comprehensive_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: comprehensive_test_report.json")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        self.print_header("AKSJERADAR COMPREHENSIVE TEST SUITE")
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test public endpoints first
        self.test_public_endpoints()
        self.test_api_endpoints("public")
        
        # Create test users
        self.create_test_users()
        
        # Test each user type workflow
        for user_type in ["demo", "premium", "admin"]:
            self.test_user_workflow(user_type)
        
        # Generate comprehensive report
        self.generate_comprehensive_report()

def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Aksjeradar Test Suite')
    parser.add_argument('--base-url', default='http://localhost:5000', 
                       help='Base URL to test against')
    args = parser.parse_args()
    
    # Check if server is running
    try:
        response = requests.get(f"{args.base_url}/api/health", timeout=5)
        print(f"✅ Server is running at {args.base_url}")
    except:
        print(f"❌ Server is not running at {args.base_url}")
        print("Please start the server first:")
        print("  cd /workspaces/aksjeny/app && python standalone_test_server.py")
        return False
    
    # Run comprehensive tests
    tester = AksjeradarComprehensiveTester(args.base_url)
    tester.run_all_tests()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
