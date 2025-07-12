#!/usr/bin/env python3
"""
Test trial expiration by manually setting expired trial in session
"""
import requests
import hashlib
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_trial_expiration_manually():
    """Test trial expiration by manipulating session data"""
    print("=== Manual Trial Expiration Test ===\n")
    
    session = requests.Session()
    
    # First, start a trial by accessing any premium endpoint
    print("[STEP 1] Starting trial by accessing premium content...")
    response = session.get(f"{BASE_URL}/stocks/details/EQNR.OL")
    print(f"Initial access status: {response.status_code}")
    
    # Get the Flask session cookie
    flask_session_cookie = None
    for cookie in session.cookies:
        if cookie.name == 'session':
            flask_session_cookie = cookie.value
            break
    
    if flask_session_cookie:
        print("✅ Flask session cookie found")
    else:
        print("❌ No Flask session cookie found")
        return
    
    # Create device fingerprint for testing
    device_fp = hashlib.md5("127.0.0.1:python-requests/2.31.0".encode()).hexdigest()
    print(f"Device fingerprint: {device_fp[:8]}...")
    
    # Test accessing restricted_access page directly
    print("\n[STEP 2] Testing restricted access page...")
    response = session.get(f"{BASE_URL}/restricted_access")
    print(f"Restricted access page status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Restricted access page is accessible")
        # Check if page contains expected content
        if "prøveperiode" in response.text.lower() or "subscription" in response.text.lower():
            print("✅ Restricted access page contains expected content")
        else:
            print("⚠️ Restricted access page might be missing content")
    else:
        print(f"❌ Restricted access page failed: {response.status_code}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_trial_expiration_manually()
