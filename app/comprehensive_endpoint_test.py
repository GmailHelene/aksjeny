#!/usr/bin/env python3
"""
Comprehensive Endpoint and Functionality Tester for Aksjeradar
This script tests all URLs, endpoints, and core functionality including:
- Authentication (login, registration, password reset)
- Subscription and payment flows
- Access control for premium features
- AI analysis functionality
- Portfolio and watchlist operations
- All public and protected pages
"""
import os
import sys
import requests
import json
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
from bs4 import BeautifulSoup
import logging
import argparse
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("endpoint_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Insert the app directory into the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import app-specific modules
try:
    from app import create_app
    from app.extensions import db
    from app.models.user import User
    app_imports_available = True
    logger.info("Successfully imported app modules")
except ImportError as e:
    app_imports_available = False
    logger.warning(f"Could not import app modules: {e}. Will continue in external testing mode.")

class Color:
    """Terminal color codes for pretty output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AksjeradarTester:
    """Main tester class for Aksjeradar"""
    
    def __init__(self, base_url, interactive=False):
        self.base_url = base_url
        self.session = requests.Session()
        self.interactive = interactive
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "skipped": []
        }
        self.test_users = {
            "free": {"email": "test_free@aksjeradar.test", "password": "test123"},
            "premium": {"email": "test_premium@aksjeradar.test", "password": "test123"},
            "admin": {"email": "admin@aksjeradar.test", "password": "admin123"}
        }
        self.csrf_token = None
        self.current_user = None
        
        # Initialize test start time
        self.start_time = datetime.now()
        
        # Test specific data
        self.tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA", "NVDA", "PYPL", "NFLX", "INTC"]
        self.norwegian_tickers = ["DNB", "EQNR", "TEL", "MOWI", "YAR", "AKERBP", "SALM", "NHY", "ORK", "BAKKA"]
    
    def print_header(self, message):
        """Print a formatted header"""
        print(f"\n{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}")
        print(f"{Color.HEADER}{Color.BOLD}{message.center(80)}{Color.ENDC}")
        print(f"{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}\n")
    
    def print_section(self, message):
        """Print a formatted section header"""
        print(f"\n{Color.BLUE}{Color.BOLD}{'-' * 80}{Color.ENDC}")
        print(f"{Color.BLUE}{Color.BOLD}{message}{Color.ENDC}")
        print(f"{Color.BLUE}{Color.BOLD}{'-' * 80}{Color.ENDC}\n")
    
    def print_result(self, test_name, success, message=""):
        """Print test result with appropriate color"""
        if success:
            result = f"{Color.GREEN}✓ PASS{Color.ENDC}"
            self.results["passed"].append(test_name)
        else:
            result = f"{Color.RED}✗ FAIL{Color.ENDC}"
            self.results["failed"].append(test_name)
            
        print(f"{result} - {test_name}")
        if message:
            print(f"     {message}")
    
    def print_warning(self, test_name, message):
        """Print a warning message"""
        print(f"{Color.YELLOW}⚠ WARNING{Color.ENDC} - {test_name}")
        print(f"     {message}")
        self.results["warnings"].append(test_name)
    
    def print_skip(self, test_name, reason):
        """Print a skipped test message"""
        print(f"{Color.CYAN}○ SKIPPED{Color.ENDC} - {test_name}")
        print(f"     {reason}")
        self.results["skipped"].append(test_name)
    
    def extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            return csrf_input.get('value')
        return None
    
    def get_url(self, endpoint):
        """Get full URL from endpoint"""
        return urljoin(self.base_url, endpoint)
    
    def make_request(self, method, endpoint, expected_status=200, **kwargs):
        """Make a request and log the result"""
        url = self.get_url(endpoint)
        try:
            if method.lower() == 'get':
                response = self.session.get(url, **kwargs)
            elif method.lower() == 'post':
                response = self.session.post(url, **kwargs)
            elif method.lower() == 'put':
                response = self.session.put(url, **kwargs)
            elif method.lower() == 'delete':
                response = self.session.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            return response, success
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None, False
    
    def login(self, user_type="free"):
        """Login with a specific user type"""
        self.print_section(f"Logging in as {user_type} user")
        
        # First, get the login page to extract CSRF token
        response, success = self.make_request('get', '/login')
        if not success:
            self.print_result("Get login page", False, "Could not access login page")
            return False
        
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_result("Extract CSRF token", False, "Could not extract CSRF token from login page")
            return False
        
        # Now attempt to login
        user_credentials = self.test_users.get(user_type)
        if not user_credentials:
            self.print_result(f"Login as {user_type}", False, f"No test credentials defined for {user_type} user")
            return False
        
        login_data = {
            'email': user_credentials['email'],
            'password': user_credentials['password'],
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/login', data=login_data, allow_redirects=True)
        if not success:
            self.print_result(f"Login as {user_type}", False, "Login request failed")
            return False
        
        # Check if login was successful by looking for typical success patterns
        if "Logged in successfully" in response.text or "dashboard" in response.text.lower():
            self.print_result(f"Login as {user_type}", True)
            self.current_user = user_type
            return True
        else:
            self.print_result(f"Login as {user_type}", False, "Login appeared to fail based on response content")
            return False
    
    def logout(self):
        """Logout the current user"""
        self.print_section("Logging out")
        
        response, success = self.make_request('get', '/logout', allow_redirects=True)
        if not success:
            self.print_result("Logout", False, "Logout request failed")
            return False
        
        # Check if logout was successful
        if "Login" in response.text or "Sign in" in response.text:
            self.print_result("Logout", True)
            self.current_user = None
            return True
        else:
            self.print_result("Logout", False, "Logout appeared to fail based on response content")
            return False
    
    def register_user(self, email=None, password=None):
        """Test user registration"""
        self.print_section("Testing User Registration")
        
        # Generate a unique email if not provided
        if not email:
            timestamp = int(time.time())
            email = f"test_user_{timestamp}@aksjeradar.test"
        
        if not password:
            password = "test123"
        
        # First, get the registration page to extract CSRF token
        response, success = self.make_request('get', '/register')
        if not success:
            self.print_result("Get registration page", False, "Could not access registration page")
            return False
        
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_result("Extract CSRF token", False, "Could not extract CSRF token from registration page")
            return False
        
        # Now attempt to register
        registration_data = {
            'email': email,
            'password': password,
            'password2': password,  # Assuming password confirmation field
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/register', data=registration_data, allow_redirects=True)
        if not success:
            self.print_result("User Registration", False, "Registration request failed")
            return False
        
        # Check if registration was successful
        if "successfully" in response.text.lower() or "verification" in response.text.lower():
            self.print_result("User Registration", True)
            return True
        else:
            self.print_result("User Registration", False, "Registration appeared to fail based on response content")
            return False
    
    def test_password_reset(self):
        """Test password reset functionality"""
        self.print_section("Testing Password Reset")
        
        # First, get the password reset page to extract CSRF token
        response, success = self.make_request('get', '/reset_password')
        if not success:
            self.print_result("Get password reset page", False, "Could not access password reset page")
            return False
        
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_result("Extract CSRF token", False, "Could not extract CSRF token from password reset page")
            return False
        
        # Now attempt to request password reset
        reset_data = {
            'email': self.test_users['free']['email'],
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/reset_password', data=reset_data, allow_redirects=True)
        if not success:
            self.print_result("Password Reset Request", False, "Password reset request failed")
            return False
        
        # Check if password reset request was accepted
        if "email" in response.text.lower() and ("sent" in response.text.lower() or "check" in response.text.lower()):
            self.print_result("Password Reset Request", True)
            return True
        else:
            self.print_result("Password Reset Request", False, "Password reset request appeared to fail based on response content")
            return False
    
    def test_subscription_pages(self):
        """Test subscription and pricing pages"""
        self.print_section("Testing Subscription Pages")
        
        # Test pricing page
        response, success = self.make_request('get', '/pricing')
        if success:
            self.print_result("Pricing Page", True)
            
            # Check for expected content
            if "monthly" in response.text.lower() and "yearly" in response.text.lower():
                self.print_result("Pricing Page Content", True)
            else:
                self.print_result("Pricing Page Content", False, "Expected pricing information not found")
        else:
            self.print_result("Pricing Page", False, "Could not access pricing page")
        
        # Test subscription page
        response, success = self.make_request('get', '/subscription')
        if success:
            self.print_result("Subscription Page", True)
            
            # Check for expected content
            if "subscription" in response.text.lower() and ("payment" in response.text.lower() or "stripe" in response.text.lower()):
                self.print_result("Subscription Page Content", True)
            else:
                self.print_result("Subscription Page Content", False, "Expected subscription information not found")
        else:
            self.print_result("Subscription Page", False, "Could not access subscription page")
        
        return success
    
    def test_ai_analysis(self):
        """Test AI analysis functionality"""
        self.print_section("Testing AI Analysis")
        
        # Test Graham analysis
        response, success = self.make_request('get', '/analysis/graham')
        if success:
            self.print_result("Graham Analysis Page", True)
        else:
            self.print_result("Graham Analysis Page", False, "Could not access Graham analysis page")
        
        # Test Buffett analysis
        response, success = self.make_request('get', '/analysis/buffett')
        if success:
            self.print_result("Buffett Analysis Page", True)
        else:
            self.print_result("Buffett Analysis Page", False, "Could not access Buffett analysis page")
        
        # Test AI API endpoint with a sample ticker
        test_ticker = "AAPL"
        response, success = self.make_request('get', f'/api/analysis/{test_ticker}')
        if success:
            self.print_result(f"AI API Endpoint for {test_ticker}", True)
            
            # Check for valid JSON response
            try:
                data = response.json()
                if "analysis" in data or "data" in data or "result" in data:
                    self.print_result("AI API Response Content", True)
                else:
                    self.print_result("AI API Response Content", False, "Expected analysis data not found in response")
            except json.JSONDecodeError:
                self.print_result("AI API Response Content", False, "Response is not valid JSON")
        else:
            self.print_result(f"AI API Endpoint for {test_ticker}", False, "Could not access AI API endpoint")
        
        return success
    
    def test_portfolio_functionality(self):
        """Test portfolio-related functionality"""
        self.print_section("Testing Portfolio Functionality")
        
        # First ensure we're logged in
        if not self.current_user:
            self.print_warning("Portfolio Test", "Not logged in, attempting to login as free user")
            if not self.login("free"):
                self.print_result("Portfolio Test", False, "Login required for portfolio testing")
                return False
        
        # Test portfolio page
        response, success = self.make_request('get', '/portfolio')
        if success:
            self.print_result("Portfolio Page", True)
        else:
            self.print_result("Portfolio Page", False, "Could not access portfolio page")
            return False
        
        # Extract CSRF token for portfolio operations
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_warning("Portfolio Operations", "Could not extract CSRF token, some tests may fail")
        
        # Test adding a stock to portfolio
        test_stock = {
            'ticker': 'AAPL',
            'quantity': 10,
            'price': 150.00,
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/portfolio/add', data=test_stock, allow_redirects=True)
        if success:
            self.print_result("Add Stock to Portfolio", True)
        else:
            self.print_result("Add Stock to Portfolio", False, "Could not add stock to portfolio")
        
        return True
    
    def test_watchlist_functionality(self):
        """Test watchlist-related functionality"""
        self.print_section("Testing Watchlist Functionality")
        
        # First ensure we're logged in
        if not self.current_user:
            self.print_warning("Watchlist Test", "Not logged in, attempting to login as free user")
            if not self.login("free"):
                self.print_result("Watchlist Test", False, "Login required for watchlist testing")
                return False
        
        # Test watchlist page
        response, success = self.make_request('get', '/watchlist')
        if success:
            self.print_result("Watchlist Page", True)
        else:
            self.print_result("Watchlist Page", False, "Could not access watchlist page")
            return False
        
        # Extract CSRF token for watchlist operations
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_warning("Watchlist Operations", "Could not extract CSRF token, some tests may fail")
        
        # Test adding a stock to watchlist
        test_stock = {
            'ticker': 'MSFT',
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/watchlist/add', data=test_stock, allow_redirects=True)
        if success:
            self.print_result("Add Stock to Watchlist", True)
        else:
            self.print_result("Add Stock to Watchlist", False, "Could not add stock to watchlist")
        
        return True
    
    def test_search_functionality(self):
        """Test search functionality"""
        self.print_section("Testing Search Functionality")
        
        # Test basic search
        test_query = "Apple"
        response, success = self.make_request('get', f'/search?q={test_query}')
        if success:
            self.print_result("Basic Search", True)
            
            # Check for expected content
            if test_query.lower() in response.text.lower() or "AAPL" in response.text:
                self.print_result("Search Results Content", True)
            else:
                self.print_result("Search Results Content", False, "Expected search results not found")
        else:
            self.print_result("Basic Search", False, "Could not access search page")
        
        return success
    
    def test_public_pages(self):
        """Test all public pages"""
        self.print_section("Testing Public Pages")
        
        public_pages = [
            ('Home Page', '/'),
            ('About Page', '/about'),
            ('Contact Page', '/contact'),
            ('FAQ Page', '/faq'),
            ('Terms Page', '/terms'),
            ('Privacy Page', '/privacy'),
            ('Demo Page', '/demo')
        ]
        
        all_success = True
        for page_name, endpoint in public_pages:
            response, success = self.make_request('get', endpoint)
            if success:
                self.print_result(page_name, True)
            else:
                self.print_result(page_name, False, f"Could not access {page_name}")
                all_success = False
        
        return all_success
    
    def test_admin_pages(self):
        """Test admin functionality"""
        self.print_section("Testing Admin Pages")
        
        # First ensure we're logged in as admin
        if self.current_user != "admin":
            self.print_warning("Admin Test", "Not logged in as admin, attempting to login")
            if not self.login("admin"):
                self.print_result("Admin Access", False, "Could not login as admin")
                return False
        
        # Test admin dashboard
        response, success = self.make_request('get', '/admin')
        if success:
            self.print_result("Admin Dashboard", True)
            
            # Check for expected admin content
            if "admin" in response.text.lower() and ("users" in response.text.lower() or "statistics" in response.text.lower()):
                self.print_result("Admin Dashboard Content", True)
            else:
                self.print_result("Admin Dashboard Content", False, "Expected admin content not found")
        else:
            self.print_result("Admin Dashboard", False, "Could not access admin dashboard")
            return False
        
        return True
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        self.print_section("Testing API Endpoints")
        
        api_endpoints = [
            ('Stock Data API', '/api/stock/AAPL'),
            ('Market Data API', '/api/market/summary'),
            ('News API', '/api/news')
        ]
        
        all_success = True
        for endpoint_name, endpoint in api_endpoints:
            response, success = self.make_request('get', endpoint)
            if success:
                self.print_result(endpoint_name, True)
                
                # Check for valid JSON response
                try:
                    data = response.json()
                    self.print_result(f"{endpoint_name} Response", True)
                except json.JSONDecodeError:
                    self.print_result(f"{endpoint_name} Response", False, "Response is not valid JSON")
                    all_success = False
            else:
                self.print_result(endpoint_name, False, f"Could not access {endpoint_name}")
                all_success = False
        
        return all_success
    
    def test_premium_features(self):
        """Test premium features access control"""
        self.print_section("Testing Premium Features Access Control")
        
        premium_features = [
            ('Advanced Analysis', '/analysis/advanced'),
            ('Portfolio Analytics', '/portfolio/analytics'),
            ('Market Intelligence', '/market/intelligence'),
            ('Social Sentiment', '/social/sentiment')
        ]
        
        # First test with free user
        if self.current_user != "free":
            self.print_warning("Premium Features Test", "Not logged in as free user, attempting to login")
            if not self.login("free"):
                self.print_result("Free User Access", False, "Could not login as free user")
                return False
        
        # Test premium features with free user (should be restricted)
        for feature_name, endpoint in premium_features:
            response, success = self.make_request('get', endpoint)
            
            # Check if we got redirected or see a paywall/upgrade message
            premium_restricted = False
            if response:
                if response.history and urlparse(response.url).path != endpoint:
                    premium_restricted = True  # Redirected
                elif "upgrade" in response.text.lower() or "premium" in response.text.lower() or "subscribe" in response.text.lower():
                    premium_restricted = True  # Paywall shown
            
            if premium_restricted:
                self.print_result(f"{feature_name} (Free User)", True, "Correctly restricted for free user")
            else:
                self.print_result(f"{feature_name} (Free User)", False, "Premium feature not properly restricted for free user")
        
        # Now test with premium user
        if not self.login("premium"):
            self.print_result("Premium User Access", False, "Could not login as premium user")
            return False
        
        # Test premium features with premium user (should have access)
        all_success = True
        for feature_name, endpoint in premium_features:
            response, success = self.make_request('get', endpoint)
            
            # Check if we have access to the feature
            if success:
                self.print_result(f"{feature_name} (Premium User)", True)
            else:
                self.print_result(f"{feature_name} (Premium User)", False, "Premium user could not access premium feature")
                all_success = False
        
        return all_success
    
    def find_all_endpoints(self):
        """Find all endpoints in the application by crawling"""
        self.print_section("Finding All Endpoints by Crawling")
        
        visited = set()
        to_visit = ['/']
        endpoints = set()
        
        # Regular expression to find href links
        href_pattern = re.compile(r'href=[\'"](\/[^\'"]*)[\'"]')
        
        # Limit the crawl to a reasonable number
        max_pages = 50
        count = 0
        
        while to_visit and count < max_pages:
            current = to_visit.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            count += 1
            
            logger.info(f"Crawling: {current}")
            response, success = self.make_request('get', current)
            if not success or not response:
                continue
            
            # Add to endpoints
            endpoints.add(current)
            
            # Find all links
            links = href_pattern.findall(response.text)
            for link in links:
                # Normalize the link
                normalized = urlparse(link).path
                if normalized and normalized not in visited and normalized not in to_visit:
                    to_visit.append(normalized)
        
        logger.info(f"Found {len(endpoints)} endpoints through crawling")
        return list(endpoints)
    
    def test_discovered_endpoints(self, endpoints):
        """Test all discovered endpoints"""
        self.print_section(f"Testing {len(endpoints)} Discovered Endpoints")
        
        results = {
            "success": [],
            "redirect": [],
            "client_error": [],
            "server_error": [],
            "other": []
        }
        
        for endpoint in endpoints:
            logger.info(f"Testing: {endpoint}")
            response, _ = self.make_request('get', endpoint, expected_status=None)
            
            if not response:
                results["other"].append((endpoint, "Connection Error"))
                continue
            
            status_code = response.status_code
            if 200 <= status_code < 300:
                results["success"].append((endpoint, status_code))
            elif 300 <= status_code < 400:
                results["redirect"].append((endpoint, status_code))
            elif 400 <= status_code < 500:
                results["client_error"].append((endpoint, status_code))
            elif 500 <= status_code < 600:
                results["server_error"].append((endpoint, status_code))
            else:
                results["other"].append((endpoint, status_code))
        
        # Print summary
        self.print_result("Successful Endpoints", True, f"{len(results['success'])} endpoints returned success (200-299)")
        
        if results["redirect"]:
            self.print_warning("Redirecting Endpoints", f"{len(results['redirect'])} endpoints returned redirects (300-399)")
        
        if results["client_error"]:
            self.print_result("Client Error Endpoints", False, f"{len(results['client_error'])} endpoints returned client errors (400-499)")
            for endpoint, status in results["client_error"]:
                logger.error(f"Client Error {status}: {endpoint}")
        
        if results["server_error"]:
            self.print_result("Server Error Endpoints", False, f"{len(results['server_error'])} endpoints returned server errors (500-599)")
            for endpoint, status in results["server_error"]:
                logger.error(f"Server Error {status}: {endpoint}")
        
        # Write detailed results to a JSON file
        with open('endpoint_test_results.json', 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "results": {
                    "success": [{"endpoint": e, "status": s} for e, s in results["success"]],
                    "redirect": [{"endpoint": e, "status": s} for e, s in results["redirect"]],
                    "client_error": [{"endpoint": e, "status": s} for e, s in results["client_error"]],
                    "server_error": [{"endpoint": e, "status": s} for e, s in results["server_error"]],
                    "other": [{"endpoint": e, "status": s} for e, s in results["other"]]
                }
            }, f, indent=2)
        
        return not results["server_error"]
    
    def test_payment_flow(self):
        """Test the payment flow (as much as possible without actual payments)"""
        self.print_section("Testing Payment Flow")
        
        # Ensure we're logged in
        if not self.current_user:
            self.print_warning("Payment Flow Test", "Not logged in, attempting to login as free user")
            if not self.login("free"):
                self.print_result("Payment Flow", False, "Login required for payment flow testing")
                return False
        
        # Go to subscription page
        response, success = self.make_request('get', '/subscription')
        if not success:
            self.print_result("Subscription Page", False, "Could not access subscription page")
            return False
        
        # Extract CSRF token
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_warning("Payment Flow", "Could not extract CSRF token, some tests may fail")
        
        # Check if Stripe checkout form exists
        if "stripe" in response.text.lower() and ("checkout" in response.text.lower() or "payment" in response.text.lower()):
            self.print_result("Stripe Checkout Form", True)
        else:
            self.print_result("Stripe Checkout Form", False, "Stripe checkout form not found on subscription page")
            return False
        
        # We can't actually complete a payment, but we can check if the form looks right
        self.print_warning("Complete Payment", "Cannot complete actual payment in test, but checkout form is present")
        
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("Aksjeradar Comprehensive Test Suite")
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get all endpoints first
        endpoints = self.find_all_endpoints()
        
        # Basic public pages test
        self.test_public_pages()
        
        # Authentication tests
        self.register_user()
        self.login("free")
        self.test_password_reset()
        self.logout()
        
        # Content and feature tests
        self.test_subscription_pages()
        self.test_ai_analysis()
        
        # Authenticated feature tests
        self.login("free")
        self.test_portfolio_functionality()
        self.test_watchlist_functionality()
        self.test_search_functionality()
        self.logout()
        
        # Premium features test
        self.test_premium_features()
        self.logout()
        
        # Admin tests
        self.test_admin_pages()
        self.logout()
        
        # API tests
        self.test_api_endpoints()
        
        # Payment flow test
        self.login("free")
        self.test_payment_flow()
        self.logout()
        
        # Test all discovered endpoints
        self.test_discovered_endpoints(endpoints)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        self.print_header("Test Report")
        
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print(f"Test completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total duration: {duration}")
        print()
        
        print(f"{Color.GREEN}Tests passed: {len(self.results['passed'])}{Color.ENDC}")
        print(f"{Color.RED}Tests failed: {len(self.results['failed'])}{Color.ENDC}")
        print(f"{Color.YELLOW}Warnings: {len(self.results['warnings'])}{Color.ENDC}")
        print(f"{Color.CYAN}Tests skipped: {len(self.results['skipped'])}{Color.ENDC}")
        
        if self.results["failed"]:
            print("\nFailed tests:")
            for test in self.results["failed"]:
                print(f"  - {test}")
        
        # Write detailed report to a file
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "duration_seconds": duration.total_seconds(),
            "summary": {
                "passed": len(self.results["passed"]),
                "failed": len(self.results["failed"]),
                "warnings": len(self.results["warnings"]),
                "skipped": len(self.results["skipped"])
            },
            "tests": {
                "passed": self.results["passed"],
                "failed": self.results["failed"],
                "warnings": self.results["warnings"],
                "skipped": self.results["skipped"]
            }
        }
        
        with open('endpoint_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDetailed report saved to: endpoint_test_report.json")
        
        # Write a simple text summary
        with open('endpoint_test_output.txt', 'w') as f:
            f.write(f"Aksjeradar Test Report\n")
            f.write(f"=====================\n\n")
            f.write(f"Date: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Base URL: {self.base_url}\n")
            f.write(f"Duration: {duration}\n\n")
            
            f.write(f"Summary:\n")
            f.write(f"- Passed: {len(self.results['passed'])}\n")
            f.write(f"- Failed: {len(self.results['failed'])}\n")
            f.write(f"- Warnings: {len(self.results['warnings'])}\n")
            f.write(f"- Skipped: {len(self.results['skipped'])}\n\n")
            
            if self.results["failed"]:
                f.write("Failed tests:\n")
                for test in self.results["failed"]:
                    f.write(f"  - {test}\n")
        
        print(f"Text summary saved to: endpoint_test_output.txt")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Comprehensive Endpoint and Functionality Tester for Aksjeradar')
    parser.add_argument('--base-url', default='http://localhost:5000', help='Base URL to test against')
    parser.add_argument('--interactive', action='store_true', help='Enable interactive mode')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    tester = AksjeradarTester(args.base_url, args.interactive)
    tester.run_all_tests()
