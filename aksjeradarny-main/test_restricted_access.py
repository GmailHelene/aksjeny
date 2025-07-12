#!/usr/bin/env python3
"""
Test that restricted users cannot access the main index page with stock tables.
"""

import requests
import sys
from datetime import datetime

def test_restricted_user_access():
    """Test that users with expired trial cannot access main index page"""
    
    print("Testing restricted user access to main page...")
    
    # Test local development server
    base_url = "http://localhost:5000"
    
    try:
        # Create a new session (simulating new user with no trial)
        session = requests.Session()
        
        # Clear any existing cookies
        session.cookies.clear()
        
        # Set cookies to simulate expired trial
        from datetime import datetime, timedelta
        import hashlib
        
        # Simulate device fingerprint
        fingerprint_data = "127.0.0.1:test-user-agent"
        device_fingerprint = hashlib.md5(fingerprint_data.encode()).hexdigest()
        trial_key = f"trial_{device_fingerprint}"
        
        # Set expired trial time (more than 15 minutes ago)
        expired_time = (datetime.utcnow() - timedelta(minutes=20)).isoformat()
        session.cookies.set(trial_key, expired_time)
        
        # Try to access main page
        print(f"Attempting to access {base_url}/")
        
        response = session.get(base_url + "/", allow_redirects=False)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Redirected to: {location}")
            
            if '/demo' in location:
                print("✅ SUCCESS: Restricted user correctly redirected to demo page")
                return True
            else:
                print(f"❌ FAILURE: Restricted user redirected to wrong page: {location}")
                return False
        elif response.status_code == 200:
            print("❌ FAILURE: Restricted user was allowed to access main page")
            print("Content preview:", response.text[:500])
            return False
        else:
            print(f"❌ UNEXPECTED: Got status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to local server. Make sure Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

def test_with_simple_request():
    """Test with a simple request without any cookies"""
    print("\nTesting fresh user (no cookies) access to main page...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(base_url + "/", allow_redirects=False)
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"Redirected to: {location}")
            
            if '/demo' in location:
                print("✅ SUCCESS: Fresh user correctly redirected to demo page")
                return True
            else:
                print(f"❌ FAILURE: Fresh user redirected to wrong page: {location}")
                return False
        elif response.status_code == 200:
            print("❌ FAILURE: Fresh user was allowed to access main page")
            return False
        else:
            print(f"❌ UNEXPECTED: Got status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to local server. Make sure Flask app is running on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING RESTRICTED ACCESS TO MAIN PAGE")
    print("=" * 60)
    
    # Test 1: User with expired trial
    test1_passed = test_restricted_user_access()
    
    # Test 2: Fresh user without any cookies
    test2_passed = test_with_simple_request()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Test 1 (Expired trial user): {'PASS' if test1_passed else 'FAIL'}")
    print(f"Test 2 (Fresh user): {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n✅ ALL TESTS PASSED: Restricted access is working correctly")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED: Restricted access needs fixing")
        sys.exit(1)
