#!/usr/bin/env python3
"""
Simple test runner without external dependencies
"""
import sys
import os

def test_imports():
    """Test basic imports"""
    print("🧪 Testing basic imports...")
    
    try:
        # Test config import
        from config import Config
        print("✅ Config import successful")
        
        # Test app creation
        from app import create_app
        print("✅ App import successful")
        
        # Test basic app creation
        app = create_app()
        print("✅ App creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic app functionality"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from app import create_app
        from config import Config
        
        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            WTF_CSRF_ENABLED = False
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            response = client.get('/')
            print(f"✅ Homepage request: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    print("🚀 Running simple tests for Aksjeradar\n")
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    tests_passed = 0
    total_tests = 2
    
    if test_imports():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All simple tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
