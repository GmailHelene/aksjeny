#!/usr/bin/env python3
"""
Test login flow for the specified user credentials
"""
import requests
from bs4 import BeautifulSoup
import time

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "helene721@gmail.com"
TEST_PASSWORD = "Soda2001??"
TEST_USERNAME = "helene721"

def get_csrf_token(session, url):
    """Extract CSRF token from a form page"""
    try:
        response = session.get(url)
        if response.status_code != 200:
            print(f"Failed to load {url}: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            return csrf_input.get('value')
        else:
            print("No CSRF token found on page")
            return None
    except Exception as e:
        print(f"Error getting CSRF token: {e}")
        return None

def test_login_with_email():
    """Test login using email"""
    print("\n=== Testing Login with Email ===")
    session = requests.Session()
    
    # Get login page and CSRF token
    csrf_token = get_csrf_token(session, f"{BASE_URL}/login")
    if not csrf_token:
        print("Failed to get CSRF token")
        return False
    
    print(f"Got CSRF token: {csrf_token[:20]}...")
    
    # Try login
    login_data = {
        'username': TEST_EMAIL,  # The form field is called 'username' but accepts both username and email
        'password': TEST_PASSWORD,
        'csrf_token': csrf_token
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"Login response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code in [302, 301]:
        print(f"Redirect location: {response.headers.get('Location', 'No location header')}")
        # Follow redirect
        if 'Location' in response.headers:
            final_response = session.get(response.headers['Location'])
            print(f"Final page status: {final_response.status_code}")
            print(f"Final URL: {final_response.url}")
            
            # Check if we're logged in by looking for user-specific content
            if "Logg ut" in final_response.text or "portfolio" in final_response.text.lower():
                print("✅ Login appears successful")
                return True
            else:
                print("❌ Login may have failed - no logout link found")
                return False
    else:
        print(f"❌ Login failed with status {response.status_code}")
        if response.text:
            print("Response content:")
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for error messages
            error_divs = soup.find_all('div', class_=['alert', 'error', 'flash'])
            for div in error_divs:
                print(f"  Error: {div.get_text().strip()}")
        return False

def test_login_with_username():
    """Test login using username"""
    print("\n=== Testing Login with Username ===")
    session = requests.Session()
    
    # Get login page and CSRF token
    csrf_token = get_csrf_token(session, f"{BASE_URL}/login")
    if not csrf_token:
        print("Failed to get CSRF token")
        return False
    
    print(f"Got CSRF token: {csrf_token[:20]}...")
    
    # Try login with username in username field
    login_data = {
        'username': TEST_USERNAME,
        'password': TEST_PASSWORD,
        'csrf_token': csrf_token
    }
    
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code in [302, 301]:
        print(f"Redirect location: {response.headers.get('Location', 'No location header')}")
        return True
    else:
        print(f"❌ Login with username failed with status {response.status_code}")
        return False

def test_auth_page():
    """Test the /auth page"""
    print("\n=== Testing /auth Page ===")
    session = requests.Session()
    
    try:
        response = session.get(f"{BASE_URL}/auth")
        print(f"Auth page status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Check for login form
            login_form = soup.find('form')
            if login_form:
                print("✅ Auth page loads and has form")
                return True
            else:
                print("❌ Auth page loads but no form found")
                return False
        else:
            print(f"❌ Auth page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing auth page: {e}")
        return False

def test_forgot_password():
    """Test forgot password functionality"""
    print("\n=== Testing Forgot Password ===")
    session = requests.Session()
    
    # Get forgot password page
    csrf_token = get_csrf_token(session, f"{BASE_URL}/forgot_password")
    if not csrf_token:
        print("Failed to get CSRF token for forgot password")
        return False
    
    print(f"Got CSRF token for forgot password: {csrf_token[:20]}...")
    
    # Submit forgot password request
    forgot_data = {
        'email': TEST_EMAIL,
        'csrf_token': csrf_token
    }
    
    response = session.post(f"{BASE_URL}/forgot_password", data=forgot_data, allow_redirects=False)
    print(f"Forgot password response status: {response.status_code}")
    
    if response.status_code in [200, 302]:
        print("✅ Forgot password request submitted successfully")
        return True
    else:
        print(f"❌ Forgot password failed with status {response.status_code}")
        return False

def main():
    """Run all login tests"""
    print("Starting login flow tests...")
    print(f"Testing with email: {TEST_EMAIL}")
    print(f"Testing with username: {TEST_USERNAME}")
    
    results = {
        'auth_page': test_auth_page(),
        'login_email': test_login_with_email(),
        'login_username': test_login_with_username(),
        'forgot_password': test_forgot_password()
    }
    
    print("\n=== Test Results Summary ===")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test}: {status}")
    
    if all(results.values()):
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the details above.")

if __name__ == "__main__":
    main()
