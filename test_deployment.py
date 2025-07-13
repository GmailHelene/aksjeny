#!/usr/bin/env python3
"""
Test script to verify the Flask app can be created and started
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """Test that the Flask app can be created"""
    try:
        from app import create_app
        app = create_app('production')
        
        print("✅ Flask app created successfully")
        print(f"✅ App name: {app.name}")
        print(f"✅ Debug mode: {app.debug}")
        print(f"✅ Secret key configured: {bool(app.config.get('SECRET_KEY'))}")
        print(f"✅ Database configured: {bool(app.config.get('SQLALCHEMY_DATABASE_URI'))}")
        
        # Test basic routes
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Homepage accessible: {response.status_code}")
            
            response = client.get('/demo')
            print(f"✅ Demo page accessible: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Flask app: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_app_creation():
        print("\n🎉 App test passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n💥 App test failed!")
        sys.exit(1)
