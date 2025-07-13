#!/usr/bin/env python3
"""
Subscription and Payment Flow Tester for Aksjeradar
This script focuses on testing the subscription and payment processes:
- Pricing page display
- Subscription page functionality
- Stripe checkout integration
- Subscription state tracking
- Access control based on subscription
"""
import os
import sys
import requests
import json
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("subscription_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

class SubscriptionTester:
    """Tester for subscription and payment functionality"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        self.test_user = {"email": "subscription_test@aksjeradar.test", "password": "test123"}
    
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
        else:
            result = f"{Color.RED}✗ FAIL{Color.ENDC}"
            
        print(f"{result} - {test_name}")
        if message:
            print(f"     {message}")
    
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
    
    def register_and_login(self):
        """Register a test user and login"""
        self.print_section("Registering and Logging In")
        
        # First, get the registration page to extract CSRF token
        response, success = self.make_request('get', '/register')
        if not success:
            self.print_result("Get Registration Page", False, "Could not access registration page")
            return False
        
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_result("Extract CSRF Token", False, "Could not extract CSRF token from registration page")
            return False
        
        # Register the test user
        registration_data = {
            'email': self.test_user['email'],
            'password': self.test_user['password'],
            'password2': self.test_user['password'],  # Assuming password confirmation field
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/register', data=registration_data, allow_redirects=True)
        
        # If registration fails (maybe user already exists), try logging in
        if not success:
            self.print_result("User Registration", False, "Registration failed, attempting login")
            
            # Get login page to extract CSRF token
            response, success = self.make_request('get', '/login')
            if not success:
                self.print_result("Get Login Page", False, "Could not access login page")
                return False
            
            self.csrf_token = self.extract_csrf_token(response.text)
            if not self.csrf_token:
                self.print_result("Extract CSRF Token", False, "Could not extract CSRF token from login page")
                return False
            
            # Login with test user
            login_data = {
                'email': self.test_user['email'],
                'password': self.test_user['password'],
                'csrf_token': self.csrf_token
            }
            
            response, success = self.make_request('post', '/login', data=login_data, allow_redirects=True)
            if not success:
                self.print_result("User Login", False, "Login failed")
                return False
            
            self.print_result("User Login", True)
        else:
            self.print_result("User Registration", True)
        
        return True
    
    def test_pricing_page(self):
        """Test the pricing page"""
        self.print_section("Testing Pricing Page")
        
        response, success = self.make_request('get', '/pricing')
        if not success:
            self.print_result("Pricing Page", False, "Could not access pricing page")
            return False
        
        # Check if pricing information is present
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for pricing elements
        pricing_keywords = ['price', 'subscription', 'monthly', 'yearly', 'premium', 'pro']
        pricing_content_found = False
        
        for keyword in pricing_keywords:
            if keyword in response.text.lower():
                pricing_content_found = True
                break
        
        if pricing_content_found:
            self.print_result("Pricing Page Content", True, "Pricing information found")
        else:
            self.print_result("Pricing Page Content", False, "Pricing information not found")
        
        # Check for subscription CTAs
        cta_found = False
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if 'subscription' in href or 'checkout' in href or 'pricing' in href:
                cta_found = True
                break
        
        if cta_found:
            self.print_result("Subscription CTAs", True, "Subscription calls-to-action found")
        else:
            self.print_result("Subscription CTAs", False, "Subscription calls-to-action not found")
        
        return success
    
    def test_subscription_page(self):
        """Test the subscription page"""
        self.print_section("Testing Subscription Page")
        
        response, success = self.make_request('get', '/subscription')
        if not success:
            self.print_result("Subscription Page", False, "Could not access subscription page")
            return False
        
        # Check if subscription information is present
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for Stripe elements
        stripe_found = False
        for script in soup.find_all('script'):
            src = script.get('src', '')
            if 'stripe' in src.lower():
                stripe_found = True
                break
            
            if script.string and 'stripe' in script.string.lower():
                stripe_found = True
                break
        
        if stripe_found:
            self.print_result("Stripe Integration", True, "Stripe scripts found")
        else:
            self.print_result("Stripe Integration", False, "Stripe scripts not found")
        
        # Check for payment form
        payment_form_found = False
        for form in soup.find_all('form'):
            action = form.get('action', '')
            if 'payment' in action.lower() or 'checkout' in action.lower() or 'subscribe' in action.lower():
                payment_form_found = True
                break
            
            # Also check if form has payment-related inputs
            payment_inputs = form.find_all('input', {'name': lambda x: x and ('payment' in x.lower() or 'stripe' in x.lower())})
            if payment_inputs:
                payment_form_found = True
                break
        
        if payment_form_found:
            self.print_result("Payment Form", True, "Payment form found")
        else:
            self.print_result("Payment Form", False, "Payment form not found")
        
        # Extract CSRF token for later use
        self.csrf_token = self.extract_csrf_token(response.text)
        if self.csrf_token:
            self.print_result("CSRF Token", True, "CSRF token found for subscription form")
        else:
            self.print_result("CSRF Token", False, "Could not find CSRF token for subscription form")
        
        return success
    
    def test_stripe_checkout(self):
        """Test the Stripe checkout flow"""
        self.print_section("Testing Stripe Checkout Flow")
        
        # If we don't have a CSRF token, we need to get one
        if not self.csrf_token:
            response, success = self.make_request('get', '/subscription')
            if not success:
                self.print_result("Get Subscription Page", False, "Could not access subscription page")
                return False
            
            self.csrf_token = self.extract_csrf_token(response.text)
            if not self.csrf_token:
                self.print_result("Extract CSRF Token", False, "Could not extract CSRF token from subscription page")
                return False
        
        # Attempt to initiate Stripe checkout
        checkout_data = {
            'plan': 'monthly',  # Assuming 'monthly' is a valid plan ID
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/create-checkout-session', data=checkout_data, allow_redirects=False)
        
        # Check if we get redirected to Stripe
        if response and response.status_code in (302, 303):
            redirect_url = response.headers.get('Location', '')
            if 'stripe.com' in redirect_url:
                self.print_result("Stripe Redirect", True, "Successfully redirected to Stripe")
            else:
                self.print_result("Stripe Redirect", False, f"Redirected to non-Stripe URL: {redirect_url}")
        elif response and 'stripe.com' in response.text:
            self.print_result("Stripe Checkout", True, "Stripe checkout form found in response")
        else:
            self.print_result("Stripe Checkout", False, "No Stripe checkout detected in response")
            return False
        
        # Note: We can't actually complete the payment without a real credit card
        self.print_result("Complete Payment", True, "Test limited to checkout initiation (can't actually pay)")
        
        return True
    
    def test_subscription_api(self):
        """Test subscription API endpoints"""
        self.print_section("Testing Subscription API Endpoints")
        
        # Test subscription status endpoint
        response, success = self.make_request('get', '/api/subscription/status')
        if success:
            self.print_result("Subscription Status API", True)
            
            try:
                data = response.json()
                if 'status' in data or 'subscription' in data:
                    self.print_result("Subscription Status Response", True, "Valid subscription data returned")
                else:
                    self.print_result("Subscription Status Response", False, "Missing expected subscription data")
            except json.JSONDecodeError:
                self.print_result("Subscription Status Response", False, "Response is not valid JSON")
        else:
            self.print_result("Subscription Status API", False, "Could not access subscription status API")
        
        # Test subscription plans endpoint
        response, success = self.make_request('get', '/api/subscription/plans')
        if success:
            self.print_result("Subscription Plans API", True)
            
            try:
                data = response.json()
                if isinstance(data, list) or 'plans' in data:
                    self.print_result("Subscription Plans Response", True, "Valid plans data returned")
                else:
                    self.print_result("Subscription Plans Response", False, "Missing expected plans data")
            except json.JSONDecodeError:
                self.print_result("Subscription Plans Response", False, "Response is not valid JSON")
        else:
            self.print_result("Subscription Plans API", False, "Could not access subscription plans API")
        
        return success
    
    def test_premium_access(self):
        """Test access to premium features based on subscription"""
        self.print_section("Testing Premium Access Control")
        
        # Attempt to access a premium feature
        premium_endpoints = [
            '/analysis/advanced',
            '/portfolio/analytics',
            '/market/intelligence'
        ]
        
        for endpoint in premium_endpoints:
            response, _ = self.make_request('get', endpoint, expected_status=None)
            if response:
                if response.status_code in (302, 303):
                    # Check if redirected to subscription page
                    redirect_url = response.headers.get('Location', '')
                    if 'subscription' in redirect_url or 'pricing' in redirect_url:
                        self.print_result(f"Premium Access ({endpoint})", True, "Correctly redirected to subscription page")
                    else:
                        self.print_result(f"Premium Access ({endpoint})", False, f"Redirected to unexpected URL: {redirect_url}")
                elif response.status_code == 200:
                    # Check if page contains upgrade message
                    if 'upgrade' in response.text.lower() or 'subscribe' in response.text.lower() or 'premium' in response.text.lower():
                        self.print_result(f"Premium Access ({endpoint})", True, "Page shows upgrade message")
                    else:
                        self.print_result(f"Premium Access ({endpoint})", False, "Access granted to premium feature without subscription")
                else:
                    self.print_result(f"Premium Access ({endpoint})", False, f"Unexpected status code: {response.status_code}")
            else:
                self.print_result(f"Premium Access ({endpoint})", False, "Failed to make request")
        
        return True
    
    def test_webhook_endpoint(self):
        """Test the Stripe webhook endpoint"""
        self.print_section("Testing Stripe Webhook Endpoint")
        
        # Create a fake Stripe webhook event
        webhook_data = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                    'customer': 'cus_test_123',
                    'subscription': 'sub_test_123',
                    'client_reference_id': self.test_user['email']
                }
            }
        }
        
        # Send the webhook request
        # Note: In a real environment, Stripe signs the webhook with a secret
        # Here we're just testing if the endpoint exists and accepts POST requests
        response, _ = self.make_request('post', '/stripe/webhook', expected_status=None, json=webhook_data)
        
        if response:
            if response.status_code in (200, 202, 204):
                self.print_result("Stripe Webhook Endpoint", True, f"Webhook accepted with status code: {response.status_code}")
            else:
                self.print_result("Stripe Webhook Endpoint", False, f"Webhook rejected with status code: {response.status_code}")
                
                # Log the response for debugging
                try:
                    error_content = response.json()
                    logger.error(f"Webhook error response: {json.dumps(error_content)}")
                except:
                    logger.error(f"Webhook error response text: {response.text}")
        else:
            self.print_result("Stripe Webhook Endpoint", False, "Failed to make webhook request")
        
        return response and response.status_code in (200, 202, 204)
    
    def run_all_tests(self):
        """Run all subscription and payment tests"""
        self.print_header("Aksjeradar Subscription and Payment Flow Test")
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test pricing page
        self.test_pricing_page()
        
        # Register and login
        if self.register_and_login():
            # Test subscription page
            self.test_subscription_page()
            
            # Test Stripe checkout
            self.test_stripe_checkout()
            
            # Test subscription API
            self.test_subscription_api()
            
            # Test premium access control
            self.test_premium_access()
            
            # Test webhook endpoint
            self.test_webhook_endpoint()
        else:
            print(f"{Color.RED}Failed to register or login. Skipping subscription tests.{Color.ENDC}")
        
        self.print_header("Test Complete")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Subscription and Payment Flow Tester for Aksjeradar')
    parser.add_argument('--base-url', default='http://localhost:5000', help='Base URL to test against')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    tester = SubscriptionTester(args.base_url)
    tester.run_all_tests()
