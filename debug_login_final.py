#!/usr/bin/env python3
"""
ENDELIG TEST: Database og Login Debugging
Test om login faktisk fungerer i browseren vs programmatisk
"""

import requests
import time

print("=== 🔍 DEBUGGING LOGIN ISSUE ===\n")

# Test 1: Sjekk at server responderer
print("1. Testing server response...")
try:
    r = requests.get('http://localhost:3000/', timeout=5)
    print(f"   ✅ Server responds: {r.status_code}")
except Exception as e:
    print(f"   ❌ Server error: {e}")
    exit(1)

print("\n2. Testing login page...")
try:
    r = requests.get('http://localhost:3000/login', timeout=5)
    print(f"   ✅ Login page: {r.status_code}")
    
    # Sjekk om siden faktisk har login form
    if 'csrf_token' in r.text:
        print("   ✅ CSRF token found in form")
    else:
        print("   ❌ No CSRF token found")
        
    if 'password' in r.text and 'email' in r.text:
        print("   ✅ Login form fields found")
    else:
        print("   ❌ Login form fields missing")
        
except Exception as e:
    print(f"   ❌ Login page error: {e}")

print("\n3. Database direct test...")
try:
    import sqlite3
    conn = sqlite3.connect('/workspaces/aksjeny/instance/app.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT email, password_hash FROM users WHERE email = 'helene721@gmail.com'")
    user = cursor.fetchone()
    
    if user:
        print(f"   ✅ User found in database: {user[0]}")
        print(f"   ✅ Password hash exists: {len(user[1])} chars")
        
        # Test password
        from werkzeug.security import check_password_hash
        if check_password_hash(user[1], 'test123'):
            print("   ✅ Password 'test123' is correct")
        else:
            print("   ❌ Password 'test123' is wrong")
    else:
        print("   ❌ User not found in database")
        
    conn.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")

print("\n=== 🎯 MULIG ÅRSAKER TIL LOGIN PROBLEM ===")
print("1. CSRF token validation feiler")
print("2. Form validation feiler (required fields)")
print("3. Session handling problemer")  
print("4. Flask config problemer")
print("\n💡 ANBEFALING: Test login i browser først!")
print("   http://localhost:3000/login")
print("   Email: helene721@gmail.com")
print("   Password: test123")
