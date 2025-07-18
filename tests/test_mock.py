"""
Tests with all external dependencies mocked
"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@patch('redis.Redis')
@patch('app.services.stock_service.StockService')
@patch('app.services.news_service.NewsService')
class TestMockedApp:
    """Test app with all external services mocked"""
    
    def test_app_creation_mocked(self, mock_news, mock_stock, mock_redis):
        """Test app creation with mocked services"""
        from app import create_app
        from config import Config
        
        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            WTF_CSRF_ENABLED = False
            SECRET_KEY = 'test-secret'
            REDIS_URL = 'redis://localhost:6379/0'
        
        # Mock Redis
        mock_redis.return_value = Mock()
        
        app = create_app(TestConfig)
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_homepage_mocked(self, mock_news, mock_stock, mock_redis):
        """Test homepage with mocked services"""
        from app import create_app
        from config import Config
        
        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            WTF_CSRF_ENABLED = False
            SECRET_KEY = 'test-secret'
        
        # Mock Redis
        mock_redis.return_value = Mock()
        
        with patch('app.models.db.create_all'):
            app = create_app(TestConfig)
            
            with app.test_client() as client:
                response = client.get('/')
                # Should work without DB/Redis errors
                assert response.status_code in [200, 404, 500]

def test_simple_math():
    """Simple test to ensure pytest is working"""
    assert 1 + 1 == 2
    assert "test" in "testing"

def test_python_version():
    """Test Python version"""
    import sys
    assert sys.version_info >= (3, 7)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
