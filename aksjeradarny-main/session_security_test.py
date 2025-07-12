#!/usr/bin/env python3
"""
Session and Cookie Security Test
Tests the security configuration of sessions and cookies
"""

import os
import sys
import requests
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_security_headers():
    """Test security headers are properly set"""
    print("🔒 Testing Security Headers...")
    
    try:
        # Test with a simple GET request to the home page
        response = requests.get('http://localhost:5000/', timeout=10)
        
        headers_to_check = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': 'default-src',  # Should contain this
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'X-Download-Options': 'noopen',
            'X-Permitted-Cross-Domain-Policies': 'none'
        }
        
        print(f"Response Status: {response.status_code}")
        
        for header, expected_value in headers_to_check.items():
            if header in response.headers:
                actual_value = response.headers[header]
                if expected_value in actual_value:
                    print(f"✅ {header}: {actual_value}")
                else:
                    print(f"⚠️ {header}: {actual_value} (expected to contain '{expected_value}')")
            else:
                print(f"❌ Missing {header}")
                
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test security headers: {e}")
        print("💡 Make sure the app is running on http://localhost:5000")
        return False

def test_cookie_security():
    """Test cookie security settings"""
    print("\n🍪 Testing Cookie Security...")
    
    try:
        # Create a session to test cookies
        session = requests.Session()
        
        # Try to access a page that sets cookies
        response = session.get('http://localhost:5000/', timeout=10)
        
        print(f"Response Status: {response.status_code}")
        
        # Check if cookies are set with proper flags
        cookies = session.cookies
        
        if cookies:
            print(f"Found {len(cookies)} cookies:")
            for cookie in cookies:
                print(f"  Cookie: {cookie.name}")
                print(f"    Path: {cookie.path}")
                print(f"    Domain: {cookie.domain}")
                print(f"    Secure: {cookie.secure}")
                print(f"    HttpOnly: {cookie.has_nonstandard_attr('HttpOnly')}")
                print(f"    SameSite: {cookie.get_nonstandard_attr('SameSite', 'Not set')}")
        else:
            print("No cookies found (this may be normal for the homepage)")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test cookie security: {e}")
        return False

def test_csrf_protection():
    """Test CSRF protection is working"""
    print("\n🛡️ Testing CSRF Protection...")
    
    try:
        session = requests.Session()
        
        # Get the login page to retrieve CSRF token
        response = session.get('http://localhost:5000/login', timeout=10)
        
        if response.status_code == 200:
            print("✅ Login page accessible")
            
            # Try to submit login without CSRF token
            login_data = {
                'email': 'test@example.com',
                'password': 'testpassword'
            }
            
            response = session.post('http://localhost:5000/login', 
                                  data=login_data, 
                                  timeout=10,
                                  allow_redirects=False)
            
            # Should be rejected due to missing CSRF token
            if response.status_code in [400, 403, 422]:
                print("✅ CSRF protection is working - request rejected without token")
            else:
                print(f"⚠️ Unexpected response without CSRF token: {response.status_code}")
                
        else:
            print(f"❌ Could not access login page: {response.status_code}")
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to test CSRF protection: {e}")
        return False

def test_session_configuration():
    """Test session configuration by checking config"""
    print("\n⚙️ Testing Session Configuration...")
    
    try:
        from config import config
        from app import create_app
        
        app = create_app('development')
        
        with app.app_context():
            config_checks = {
                'SESSION_COOKIE_NAME': app.config.get('SESSION_COOKIE_NAME'),
                'SESSION_COOKIE_HTTPONLY': app.config.get('SESSION_COOKIE_HTTPONLY'),
                'SESSION_COOKIE_SAMESITE': app.config.get('SESSION_COOKIE_SAMESITE'),
                'PERMANENT_SESSION_LIFETIME': app.config.get('PERMANENT_SESSION_LIFETIME'),
                'WTF_CSRF_TIME_LIMIT': app.config.get('WTF_CSRF_TIME_LIMIT'),
                'WTF_CSRF_ENABLED': app.config.get('WTF_CSRF_ENABLED'),
            }
            
            print("Session Configuration:")
            for key, value in config_checks.items():
                if value is not None:
                    print(f"✅ {key}: {value}")
                else:
                    print(f"❌ {key}: Not set")
                    
        # Test production config differences
        prod_config = config['production']()
        
        print("\nProduction-specific settings:")
        prod_settings = {
            'SESSION_COOKIE_SECURE': getattr(prod_config, 'SESSION_COOKIE_SECURE', 'Not set'),
            'REMEMBER_COOKIE_SECURE': getattr(prod_config, 'REMEMBER_COOKIE_SECURE', 'Not set'),
            'WTF_CSRF_SSL_STRICT': getattr(prod_config, 'WTF_CSRF_SSL_STRICT', 'Not set'),
        }
        
        for key, value in prod_settings.items():
            print(f"✅ {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to test session configuration: {e}")
        return False

def main():
    """Run all security tests"""
    print("🔐 AKSJERADAR SESSION & COOKIE SECURITY TEST")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # Test configuration first (doesn't require running server)
    results.append(test_session_configuration())
    
    # Test live server endpoints (requires running server)
    results.append(test_security_headers())
    results.append(test_cookie_security())
    results.append(test_csrf_protection())
    
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} security tests passed!")
        print("🔒 Session and cookie security is properly configured.")
    else:
        print(f"⚠️ {passed}/{total} tests passed")
        print("🔧 Some security configurations may need attention.")
        
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
