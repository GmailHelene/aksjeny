#!/usr/bin/env python3
"""
Simple startup test to debug Railway deployment issues
"""

import sys
import os
import traceback

# Add the app directory to the Python path
sys.path.insert(0, '/app')

def test_basic_imports():
    """Test if basic imports work"""
    try:
        print("Testing basic imports...")
        import flask
        print(f"✅ Flask version: {flask.__version__}")
        
        import sqlalchemy
        print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
        
        print("✅ Basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        traceback.print_exc()
        return False

def test_app_creation():
    """Test if we can create the Flask app"""
    try:
        print("Testing app creation...")
        from app import create_app
        
        # Create app with production config
        config_name = os.getenv('FLASK_ENV', 'production')
        app = create_app(config_name)
        
        print(f"✅ App created successfully in {config_name} mode")
        
        # Test if we can access app context
        with app.app_context():
            print("✅ App context works")
            
        return app
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        traceback.print_exc()
        return None

def test_database_connection(app):
    """Test database connection"""
    try:
        print("Testing database connection...")
        with app.app_context():
            from app.extensions import db
            from sqlalchemy import text
            
            # Test basic database query
            result = db.session.execute(text('SELECT 1'))
            db.session.commit()
            
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

def test_health_endpoint(app):
    """Test health endpoint"""
    try:
        print("Testing health endpoint...")
        with app.test_client() as client:
            response = client.get('/health/ready')
            print(f"Health endpoint status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Health endpoint works")
                return True
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)}")
                return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main diagnostic function"""
    print("🔍 Railway Deployment Diagnostic Tool")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Basic imports
    if test_basic_imports():
        success_count += 1
    
    # Test 2: App creation
    app = test_app_creation()
    if app:
        success_count += 1
        
        # Test 3: Database connection
        if test_database_connection(app):
            success_count += 1
        
        # Test 4: Health endpoint
        if test_health_endpoint(app):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! The app should work in production.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
