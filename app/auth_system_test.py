#!/usr/bin/env python3
"""
Authentication System Tester for Aksjeradar
This script tests user authentication-related functionality:
- User registration
- Login and logout
- Password reset
- Account management
- Session handling
- CSRF protection
"""
import os
import sys
import requests
import json
import uuid
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
        logging.FileHandler("auth_test.log"),
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

class AuthTester:
    """Tester for authentication functionality"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        # Generate a unique email for testing
        unique_id = uuid.uuid4().hex[:8]
        self.test_user = {
            "email": f"test_user_{unique_id}@aksjeradar.test",
            "password": "TestPassword123!",
            "new_password": "NewTestPassword456!"
        }
        self.registered = False
    
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
    
    def test_registration_page(self):
        """Test the registration page"""
        self.print_section("Testing Registration Page")
        
        response, success = self.make_request('get', '/register')
        if not success:
            self.print_result("Registration Page", False, "Could not access registration page")
            return False
        
        # Check for registration form
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            self.print_result("Registration Form", False, "No form found on registration page")
            return False
        
        # Check for required fields
        email_input = form.find('input', {'name': lambda x: x and 'email' in x.lower()})
        password_input = form.find('input', {'type': 'password'})
        
        if email_input:
            self.print_result("Email Field", True)
        else:
            self.print_result("Email Field", False, "No email field found in registration form")
        
        if password_input:
            self.print_result("Password Field", True)
        else:
            self.print_result("Password Field", False, "No password field found in registration form")
        
        # Extract CSRF token
        self.csrf_token = self.extract_csrf_token(response.text)
        if self.csrf_token:
            self.print_result("CSRF Protection", True, "CSRF token found in registration form")
        else:
            self.print_result("CSRF Protection", False, "No CSRF token found in registration form")
        
        return success
    
    def test_user_registration(self):
        """Test user registration"""
        self.print_section("Testing User Registration")
        
        # If we don't have a CSRF token, we need to get one
        if not self.csrf_token:
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
        if not success:
            self.print_result("User Registration", False, "Registration request failed")
            return False
        
        # Check response for success indicators
        if "success" in response.text.lower() or "registered" in response.text.lower() or "welcome" in response.text.lower():
            self.print_result("User Registration", True, f"Successfully registered user: {self.test_user['email']}")
            self.registered = True
        else:
            # Check if user might already exist
            if "already exists" in response.text.lower() or "already registered" in response.text.lower():
                self.print_result("User Registration", False, "User already exists, try with a different email")
            else:
                self.print_result("User Registration", False, "Registration response doesn't indicate success")
            return False
        
        return True
    
    def test_login_page(self):
        """Test the login page"""
        self.print_section("Testing Login Page")
        
        response, success = self.make_request('get', '/login')
        if not success:
            self.print_result("Login Page", False, "Could not access login page")
            return False
        
        # Check for login form
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        
        if not form:
            self.print_result("Login Form", False, "No form found on login page")
            return False
        
        # Check for required fields
        email_input = form.find('input', {'name': lambda x: x and 'email' in x.lower()})
        password_input = form.find('input', {'type': 'password'})
        
        if email_input:
            self.print_result("Email Field", True)
        else:
            self.print_result("Email Field", False, "No email field found in login form")
        
        if password_input:
            self.print_result("Password Field", True)
        else:
            self.print_result("Password Field", False, "No password field found in login form")
        
        # Check for password reset link
        reset_link = soup.find('a', string=lambda s: s and 'password' in s.lower() and ('reset' in s.lower() or 'forgot' in s.lower()))
        if reset_link:
            self.print_result("Password Reset Link", True)
        else:
            self.print_result("Password Reset Link", False, "No password reset link found on login page")
        
        # Extract CSRF token
        self.csrf_token = self.extract_csrf_token(response.text)
        if self.csrf_token:
            self.print_result("CSRF Protection", True, "CSRF token found in login form")
        else:
            self.print_result("CSRF Protection", False, "No CSRF token found in login form")
        
        return success
    
    def test_user_login(self):
        """Test user login"""
        self.print_section("Testing User Login")
        
        # If we don't have a CSRF token, we need to get one
        if not self.csrf_token:
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
            self.print_result("User Login", False, "Login request failed")
            return False
        
        # Check response for success indicators
        if "success" in response.text.lower() or "logged in" in response.text.lower() or "welcome" in response.text.lower() or "dashboard" in response.text.lower():
            self.print_result("User Login", True, f"Successfully logged in as: {self.test_user['email']}")
        else:
            self.print_result("User Login", False, "Login response doesn't indicate success")
            return False
        
        # Test that we can access a protected page
        response, success = self.make_request('get', '/dashboard')  # Assuming /dashboard is a protected page
        if success:
            self.print_result("Access Protected Page", True, "Successfully accessed protected page after login")
        else:
            self.print_result("Access Protected Page", False, "Could not access protected page after login")
        
        return True
    
    def test_csrf_protection(self):
        """Test CSRF protection"""
        self.print_section("Testing CSRF Protection")
        
        # Try to make a POST request without CSRF token
        login_data = {
            'email': self.test_user['email'],
            'password': self.test_user['password']
        }
        
        response, _ = self.make_request('post', '/login', expected_status=None, data=login_data)
        
        if response and response.status_code in (400, 403, 422):
            self.print_result("CSRF Protection", True, f"Request correctly rejected with status code: {response.status_code}")
        else:
            status_code = response.status_code if response else "No response"
            self.print_result("CSRF Protection", False, f"Request without CSRF token not properly rejected: {status_code}")
            return False
        
        return True
    
    def test_password_reset(self):
        """Test password reset functionality"""
        self.print_section("Testing Password Reset")
        
        # Get password reset page
        response, success = self.make_request('get', '/reset_password')
        if not success:
            self.print_result("Password Reset Page", False, "Could not access password reset page")
            return False
        
        # Extract CSRF token
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_result("Extract CSRF Token", False, "Could not extract CSRF token from password reset page")
            return False
        
        # Submit password reset request
        reset_data = {
            'email': self.test_user['email'],
            'csrf_token': self.csrf_token
        }
        
        response, success = self.make_request('post', '/reset_password', data=reset_data, allow_redirects=True)
        if not success:
            self.print_result("Password Reset Request", False, "Password reset request failed")
            return False
        
        # Check response for success indicators
        if "email" in response.text.lower() and ("sent" in response.text.lower() or "check" in response.text.lower()):
            self.print_result("Password Reset Request", True, "Password reset email would be sent in production")
        else:
            self.print_result("Password Reset Request", False, "Password reset response doesn't indicate success")
            return False
        
        # Note: We can't actually test the reset link since it would be sent by email
        self.print_result("Complete Password Reset", True, "Test limited to reset request (can't test email link)")
        
        return True
    
    def test_logout(self):
        """Test user logout"""
        self.print_section("Testing User Logout")
        
        response, success = self.make_request('get', '/logout', allow_redirects=True)
        if not success:
            self.print_result("User Logout", False, "Logout request failed")
            return False
        
        # Check if we're redirected to login page or home
        if "login" in response.url.lower() or "login" in response.text.lower():
            self.print_result("User Logout", True, "Successfully logged out and redirected to login page")
        else:
            # Check for other logout indicators
            if "logged out" in response.text.lower() or "sign in" in response.text.lower():
                self.print_result("User Logout", True, "Successfully logged out")
            else:
                self.print_result("User Logout", False, "Logout response doesn't indicate success")
                return False
        
        # Verify we can't access protected pages anymore
        response, _ = self.make_request('get', '/dashboard', expected_status=None)
        
        if response and (response.status_code in (302, 303) or "login" in response.url.lower()):
            self.print_result("Protection After Logout", True, "Correctly redirected when accessing protected page after logout")
        else:
            status_code = response.status_code if response else "No response"
            self.print_result("Protection After Logout", False, f"Still able to access protected page after logout: {status_code}")
            return False
        
        return True
    
    def test_password_change(self):
        """Test password change functionality"""
        self.print_section("Testing Password Change")
        
        # First login
        if not self.test_user_login():
            self.print_result("Login for Password Change", False, "Could not login to test password change")
            return False
        
        # Get account settings or password change page
        response, success = self.make_request('get', '/account/settings')
        if not success:
            # Try alternative URL
            response, success = self.make_request('get', '/change_password')
            if not success:
                self.print_result("Password Change Page", False, "Could not access password change page")
                return False
        
        # Extract CSRF token
        self.csrf_token = self.extract_csrf_token(response.text)
        if not self.csrf_token:
            self.print_result("Extract CSRF Token", False, "Could not extract CSRF token from password change page")
            return False
        
        # Submit password change
        change_data = {
            'current_password': self.test_user['password'],
            'new_password': self.test_user['new_password'],
            'confirm_password': self.test_user['new_password'],
            'csrf_token': self.csrf_token
        }
        
        # Try different endpoint formats
        for endpoint in ['/account/password', '/change_password', '/account/settings']:
            response, success = self.make_request('post', endpoint, data=change_data, allow_redirects=True, expected_status=None)
            if success or (response and "password" in response.text.lower() and "changed" in response.text.lower()):
                self.print_result("Password Change", True, f"Successfully changed password using endpoint: {endpoint}")
                
                # Update password for subsequent tests
                old_password = self.test_user['password']
                self.test_user['password'] = self.test_user['new_password']
                self.test_user['new_password'] = old_password
                
                return True
        
        self.print_result("Password Change", False, "Could not change password with any endpoint")
        return False
    
    def test_session_handling(self):
        """Test session handling"""
        self.print_section("Testing Session Handling")
        
        # Login
        if not self.test_user_login():
            self.print_result("Login for Session Test", False, "Could not login to test sessions")
            return False
        
        # Check session cookie
        has_session_cookie = False
        for cookie in self.session.cookies:
            if cookie.name.lower() in ('session', 'sessionid', 'aksjeradar_session'):
                has_session_cookie = True
                break
        
        if has_session_cookie:
            self.print_result("Session Cookie", True, "Session cookie found after login")
        else:
            self.print_result("Session Cookie", False, "No session cookie found after login")
            return False
        
        # Make a request to confirm session is valid
        response, success = self.make_request('get', '/dashboard')
        if success:
            self.print_result("Session Validity", True, "Session is valid for accessing protected content")
        else:
            self.print_result("Session Validity", False, "Session is not valid for accessing protected content")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all authentication tests"""
        self.print_header("Aksjeradar Authentication System Test")
        print(f"Testing against: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test user email: {self.test_user['email']}")
        
        # Test registration flow
        self.test_registration_page()
        self.test_user_registration()
        
        # Test login flow
        self.test_login_page()
        self.test_user_login()
        
        # Test CSRF protection
        self.test_csrf_protection()
        
        # Test password reset
        self.test_password_reset()
        
        # Test password change
        self.test_password_change()
        
        # Test session handling
        self.test_session_handling()
        
        # Test logout
        self.test_logout()
        
        self.print_header("Test Complete")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Authentication System Tester for Aksjeradar')
    parser.add_argument('--base-url', default='http://localhost:5000', help='Base URL to test against')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    tester = AuthTester(args.base_url)
    tester.run_all_tests()
