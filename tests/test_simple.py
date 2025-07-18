"""
Simple tests without any conftest.py dependencies
"""
import sys
import os
import unittest
from unittest.mock import patch, Mock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestBasicImports(unittest.TestCase):
    """Test basic imports work"""
    
    def test_config_import(self):
        """Test config can be imported"""
        try:
            from config import Config
            self.assertIsNotNone(Config)
        except ImportError as e:
            self.fail(f"Could not import Config: {e}")
    
    def test_app_import(self):
        """Test app can be imported"""
        try:
            from app import create_app
            self.assertIsNotNone(create_app)
        except ImportError as e:
            self.fail(f"Could not import create_app: {e}")

class TestAppCreation(unittest.TestCase):
    """Test app creation"""
    
    @patch('redis.Redis')
    def test_create_app(self, mock_redis):
        """Test app can be created"""
        try:
            from app import create_app
            from config import Config
            
            # Mock Redis to avoid connection issues
            mock_redis.return_value = Mock()
            
            class TestConfig(Config):
                TESTING = True
                SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
                SQLALCHEMY_TRACK_MODIFICATIONS = False
                WTF_CSRF_ENABLED = False
                SECRET_KEY = 'test-secret-key'
            
            app = create_app(TestConfig)
            self.assertIsNotNone(app)
            self.assertTrue(app.config['TESTING'])
            
        except Exception as e:
            self.fail(f"Could not create app: {e}")

class TestMath(unittest.TestCase):
    """Simple math tests to ensure testing works"""
    
    def test_addition(self):
        """Test basic math"""
        self.assertEqual(1 + 1, 2)
        self.assertEqual(2 + 3, 5)
    
    def test_string_operations(self):
        """Test string operations"""
        self.assertIn('test', 'testing')
        self.assertEqual('hello'.upper(), 'HELLO')

if __name__ == '__main__':
    unittest.main()
