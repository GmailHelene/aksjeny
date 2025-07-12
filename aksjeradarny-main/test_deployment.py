#!/usr/bin/env python3
"""
Test deployment startup for Railway
"""
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """Test if the app can start up without errors"""
    try:
        print("🚀 Testing app startup...")
        
        # Test basic imports
        print("📦 Testing imports...")
        import app
        print("✅ App module imported successfully")
        
        from app import create_app
        print("✅ create_app function imported successfully")
        
        # Test app creation
        print("🏗️  Testing app creation...")
        app_instance = create_app('production')
        print("✅ App instance created successfully")
        
        # Test app context
        print("🔧 Testing app context...")
        with app_instance.app_context():
            from flask import current_app
            print(f"✅ App context working, app name: {current_app.name}")
        
        print("🎉 All tests passed! App should deploy successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Error during startup test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)
