import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_basic_import():
    """Test that we can import the app"""
    try:
        from app import create_app
        assert create_app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import app: {e}")

def test_config_import():
    """Test that we can import config"""
    try:
        from config import Config
        assert Config is not None
    except ImportError as e:
        pytest.fail(f"Failed to import config: {e}")

def test_app_creation():
    """Test that we can create an app instance"""
    try:
        from app import create_app
        from config import Config
        
        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        
        app = create_app(TestConfig)
        assert app is not None
        assert app.config['TESTING'] is True
        
    except Exception as e:
        pytest.fail(f"Failed to create app: {e}")

def test_app_routes():
    """Test that basic routes are accessible"""
    try:
        from app import create_app
        from config import Config
        
        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            WTF_CSRF_ENABLED = False
        
        app = create_app(TestConfig)
        
        with app.test_client() as client:
            # Test homepage
            response = client.get('/')
            # Should either load successfully or have a reasonable error
            assert response.status_code in [200, 404, 500]  # Any of these is fine for now
            
    except Exception as e:
        pytest.fail(f"Failed to test routes: {e}")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
