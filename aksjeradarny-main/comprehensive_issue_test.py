#!/usr/bin/env python3
"""
Comprehensive fix for all identified issues:
1. Demo logic consistency
2. Navigation layout 
3. Trial banners for premium users
4. Timer popup on all pages
5. User functions for logged-in users
6. Security headers
7. Responsive classes
8. Language switching
9. News sources
"""

import subprocess
import time
import requests
from datetime import datetime

def test_demo_logic():
    """Test demo timer consistency"""
    print("\n=== Testing Demo Logic ===")
    
    session = requests.Session()
    
    # Test demo page
    response = session.get('http://localhost:5000/demo')
    print(f"Demo page status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        
        # Check for conflicting messages
        utlopt_count = content.lower().count('utløpt')
        timer_count = content.lower().count('demo-countdown')
        
        print(f"  'Utløpt' mentions: {utlopt_count}")
        print(f"  Timer elements: {timer_count}")
        
        if utlopt_count > 0 and timer_count > 0:
            print("  ❌ CONFLICT: Both 'expired' message AND countdown timer present")
        else:
            print("  ✅ Demo logic appears consistent")

def test_navigation_layout():
    """Test navigation layout and responsive elements"""
    print("\n=== Testing Navigation Layout ===")
    
    response = requests.get('http://localhost:5000/')
    if response.status_code == 200:
        content = response.text
        
        # Check for responsive classes
        has_d_none = 'd-none' in content
        has_d_md_block = 'd-md-block' in content
        
        print(f"  d-none class present: {'✅' if has_d_none else '❌'}")
        print(f"  d-md-block class present: {'✅' if has_d_md_block else '❌'}")
        
        # Check navigation structure
        has_login_btn = 'Logg inn' in content
        has_register_btn = 'Registrer deg' in content
        
        print(f"  Login button present: {'✅' if has_login_btn else '❌'}")
        print(f"  Register button present: {'✅' if has_register_btn else '❌'}")

def test_trial_banners():
    """Test that trial banners don't show for premium users"""
    print("\n=== Testing Trial Banners ===")
    
    # Would need authenticated session for full test
    response = requests.get('http://localhost:5000/')
    if response.status_code == 200:
        content = response.text
        
        # Check for trial-related messages
        trial_messages = [
            'prøveperiode er utløpt',
            'demo-tilgang er utløpt', 
            '15 minutter',
            'trial'
        ]
        
        found_messages = []
        for msg in trial_messages:
            if msg.lower() in content.lower():
                found_messages.append(msg)
        
        print(f"  Trial messages found: {found_messages}")

def test_security_headers():
    """Test security headers"""
    print("\n=== Testing Security Headers ===")
    
    response = requests.get('http://localhost:5000/')
    headers = response.headers
    
    security_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY', 
        'Content-Security-Policy': 'present',
        'X-XSS-Protection': '1; mode=block'
    }
    
    for header, expected in security_headers.items():
        if header in headers:
            print(f"  ✅ {header}: {headers[header]}")
        else:
            print(f"  ❌ {header}: Missing")

def main():
    """Run all tests"""
    print("🔍 RUNNING COMPREHENSIVE ISSUE TESTING")
    print("=" * 50)
    
    # Start Flask app
    print("Starting Flask app...")
    process = subprocess.Popen(
        ['python', 'app.py'],
        cwd='/workspaces/aksjeradarv6',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)
    
    try:
        test_demo_logic()
        test_navigation_layout()
        test_trial_banners()
        test_security_headers()
        
        print("\n" + "=" * 50)
        print("🎯 NEXT STEPS:")
        print("1. Fix demo logic consistency")
        print("2. Update navigation layout")
        print("3. Add security headers")
        print("4. Implement responsive classes")
        print("5. Fix language switching")
        print("6. Add more news sources")
        
    finally:
        print("\nStopping Flask app...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()
