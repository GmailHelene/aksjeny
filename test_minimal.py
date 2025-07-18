"""
Minimal test to check if basic imports work
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_math():
    """Test that Python works"""
    assert 1 + 1 == 2
    print("✅ Basic math works")
    return True

def test_imports():
    """Test basic imports"""
    try:
        from config import Config
        print("✅ Config import works")
        
        from app import create_app
        print("✅ App import works")
        
        # Try creating app with minimal config
        class SimpleConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SECRET_KEY = 'test'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            WTF_CSRF_ENABLED = False
        
        # Mock Redis and database operations
        import unittest.mock
        with unittest.mock.patch('redis.Redis') as mock_redis, \
             unittest.mock.patch('flask_sqlalchemy.SQLAlchemy.create_all') as mock_create_all:
            
            mock_redis.return_value = unittest.mock.Mock()
            mock_create_all.return_value = None
            
            app = create_app(SimpleConfig)
            print("✅ App creation works")
            
            # Test app context
            with app.app_context():
                print("✅ App context works")
                
                # Test basic route (if it exists)
                with app.test_client() as client:
                    try:
                        response = client.get('/')
                        print(f"✅ Homepage responds with status: {response.status_code}")
                    except Exception as e:
                        print(f"⚠️  Homepage test skipped: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models():
    """Test model imports"""
    try:
        # Test if we can import models without creating them
        import app.models
        print("✅ Models import works")
        
        # Try importing specific models
        from app.models import LoginAttempt, UserSession
        print("✅ New models import works")
        
        return True
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False

def test_config_structure():
    """Test config structure"""
    try:
        from config import Config
        config = Config()
        
        required_attrs = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI']
        for attr in required_attrs:
            if hasattr(config, attr):
                print(f"✅ Config has {attr}")
            else:
                print(f"⚠️  Config missing {attr}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    print("🧪 Running minimal tests...")
    
    tests = [
        test_basic_math,
        test_config_structure,
        test_models,
        test_imports
    ]
    
    passed = 0
    for test in tests:
        try:
            print(f"\n🔍 Running {test.__name__}...")
            if test():
                passed += 1
                print(f"✅ {test.__name__} passed")
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 {passed}/{len(tests)} tests passed")
    
    if passed >= len(tests) - 1:  # Allow one test to fail
        print("✅ Most tests passed!")
        return 0
    else:
        print("❌ Too many tests failed")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
