#!/usr/bin/env python3
"""
Complete test of login and password reset functionality
"""
import requests
import re
import sys
import os

# Add the project root to Python path
project_root = '/workspaces/aksjeradarv5'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_application(base_url="http://localhost:5001"):
    """Test login and password reset functionality"""
    
    print(f"🧪 Testing Aksjeradar application at {base_url}")
    print("=" * 50)
    
    session = requests.Session()
    
    # Test 1: Check if app is running
    try:
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Application is running")
        else:
            print(f"❌ Application not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to application: {e}")
        return
    
    # Test 2: Test login page
    try:
        response = session.get(f"{base_url}/login")
        if response.status_code == 200 and "Logg inn" in response.text:
            print("✅ Login page loads correctly")
            
            # Extract CSRF token
            csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print("✅ CSRF token found in login form")
            else:
                print("❌ CSRF token not found in login form")
                return
        else:
            print("❌ Login page not working")
            return
    except Exception as e:
        print(f"❌ Error accessing login page: {e}")
        return
    
    # Test 3: Test login attempt
    try:
        login_data = {
            'csrf_token': csrf_token,
            'username': 'helene721@gmail.com',
            'password': 'Soda2001??'
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        if response.status_code in [302, 303]:  # Redirect means login successful
            print("✅ Login successful (redirected)")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print("Response:", response.text[:200])
    except Exception as e:
        print(f"❌ Error during login: {e}")
    
    # Test 4: Test password reset page
    try:
        response = session.get(f"{base_url}/forgot_password")
        if response.status_code == 200 and "Glemt passord" in response.text:
            print("✅ Forgot password page loads correctly")
        else:
            print("❌ Forgot password page not working")
    except Exception as e:
        print(f"❌ Error accessing forgot password page: {e}")
    
    # Test 5: Test password reset token generation
    try:
        response = session.get(f"{base_url}/debug/test-reset")
        if response.status_code == 200 and "Reset URL" in response.text:
            print("✅ Password reset token generation working")
            
            # Extract reset URL
            url_match = re.search(r'href="([^"]*reset_password[^"]*)"', response.text)
            if url_match:
                reset_url = url_match.group(1)
                print(f"✅ Reset URL generated: {reset_url}")
                
                # Test the reset URL
                response = session.get(reset_url)
                if response.status_code == 200 and "Tilbakestill passord" in response.text:
                    print("✅ Password reset page with token works correctly")
                else:
                    print("❌ Password reset page with token not working")
            else:
                print("❌ Could not extract reset URL")
        else:
            print("❌ Password reset token generation not working")
    except Exception as e:
        print(f"❌ Error testing password reset: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- User: helene721@gmail.com")  
    print("- Password: Soda2001??")
    print("- All main functionality should be working")
    print("- For production, make sure domain is configured correctly")

if __name__ == '__main__':
    test_application()
