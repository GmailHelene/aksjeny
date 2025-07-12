#!/usr/bin/env python3
"""
Manual debug of app creation to find where it's hanging
"""
import os
import sys
import traceback

# Add the app directory to the Python path
sys.path.insert(0, '/workspaces/aksjeradarv6')

print("Starting debug...")

try:
    print("Step 1: Basic imports")
    import flask
    print("✅ Flask imported")
    
    print("Step 2: Import app module")
    import app
    print("✅ App module imported")
    
    print("Step 3: Import create_app function")
    from app import create_app
    print("✅ create_app imported")
    
    print("Step 4: Create app instance")
    app_instance = create_app()
    print("✅ App instance created")
    
    print("Step 5: Test basic functionality")
    with app_instance.app_context():
        print(f"✅ App context works, {len(list(app_instance.url_map.iter_rules()))} routes found")
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error at step: {e}")
    traceback.print_exc()
