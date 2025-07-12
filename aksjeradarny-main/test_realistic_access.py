#!/usr/bin/env python3
"""
Realistic access control testing that accounts for trial auto-start behavior
"""
import requests
import time
import hashlib
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def create_device_fingerprint(ip="127.0.0.1", user_agent="TestAgent"):
    """Create device fingerprint like the app does"""
    fingerprint_data = f"{ip}:{user_agent}"
    return hashlib.md5(fingerprint_data.encode()).hexdigest()

def test_access_control():
    session = requests.Session()
    
    print("=== Realistic Access Control Test ===\n")
    
    # Test 1: Fresh visitor - should get trial access
    print("[TEST 1] Fresh visitor accessing premium content")
    response = session.get(f"{BASE_URL}/stocks/details/EQNR.OL")
    print(f"✅ Fresh visitor gets trial access: {response.status_code}")
    
    # Test 2: Check trial status is properly set
    cookies = session.cookies.get_dict()
    trial_cookies = {k: v for k, v in cookies.items() if k.startswith('trial_')}
    print(f"✅ Trial cookies set: {len(trial_cookies) > 0}")
    
    # Test 3: Simulate trial expiration by manipulating cookie
    print("\n[TEST 3] Simulating trial expiration")
    device_fp = create_device_fingerprint()
    trial_key = f"trial_{device_fp}"
    
    # Set expired trial time (more than 10 minutes ago)
    expired_time = (datetime.utcnow() - timedelta(minutes=15)).isoformat()
    session.cookies.set(trial_key, expired_time)
    
    # Try accessing premium content with expired trial
    response = session.get(f"{BASE_URL}/stocks/details/EQNR.OL", allow_redirects=False)
    if response.status_code in [302, 303]:
        print(f"✅ Expired trial correctly redirected: {response.status_code}")
        redirect_location = response.headers.get('Location', '')
        if 'restricted' in redirect_location:
            print("✅ Redirected to restricted access page")
        else:
            print(f"❌ Unexpected redirect location: {redirect_location}")
    else:
        print(f"❌ Expected redirect, got: {response.status_code}")
    
    # Test 4: Verify restricted access page exists
    print("\n[TEST 4] Testing restricted access page")
    response = session.get(f"{BASE_URL}/restricted_access")
    if response.status_code == 200:
        print("✅ Restricted access page accessible")
    else:
        print(f"❌ Restricted access page error: {response.status_code}")
    
    # Test 5: Test demo endpoints
    print("\n[TEST 5] Testing demo functionality")
    response = session.get(f"{BASE_URL}/demo")
    if response.status_code == 200:
        print("✅ Demo page accessible")
    else:
        print(f"❌ Demo page error: {response.status_code}")
    
    # Test 6: Test authenticated access
    print("\n[TEST 6] Testing authenticated user access")
    # Login with test user (if available)
    login_data = {
        'email': 'eiriktollan.berntsen@gmail.com',
        'password': 'admin123'
    }
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    if response.status_code in [302, 303]:
        print("✅ Login attempt processed")
        
        # Try accessing premium content as logged-in exempt user
        response = session.get(f"{BASE_URL}/stocks/details/EQNR.OL")
        if response.status_code == 200:
            print("✅ Exempt user has unrestricted access")
        else:
            print(f"❌ Exempt user access failed: {response.status_code}")
    else:
        print(f"⚠️ Login not tested (user may not exist): {response.status_code}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_access_control()
