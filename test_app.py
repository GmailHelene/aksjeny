#!/usr/bin/env python3
"""
Test script to verify the app can be imported and created
"""
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

try:
    print("Testing app import...")
    from app import create_app
    
    print("Creating app...")
    app = create_app('production')
    
    print("✅ App created successfully!")
    print(f"App name: {app.name}")
    print(f"Debug mode: {app.debug}")
    
    # Test if app can handle a simple route
    with app.test_client() as client:
        response = client.get('/')
        print(f"✅ Root route test: Status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
