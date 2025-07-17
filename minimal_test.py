#!/usr/bin/env python3
"""
Minimal test to check if app works
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

try:
    print("Testing minimal Flask app import...")
    from app import create_app
    
    print("Creating Flask app...")
    app = create_app('testing')
    
    print("Testing with test client...")
    with app.test_client() as client:
        print("Testing /api/crypto/trending endpoint...")
        response = client.get('/api/crypto/trending')
        print(f"Status code: {response.status_code}")
        print(f"Response data: {response.data.decode()[:200]}")
        
        if response.status_code == 200:
            print("✅ API endpoint working!")
        else:
            print("❌ API endpoint failed")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
