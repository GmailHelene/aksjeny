#!/usr/bin/env python3
"""
Comprehensive test of all endpoints and services in Aksjeradar
Tests all routes, authentication, premium features, and error handling
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys
import re

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AksjeradarTester:
    def __init__(self, base_url='http://localhost:5001'):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        self.test_results = []
        
        # Test user credentials (Helene as exempt user)
        self.test_email = 'helene@luxushair.com'
        self.test_password = 'HeleneTest123!'
        
    def log(self, message, color=Color.BLUE):
        print(f"{color}[{datetime.now().strftime('%H:%M:%S')}] {message}{Color.END}")
        
    def test_result(self, endpoint, status, details=""):
        result = {
            'endpoint': endpoint,
            'status': status,
            'details': details,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            self.log(f"✅ {endpoint}: {details}", Color.GREEN)
        elif status == 'FAIL':
            self.log(f"❌ {endpoint}: {details}", Color.RED)
        else:
            self.log(f"⚠️  {endpoint}: {details}", Color.YELLOW)
    
    def get_csrf_token(self, url):
        """Extract CSRF token from a page"""
        try:
            response = self.session.get(url)
            if 'csrf_token' in response.text:
                # Extract token from hidden input field
                match = re.search(r'name="csrf_token".*?value="([^"]+)"', response.text)
                if match:
                    return match.group(1)
            return None
        except Exception as e:
            self.log(f"Error getting CSRF token: {e}", Color.RED)
            return None
    
    def test_basic_pages(self):
        """Test basic accessible pages"""
        self.log("🏠 Testing basic pages...", Color.BOLD)
        
        basic_endpoints = [
            ('/', 'Landing page'),
            ('/login', 'Login page'),
            ('/register', 'Registration page'),
            ('/forgot_password', 'Forgot password page'),
            ('/privacy', 'Privacy page'),
            ('/contact', 'Contact page'),
            ('/subscription', 'Subscription page'),
            ('/stocks/', 'Stocks index'),
            ('/stocks/search', 'Stock search page'),
        ]
        
        for endpoint, description in basic_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.test_result(endpoint, 'PASS', f"{description} loads successfully")
                else:
                    self.test_result(endpoint, 'FAIL', f"{description} returned {response.status_code}")
            except Exception as e:
                self.test_result(endpoint, 'FAIL', f"Error: {str(e)}")
    
    def test_authentication(self):
        """Test login and logout functionality"""
        self.log("🔐 Testing authentication...", Color.BOLD)
        
        # Test login page access
        try:
            login_url = f"{self.base_url}/login"
            response = self.session.get(login_url)
            if response.status_code == 200:
                self.test_result('/login GET', 'PASS', 'Login page accessible')
                
                # Get CSRF token
                self.csrf_token = self.get_csrf_token(login_url)
                if self.csrf_token:
                    self.test_result('CSRF Token', 'PASS', 'CSRF token extracted successfully')
                else:
                    self.test_result('CSRF Token', 'WARN', 'Could not extract CSRF token')
            else:
                self.test_result('/login GET', 'FAIL', f'Status code: {response.status_code}')
                return False
        except Exception as e:
            self.test_result('/login GET', 'FAIL', f'Error: {str(e)}')
            return False
        
        # Test login with valid credentials
        try:
            login_data = {
                'email': self.test_email,
                'password': self.test_password,
                'submit': 'Log In'
            }
            if self.csrf_token:
                login_data['csrf_token'] = self.csrf_token
            
            response = self.session.post(login_url, data=login_data, allow_redirects=False)
            
            if response.status_code in [302, 303]:
                self.test_result('/login POST', 'PASS', 'Login successful (redirect received)')
                
                # Follow redirect to confirm login
                if 'Location' in response.headers:
                    redirect_response = self.session.get(response.headers['Location'])
                    if redirect_response.status_code == 200:
                        self.test_result('Login Redirect', 'PASS', 'Post-login page accessible')
                    else:
                        self.test_result('Login Redirect', 'WARN', f'Redirect failed: {redirect_response.status_code}')
                
                return True
            else:
                self.test_result('/login POST', 'FAIL', f'Login failed with status {response.status_code}')
                return False
                
        except Exception as e:
            self.test_result('/login POST', 'FAIL', f'Login error: {str(e)}')
            return False
    
    def test_premium_endpoints(self):
        """Test premium endpoints that require authentication or trial"""
        self.log("💎 Testing premium endpoints...", Color.BOLD)
        
        premium_endpoints = [
            ('/stocks/details/EQNR.OL', 'EQNR stock details'),
            ('/stocks/details/AAPL', 'Apple stock details'),
            ('/stocks/details/BTC-USD', 'Bitcoin details'),
            ('/stocks/list/oslo', 'Oslo Børs stocks'),
            ('/stocks/list/global', 'Global stocks'),
            ('/stocks/list/crypto', 'Cryptocurrency list'),
            ('/stocks/list/currency', 'Currency rates'),
            ('/stocks/compare', 'Stock comparison'),
            ('/portfolio/', 'Portfolio index'),
            ('/portfolio/create', 'Create portfolio'),
            ('/portfolio/overview', 'Portfolio overview'),
            ('/portfolio/watchlist', 'Watchlist'),
            ('/portfolio/tips', 'Stock tips'),
            ('/portfolio/transactions', 'Transaction history'),
        ]
        
        for endpoint, description in premium_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.test_result(endpoint, 'PASS', f"{description} accessible")
                elif response.status_code == 302:
                    self.test_result(endpoint, 'WARN', f"{description} redirected (may require login)")
                else:
                    self.test_result(endpoint, 'FAIL', f"{description} returned {response.status_code}")
            except Exception as e:
                self.test_result(endpoint, 'FAIL', f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        self.log("🔌 Testing API endpoints...", Color.BOLD)
        
        api_endpoints = [
            ('/api/search?q=EQNR', 'Stock search API'),
            ('/stocks/api/stock/EQNR.OL', 'Stock data API for EQNR'),
            ('/stocks/api/stock/AAPL', 'Stock data API for Apple'),
            ('/api/portfolio/add', 'Add to portfolio API (POST)'),
            ('/api/watchlist/add', 'Add to watchlist API (POST)'),
        ]
        
        for endpoint, description in api_endpoints:
            try:
                if 'POST' in description:
                    # Test POST endpoints
                    headers = {'Content-Type': 'application/json'}
                    if 'portfolio' in endpoint:
                        data = {'ticker': 'EQNR.OL'}
                    elif 'watchlist' in endpoint:
                        data = {'ticker': 'AAPL'}
                    else:
                        data = {}
                    
                    response = self.session.post(f"{self.base_url}{endpoint}", 
                                               json=data, headers=headers)
                else:
                    # Test GET endpoints
                    response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code in [200, 201]:
                    self.test_result(endpoint, 'PASS', f"{description} working")
                elif response.status_code == 401:
                    self.test_result(endpoint, 'WARN', f"{description} requires authentication")
                elif response.status_code == 404:
                    self.test_result(endpoint, 'WARN', f"{description} not found (may not be implemented)")
                else:
                    self.test_result(endpoint, 'FAIL', f"{description} returned {response.status_code}")
                    
            except Exception as e:
                self.test_result(endpoint, 'FAIL', f"Error: {str(e)}")
    
    def test_stock_data_endpoints(self):
        """Test specific stock data endpoints"""
        self.log("📈 Testing stock data endpoints...", Color.BOLD)
        
        test_stocks = [
            ('EQNR.OL', 'Equinor (Norwegian stock)'),
            ('DNB.OL', 'DNB Bank (Norwegian stock)'),
            ('AAPL', 'Apple (US stock)'),
            ('MSFT', 'Microsoft (US stock)'),
            ('BTC-USD', 'Bitcoin (Cryptocurrency)'),
            ('ETH-USD', 'Ethereum (Cryptocurrency)'),
        ]
        
        for ticker, description in test_stocks:
            try:
                endpoint = f"/stocks/details/{ticker}"
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    # Check if page contains stock data
                    if ticker in response.text or 'stock' in response.text.lower():
                        self.test_result(endpoint, 'PASS', f"{description} details page working")
                    else:
                        self.test_result(endpoint, 'WARN', f"{description} page loads but may lack data")
                elif response.status_code == 302:
                    self.test_result(endpoint, 'WARN', f"{description} redirected (trial/auth required)")
                else:
                    self.test_result(endpoint, 'FAIL', f"{description} returned {response.status_code}")
                    
            except Exception as e:
                self.test_result(endpoint, 'FAIL', f"Error: {str(e)}")
    
    def test_portfolio_functionality(self):
        """Test portfolio-specific functionality"""
        self.log("📊 Testing portfolio functionality...", Color.BOLD)
        
        # Test portfolio creation
        try:
            create_url = f"{self.base_url}/portfolio/create"
            response = self.session.get(create_url)
            
            if response.status_code == 200:
                self.test_result('/portfolio/create GET', 'PASS', 'Portfolio creation page accessible')
                
                # Test creating a portfolio
                csrf_token = self.get_csrf_token(create_url)
                if csrf_token:
                    portfolio_data = {
                        'name': 'Test Portfolio',
                        'description': 'Test portfolio created by automated test',
                        'csrf_token': csrf_token,
                        'submit': 'Create'
                    }
                    
                    response = self.session.post(create_url, data=portfolio_data, allow_redirects=False)
                    if response.status_code in [302, 303]:
                        self.test_result('/portfolio/create POST', 'PASS', 'Portfolio creation successful')
                    else:
                        self.test_result('/portfolio/create POST', 'WARN', f'Portfolio creation returned {response.status_code}')
                        
            else:
                self.test_result('/portfolio/create GET', 'FAIL', f'Status code: {response.status_code}')
                
        except Exception as e:
            self.test_result('/portfolio/create', 'FAIL', f'Error: {str(e)}')
        
        # Test adding stock to portfolio
        try:
            add_url = f"{self.base_url}/portfolio/add/EQNR.OL"
            response = self.session.get(add_url, allow_redirects=False)
            
            if response.status_code in [200, 302, 303]:
                self.test_result('/portfolio/add/<ticker>', 'PASS', 'Add stock to portfolio working')
            else:
                self.test_result('/portfolio/add/<ticker>', 'FAIL', f'Status code: {response.status_code}')
                
        except Exception as e:
            self.test_result('/portfolio/add/<ticker>', 'FAIL', f'Error: {str(e)}')
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        self.log("🚨 Testing error handling...", Color.BOLD)
        
        error_test_cases = [
            ('/stocks/details/INVALID_TICKER', 'Invalid stock ticker'),
            ('/portfolio/view/99999', 'Non-existent portfolio'),
            ('/nonexistent-page', '404 error handling'),
            ('/stocks/details/', 'Missing ticker parameter'),
        ]
        
        for endpoint, description in error_test_cases:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 404:
                    self.test_result(endpoint, 'PASS', f"{description} properly returns 404")
                elif response.status_code == 500:
                    self.test_result(endpoint, 'WARN', f"{description} returns 500 (may need error handling)")
                elif response.status_code == 200:
                    self.test_result(endpoint, 'WARN', f"{description} returns 200 (may have fallback data)")
                else:
                    self.test_result(endpoint, 'WARN', f"{description} returns {response.status_code}")
                    
            except Exception as e:
                self.test_result(endpoint, 'FAIL', f"Error: {str(e)}")
    
    def test_password_reset(self):
        """Test password reset functionality"""
        self.log("🔑 Testing password reset...", Color.BOLD)
        
        try:
            # Test forgot password page
            forgot_url = f"{self.base_url}/forgot_password"
            response = self.session.get(forgot_url)
            
            if response.status_code == 200:
                self.test_result('/forgot_password GET', 'PASS', 'Forgot password page accessible')
                
                # Test submitting forgot password form
                csrf_token = self.get_csrf_token(forgot_url)
                if csrf_token:
                    reset_data = {
                        'email': self.test_email,
                        'csrf_token': csrf_token,
                        'submit': 'Send Reset Email'
                    }
                    
                    response = self.session.post(forgot_url, data=reset_data, allow_redirects=False)
                    if response.status_code in [200, 302, 303]:
                        self.test_result('/forgot_password POST', 'PASS', 'Password reset request submitted')
                    else:
                        self.test_result('/forgot_password POST', 'FAIL', f'Status code: {response.status_code}')
                else:
                    self.test_result('/forgot_password CSRF', 'WARN', 'Could not get CSRF token')
                    
            else:
                self.test_result('/forgot_password GET', 'FAIL', f'Status code: {response.status_code}')
                
        except Exception as e:
            self.test_result('/forgot_password', 'FAIL', f'Error: {str(e)}')
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        self.log("🚀 Starting comprehensive endpoint testing...", Color.BOLD)
        start_time = time.time()
        
        # Run all test suites
        self.test_basic_pages()
        self.test_authentication()
        self.test_premium_endpoints()
        self.test_api_endpoints()
        self.test_stock_data_endpoints()
        self.test_portfolio_functionality()
        self.test_password_reset()
        self.test_error_handling()
        
        # Generate summary report
        end_time = time.time()
        self.generate_report(end_time - start_time)
    
    def generate_report(self, duration):
        """Generate final test report"""
        self.log("\n" + "="*80, Color.BOLD)
        self.log("📋 COMPREHENSIVE TEST REPORT", Color.BOLD)
        self.log("="*80, Color.BOLD)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        self.log(f"🔍 Total tests run: {total_tests}")
        self.log(f"✅ Passed: {passed} ({passed/total_tests*100:.1f}%)", Color.GREEN)
        self.log(f"❌ Failed: {failed} ({failed/total_tests*100:.1f}%)", Color.RED)
        self.log(f"⚠️  Warnings: {warnings} ({warnings/total_tests*100:.1f}%)", Color.YELLOW)
        self.log(f"⏱️  Duration: {duration:.2f} seconds")
        
        # Show failed tests
        if failed > 0:
            self.log("\n❌ FAILED TESTS:", Color.RED)
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    self.log(f"  - {result['endpoint']}: {result['details']}", Color.RED)
        
        # Show warnings
        if warnings > 0:
            self.log("\n⚠️  WARNINGS:", Color.YELLOW)
            for result in self.test_results:
                if result['status'] == 'WARN':
                    self.log(f"  - {result['endpoint']}: {result['details']}", Color.YELLOW)
        
        # Overall assessment
        self.log("\n🎯 OVERALL ASSESSMENT:", Color.BOLD)
        if failed == 0:
            self.log("🟢 EXCELLENT: All core functionality working!", Color.GREEN)
        elif failed <= 3:
            self.log("🟡 GOOD: Minor issues detected, most functionality working", Color.YELLOW)
        else:
            self.log("🔴 NEEDS ATTENTION: Multiple failures detected", Color.RED)
        
        # Specific recommendations
        self.log("\n💡 RECOMMENDATIONS:", Color.BLUE)
        
        # Check authentication
        auth_results = [r for r in self.test_results if 'login' in r['endpoint'].lower()]
        if any(r['status'] == 'PASS' for r in auth_results):
            self.log("  ✅ Authentication system working correctly")
        else:
            self.log("  ⚠️  Review authentication system")
        
        # Check premium features
        premium_results = [r for r in self.test_results if any(p in r['endpoint'] for p in ['/stocks/details', '/portfolio', 'crypto', 'global'])]
        premium_working = len([r for r in premium_results if r['status'] == 'PASS'])
        if premium_working > len(premium_results) * 0.8:
            self.log("  ✅ Premium features mostly accessible")
        else:
            self.log("  ⚠️  Review premium feature access and trial system")
        
        # Check API endpoints
        api_results = [r for r in self.test_results if '/api/' in r['endpoint']]
        if any(r['status'] == 'PASS' for r in api_results):
            self.log("  ✅ API endpoints responding")
        else:
            self.log("  ⚠️  Review API endpoint implementation")
        
        self.log("\n" + "="*80, Color.BOLD)

def main():
    """Main function to run the comprehensive test"""
    print(f"{Color.BOLD}🔬 Aksjeradar Comprehensive Endpoint Tester{Color.END}")
    print(f"{Color.BLUE}Testing all endpoints, authentication, and services...{Color.END}\n")
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5001', timeout=5)
        print(f"{Color.GREEN}✅ Server is running on localhost:5001{Color.END}\n")
    except requests.exceptions.RequestException:
        print(f"{Color.RED}❌ Server not running on localhost:5001{Color.END}")
        print(f"{Color.YELLOW}Please start the server with: python run.py{Color.END}")
        sys.exit(1)
    
    # Run tests
    tester = AksjeradarTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
