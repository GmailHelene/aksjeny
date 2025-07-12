#!/usr/bin/env python3
"""
Test script to verify the crypto and currency endpoints are fixed
"""

import requests
import subprocess
import time
import json


def test_api_endpoints():
    """Test the fixed crypto and currency endpoints"""
    try:
        print("\n=== Testing Fixed API Endpoints ===")
        
        # Test crypto endpoint
        print("\nTesting /api/crypto endpoint...")
        response = requests.get('http://localhost:5000/api/crypto', timeout=10)
        print(f"Crypto API status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Crypto API working correctly")
            try:
                data = response.json()
                print(f"   Returned {len(data)} crypto items" if isinstance(data, dict) else "   Data returned")
            except json.JSONDecodeError:
                print("   Non-JSON response received")
        else:
            print(f"❌ Crypto API failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        
        # Test currency endpoint
        print("\nTesting /api/currency endpoint...")
        response = requests.get('http://localhost:5000/api/currency', timeout=10)
        print(f"Currency API status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Currency API working correctly")
            try:
                data = response.json()
                print(f"   Returned {len(data)} currency items" if isinstance(data, dict) else "   Data returned")
            except json.JSONDecodeError:
                print("   Non-JSON response received")
        else:
            print(f"❌ Currency API failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
        
        # Test the pricing page is still working
        print("\nTesting /pricing page...")
        response = requests.get('http://localhost:5000/pricing', timeout=10)
        print(f"Pricing page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Pricing page still working correctly")
            # Quick check for pricing values
            if 'kr199' in response.text.replace(' ', '') or 'kr 199' in response.text:
                print("✅ Pricing values displayed correctly")
        else:
            print(f"❌ Pricing page failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False

if __name__ == "__main__":
    test_api_endpoints()
