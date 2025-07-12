#!/usr/bin/env python3
"""
Comprehensive Login and Forgot Password Flow Test
Tests complete authentication workflow including edge cases
"""
import sys
import os
import requests
import re
from datetime import datetime, timedelta

# Add project root to path
project_root = '/workspaces/aksjeradarny'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from app.models.user import User
from app.extensions import db
from app.utils.access_control import EXEMPT_EMAILS

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class LoginFlowTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
        
    def log(self, message, color=None):
        """Log message with color"""
        if color:
            print(f"{color}{message}{Color.END}")
        else:
            print(message)
            
    def test_result(self, test_name, status, details=""):
        """Record test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == 'PASS':
            self.log(f"✅ {test_name}: {details}", Color.GREEN)
        elif status == 'FAIL':
            self.log(f"❌ {test_name}: {details}", Color.RED)
        else:
            self.log(f"⚠️ {test_name}: {details}", Color.YELLOW)
    
    def get_csrf_token(self, url):
        """Extract CSRF token from page"""
        try:
            response = self.session.get(url)
            csrf_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', response.text)
            if csrf_match:
                return csrf_match.group(1)
        except Exception as e:
            self.log(f"Error getting CSRF token: {e}", Color.RED)
        return None
    
    def test_database_users(self):
        """Test database user setup"""
        self.log("\n🗄️ Testing Database User Setup", Color.BOLD)
        
        app = create_app()
        with app.app_context():
            # Check exempt users
            for email in EXEMPT_EMAILS:
                user = User.query.filter_by(email=email).first()
                if user:
                    self.test_result(f'Exempt User {email}', 'PASS', 
                                   f'Found: {user.username}, Admin: {user.is_admin}, Subscription: {user.has_subscription}')
                    
                    # Test password for known users
                    if email == 'helene721@gmail.com':
                        test_passwords = ['Soda2001??', 'aksjeradar2024']
                        for pwd in test_passwords:
                            if user.check_password(pwd):
                                self.test_result(f'Password for {email}', 'PASS', f'Works with: {pwd}')
                                break
                        else:
                            self.test_result(f'Password for {email}', 'FAIL', 'No working password found')
                else:
                    self.test_result(f'Exempt User {email}', 'FAIL', 'User not found in database')
    
    def test_login_page_access(self):
        """Test login page accessibility and structure"""
        self.log("\n🌐 Testing Login Page Access", Color.BOLD)
        
        try:
            # Test old login route (should redirect to auth)
            response = self.session.get(f"{self.base_url}/login", allow_redirects=True)
            if response.status_code == 200:
                self.test_result('Login Route Access', 'PASS', f'Status: {response.status_code}')
                
                # Check for CSRF token
                if 'csrf_token' in response.text:
                    self.test_result('Login CSRF Token', 'PASS', 'CSRF token present')
                else:
                    self.test_result('Login CSRF Token', 'FAIL', 'CSRF token missing')
                    
                # Check for form elements
                if 'password' in response.text and 'username' in response.text:
                    self.test_result('Login Form Elements', 'PASS', 'Username and password fields present')
                else:
                    self.test_result('Login Form Elements', 'FAIL', 'Missing form elements')
            else:
                self.test_result('Login Route Access', 'FAIL', f'Status: {response.status_code}')
                
            # Test new auth page
            response = self.session.get(f"{self.base_url}/auth")
            if response.status_code == 200:
                self.test_result('Auth Page Access', 'PASS', f'Status: {response.status_code}')
                
                # Check for both login and register tabs
                if 'login-tab' in response.text and 'register-tab' in response.text:
                    self.test_result('Auth Page Tabs', 'PASS', 'Both login and register tabs present')
                else:
                    self.test_result('Auth Page Tabs', 'FAIL', 'Missing login or register tabs')
            else:
                self.test_result('Auth Page Access', 'FAIL', f'Status: {response.status_code}')
                
        except Exception as e:
            self.test_result('Login Page Access', 'FAIL', f'Exception: {str(e)}')
    
    def test_login_functionality(self):
        """Test actual login functionality"""
        self.log("\n🔐 Testing Login Functionality", Color.BOLD)
        
        # Test cases: valid credentials, invalid credentials, CSRF protection
        test_cases = [
            {
                'name': 'Valid Login (Auth Page)',
                'url': f"{self.base_url}/auth",
                'post_url': f"{self.base_url}/login",
                'username': 'helene721@gmail.com',
                'password': 'Soda2001??',
                'should_succeed': True
            },
            {
                'name': 'Valid Login (Email)',
                'url': f"{self.base_url}/auth",
                'post_url': f"{self.base_url}/login",
                'username': 'helene721@gmail.com',
                'password': 'Soda2001??',
                'should_succeed': True
            },
            {
                'name': 'Valid Login (Username)',
                'url': f"{self.base_url}/auth", 
                'post_url': f"{self.base_url}/login",
                'username': 'helene721',
                'password': 'Soda2001??',
                'should_succeed': True
            },
            {
                'name': 'Invalid Password',
                'url': f"{self.base_url}/auth",
                'post_url': f"{self.base_url}/login",
                'username': 'helene721@gmail.com',
                'password': 'wrongpassword',
                'should_succeed': False
            },
            {
                'name': 'Invalid Username',
                'url': f"{self.base_url}/auth",
                'post_url': f"{self.base_url}/login",
                'username': 'nonexistent@email.com',
                'password': 'anypassword',
                'should_succeed': False
            }
        ]
        
        for test_case in test_cases:
            try:
                # Get CSRF token
                csrf_token = self.get_csrf_token(test_case['url'])
                if not csrf_token:
                    self.test_result(test_case['name'], 'FAIL', 'Could not get CSRF token')
                    continue
                
                # Attempt login
                login_data = {
                    'username': test_case['username'],
                    'password': test_case['password'],
                    'csrf_token': csrf_token
                }
                
                response = self.session.post(test_case['post_url'], data=login_data, allow_redirects=False)
                
                if test_case['should_succeed']:
                    if response.status_code in [302, 303]:
                        self.test_result(test_case['name'], 'PASS', f'Login successful (redirect: {response.status_code})')
                        
                        # Test access to protected page
                        protected_response = self.session.get(f"{self.base_url}/analysis")
                        if protected_response.status_code == 200:
                            self.test_result(f"{test_case['name']} - Protected Access", 'PASS', 'Can access protected pages')
                        else:
                            self.test_result(f"{test_case['name']} - Protected Access", 'FAIL', f'Cannot access protected pages: {protected_response.status_code}')
                        
                        # Logout for next test
                        self.session.get(f"{self.base_url}/logout")
                    else:
                        self.test_result(test_case['name'], 'FAIL', f'Login failed: {response.status_code}')
                else:
                    if response.status_code == 200 and 'Ugyldig' in response.text:
                        self.test_result(test_case['name'], 'PASS', 'Correctly rejected invalid credentials')
                    elif response.status_code in [302, 303]:
                        self.test_result(test_case['name'], 'FAIL', 'Invalid credentials were accepted')
                    else:
                        self.test_result(test_case['name'], 'WARN', f'Unexpected response: {response.status_code}')
                        
            except Exception as e:
                self.test_result(test_case['name'], 'FAIL', f'Exception: {str(e)}')
    
    def test_forgot_password_flow(self):
        """Test forgot password functionality"""
        self.log("\n🔑 Testing Forgot Password Flow", Color.BOLD)
        
        try:
            # Test forgot password page access
            response = self.session.get(f"{self.base_url}/forgot_password")
            if response.status_code == 200:
                self.test_result('Forgot Password Page', 'PASS', 'Page accessible')
                
                # Check for form elements
                if 'email' in response.text and 'csrf_token' in response.text:
                    self.test_result('Forgot Password Form', 'PASS', 'Form elements present')
                    
                    # Test password reset request
                    csrf_token = self.get_csrf_token(f"{self.base_url}/forgot_password")
                    if csrf_token:
                        reset_data = {
                            'email': 'helene721@gmail.com',
                            'csrf_token': csrf_token
                        }
                        
                        response = self.session.post(f"{self.base_url}/forgot_password", data=reset_data, allow_redirects=False)
                        if response.status_code in [200, 302, 303]:
                            self.test_result('Password Reset Request', 'PASS', 'Reset request submitted successfully')
                        else:
                            self.test_result('Password Reset Request', 'FAIL', f'Reset request failed: {response.status_code}')
                    else:
                        self.test_result('Password Reset Request', 'FAIL', 'Could not get CSRF token')
                else:
                    self.test_result('Forgot Password Form', 'FAIL', 'Missing form elements')
            else:
                self.test_result('Forgot Password Page', 'FAIL', f'Page not accessible: {response.status_code}')
                
            # Test with invalid email
            csrf_token = self.get_csrf_token(f"{self.base_url}/forgot_password")
            if csrf_token:
                reset_data = {
                    'email': 'nonexistent@example.com',
                    'csrf_token': csrf_token
                }
                
                response = self.session.post(f"{self.base_url}/forgot_password", data=reset_data)
                if 'Ingen bruker funnet' in response.text or 'funnet' in response.text:
                    self.test_result('Invalid Email Reset', 'PASS', 'Correctly handles invalid email')
                else:
                    self.test_result('Invalid Email Reset', 'WARN', 'Response unclear for invalid email')
                    
        except Exception as e:
            self.test_result('Forgot Password Flow', 'FAIL', f'Exception: {str(e)}')
    
    def test_password_reset_token(self):
        """Test password reset token functionality"""
        self.log("\n🎫 Testing Password Reset Token", Color.BOLD)
        
        app = create_app()
        with app.app_context():
            try:
                user = User.query.filter_by(email='helene721@gmail.com').first()
                if user:
                    # Generate token using app functions
                    from app.routes.main import generate_reset_token, verify_reset_token
                    from flask import url_for
                    
                    token = generate_reset_token(user)
                    self.test_result('Token Generation', 'PASS', f'Token generated: {token[:20]}...')
                    
                    # Verify token
                    verified_user = verify_reset_token(token)
                    if verified_user and verified_user.email == user.email:
                        self.test_result('Token Verification', 'PASS', 'Token verified successfully')
                        
                        # Test reset URL access
                        with app.test_request_context():
                            reset_url = url_for('main.reset_password', token=token, _external=True)
                            reset_url = reset_url.replace('localhost', '127.0.0.1:5001').replace('http://127.0.0.1:5001', self.base_url)
                        
                        try:
                            response = self.session.get(reset_url)
                            if response.status_code == 200:
                                self.test_result('Reset URL Access', 'PASS', 'Reset page accessible with token')
                                
                                if 'password' in response.text and 'csrf_token' in response.text:
                                    self.test_result('Reset Form', 'PASS', 'Reset form elements present')
                                else:
                                    self.test_result('Reset Form', 'FAIL', 'Reset form incomplete')
                            else:
                                self.test_result('Reset URL Access', 'FAIL', f'Reset page not accessible: {response.status_code}')
                        except Exception as e:
                            self.test_result('Reset URL Access', 'FAIL', f'Exception accessing reset URL: {str(e)}')
                    else:
                        self.test_result('Token Verification', 'FAIL', 'Token verification failed')
                else:
                    self.test_result('Token Generation', 'FAIL', 'Test user not found')
                    
            except Exception as e:
                self.test_result('Password Reset Token', 'FAIL', f'Exception: {str(e)}')
    
    def test_csrf_protection(self):
        """Test CSRF protection in authentication"""
        self.log("\n🛡️ Testing CSRF Protection", Color.BOLD)
        
        try:
            # Test login without CSRF token
            login_data = {
                'username': 'helene721@gmail.com',
                'password': 'Soda2001??'
                # No CSRF token
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            if response.status_code == 400 or 'CSRF' in response.text or 'token' in response.text.lower():
                self.test_result('Login CSRF Protection', 'PASS', 'Login properly protected against CSRF')
            else:
                self.test_result('Login CSRF Protection', 'WARN', 'CSRF protection may not be working')
            
            # Test forgot password without CSRF token
            reset_data = {
                'email': 'helene721@gmail.com'
                # No CSRF token
            }
            
            response = self.session.post(f"{self.base_url}/forgot_password", data=reset_data)
            if response.status_code == 400 or 'CSRF' in response.text or 'token' in response.text.lower():
                self.test_result('Reset CSRF Protection', 'PASS', 'Password reset properly protected against CSRF')
            else:
                self.test_result('Reset CSRF Protection', 'WARN', 'CSRF protection may not be working')
                
        except Exception as e:
            self.test_result('CSRF Protection', 'FAIL', f'Exception: {str(e)}')
    
    def test_session_management(self):
        """Test session management and persistence"""
        self.log("\n🍪 Testing Session Management", Color.BOLD)
        
        try:
            # Login and check session persistence
            csrf_token = self.get_csrf_token(f"{self.base_url}/auth")
            if csrf_token:
                login_data = {
                    'username': 'helene721@gmail.com',
                    'password': 'Soda2001??',
                    'csrf_token': csrf_token,
                    'remember_me': 'on'
                }
                
                response = self.session.post(f"{self.base_url}/login", data=login_data, allow_redirects=False)
                if response.status_code in [302, 303]:
                    self.test_result('Login with Remember Me', 'PASS', 'Login successful')
                    
                    # Check if session persists across requests
                    response = self.session.get(f"{self.base_url}/")
                    if 'Logg ut' in response.text or 'logout' in response.text:
                        self.test_result('Session Persistence', 'PASS', 'Session persists across requests')
                    else:
                        self.test_result('Session Persistence', 'FAIL', 'Session does not persist')
                    
                    # Test logout
                    response = self.session.get(f"{self.base_url}/logout")
                    if response.status_code in [200, 302, 303]:
                        self.test_result('Logout Functionality', 'PASS', 'Logout successful')
                        
                        # Check if session is cleared
                        response = self.session.get(f"{self.base_url}/")
                        if 'Logg inn' in response.text or 'login' in response.text:
                            self.test_result('Session Cleanup', 'PASS', 'Session properly cleared after logout')
                        else:
                            self.test_result('Session Cleanup', 'FAIL', 'Session not properly cleared')
                    else:
                        self.test_result('Logout Functionality', 'FAIL', f'Logout failed: {response.status_code}')
                else:
                    self.test_result('Login with Remember Me', 'FAIL', f'Login failed: {response.status_code}')
            else:
                self.test_result('Session Management', 'FAIL', 'Could not get CSRF token')
                
        except Exception as e:
            self.test_result('Session Management', 'FAIL', f'Exception: {str(e)}')
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        self.log("\n⚠️ Testing Edge Cases", Color.BOLD)
        
        # Test empty form submissions
        try:
            csrf_token = self.get_csrf_token(f"{self.base_url}/auth")
            if csrf_token:
                # Empty login
                response = self.session.post(f"{self.base_url}/login", data={'csrf_token': csrf_token})
                if 'required' in response.text.lower() or 'påkrevd' in response.text:
                    self.test_result('Empty Login Form', 'PASS', 'Properly validates empty fields')
                else:
                    self.test_result('Empty Login Form', 'WARN', 'Validation may not be working')
                
                # Empty forgot password
                response = self.session.post(f"{self.base_url}/forgot_password", data={'csrf_token': csrf_token})
                if 'required' in response.text.lower() or 'påkrevd' in response.text:
                    self.test_result('Empty Reset Form', 'PASS', 'Properly validates empty email')
                else:
                    self.test_result('Empty Reset Form', 'WARN', 'Validation may not be working')
        except Exception as e:
            self.test_result('Edge Cases', 'FAIL', f'Exception: {str(e)}')
        
        # Test SQL injection attempts
        try:
            csrf_token = self.get_csrf_token(f"{self.base_url}/auth")
            if csrf_token:
                malicious_data = {
                    'username': "' OR '1'='1' --",
                    'password': "anything",
                    'csrf_token': csrf_token
                }
                
                response = self.session.post(f"{self.base_url}/login", data=malicious_data)
                if response.status_code in [302, 303]:
                    self.test_result('SQL Injection Protection', 'FAIL', 'Possible SQL injection vulnerability')
                else:
                    self.test_result('SQL Injection Protection', 'PASS', 'Protected against SQL injection')
        except Exception as e:
            self.test_result('SQL Injection Protection', 'WARN', f'Exception: {str(e)}')
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("\n📊 Test Report Summary", Color.BOLD)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        
        self.log(f"Total Tests: {total_tests}")
        self.log(f"✅ Passed: {passed}", Color.GREEN)
        self.log(f"❌ Failed: {failed}", Color.RED)
        self.log(f"⚠️ Warnings: {warnings}", Color.YELLOW)
        
        if failed > 0:
            self.log("\n❌ Failed Tests:", Color.RED)
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    self.log(f"  - {result['test']}: {result['details']}")
        
        if warnings > 0:
            self.log("\n⚠️ Warnings:", Color.YELLOW)
            for result in self.test_results:
                if result['status'] == 'WARN':
                    self.log(f"  - {result['test']}: {result['details']}")
    
    def run_all_tests(self):
        """Run all authentication flow tests"""
        self.log("🚀 Starting Comprehensive Login Flow Tests", Color.BOLD)
        self.log(f"Testing against: {self.base_url}")
        
        self.test_database_users()
        self.test_login_page_access()
        self.test_login_functionality()
        self.test_forgot_password_flow()
        self.test_password_reset_token()
        self.test_csrf_protection()
        self.test_session_management()
        self.test_edge_cases()
        
        self.generate_report()

def main():
    """Main function"""
    tester = LoginFlowTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
