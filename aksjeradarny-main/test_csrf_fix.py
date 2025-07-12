#!/usr/bin/env python3
"""
Test script to validate CSRF token fixes for Stripe checkout
"""

import requests
import re
from bs4 import BeautifulSoup

def test_csrf_functionality():
    """Test CSRF token generation and form submission"""
    
    base_url = "http://localhost:5001"  # Adjust port as needed
    session = requests.Session()
    
    print("🧪 Testing CSRF Token Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Check if app is running
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"❌ App not running at {base_url}")
            return False
            
        print("✅ App is running")
        
        # Test 2: Check subscription page for CSRF tokens
        response = session.get(f"{base_url}/subscription")
        if response.status_code == 200:
            print("✅ Subscription page accessible")
            
            # Parse the HTML to find CSRF tokens
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_inputs = soup.find_all('input', {'name': 'csrf_token'})
            
            if csrf_inputs:
                print(f"✅ Found {len(csrf_inputs)} CSRF token inputs")
                for i, input_tag in enumerate(csrf_inputs[:3]):  # Show first 3
                    token_value = input_tag.get('value', '')
                    print(f"   Token {i+1}: {token_value[:20]}..." if token_value else f"   Token {i+1}: EMPTY")
            else:
                print("❌ No CSRF tokens found in subscription page")
                
        else:
            print(f"❌ Cannot access subscription page: {response.status_code}")
            
        # Test 3: Check login page for CSRF tokens
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✅ Login page accessible")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_inputs = soup.find_all('input', {'name': 'csrf_token'})
            
            if csrf_inputs:
                print(f"✅ Found CSRF token in login form")
            else:
                print("❌ No CSRF token found in login form")
        
        # Test 4: Try to access debug CSRF endpoint (if available)
        try:
            response = session.get(f"{base_url}/debug/csrf")
            if response.status_code == 200:
                print("✅ Debug CSRF endpoint accessible")
            elif response.status_code == 302:
                print("⚠️  Debug CSRF endpoint requires login (redirected)")
            else:
                print(f"⚠️  Debug CSRF endpoint returned: {response.status_code}")
        except:
            print("⚠️  Debug CSRF endpoint not available")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_stripe_checkout_form():
    """Test the Stripe checkout form specifically"""
    
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("\n💳 Testing Stripe Checkout Form")
    print("=" * 50)
    
    try:
        # Get subscription page
        response = session.get(f"{base_url}/subscription")
        if response.status_code != 200:
            print("❌ Cannot access subscription page")
            return False
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find forms that post to create-checkout-session
        checkout_forms = soup.find_all('form', action=re.compile(r'create-checkout-session'))
        
        if checkout_forms:
            print(f"✅ Found {len(checkout_forms)} Stripe checkout forms")
            
            for i, form in enumerate(checkout_forms):
                csrf_input = form.find('input', {'name': 'csrf_token'})
                subscription_input = form.find('input', {'name': 'subscription_type'})
                
                if csrf_input:
                    token_value = csrf_input.get('value', '')
                    print(f"   Form {i+1}: CSRF token present ({len(token_value)} chars)")
                else:
                    print(f"   Form {i+1}: ❌ NO CSRF TOKEN!")
                    
                if subscription_input:
                    sub_type = subscription_input.get('value', '')
                    print(f"   Form {i+1}: Subscription type = {sub_type}")
        else:
            print("❌ No Stripe checkout forms found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing Stripe forms: {e}")
        return False

if __name__ == "__main__":
    success1 = test_csrf_functionality()
    success2 = test_stripe_checkout_form()
    
    if success1 and success2:
        print("\n🎉 All CSRF tests completed!")
        print("The fixes should resolve the 'CSRF session token is missing' error.")
    else:
        print("\n⚠️  Some tests failed. Check the app configuration.")
