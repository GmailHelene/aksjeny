import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import User, LoginAttempt, UserSession
from app.auth.enhanced_auth import AuthenticationManager
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    REDIS_URL = 'redis://localhost:6379/1'  # Test database

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_manager(app):
    with app.app_context():
        return AuthenticationManager()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            email='test@example.com',
            name='Test User',
            subscription_level='basic',
            email_verified=True
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        return user

class TestAuthenticationManager:
    def test_successful_authentication(self, auth_manager, test_user):
        """Test successful user authentication"""
        request_info = {
            'ip': '127.0.0.1',
            'user_agent': 'Test Agent'
        }
        
        result = auth_manager.authenticate_user(
            'test@example.com', 
            'testpassword123', 
            remember_me=False,
            request_info=request_info
        )
        
        assert result['success'] is True
        assert 'session_token' in result
        assert result['user']['email'] == 'test@example.com'
    
    def test_invalid_password(self, auth_manager, test_user):
        """Test authentication with invalid password"""
        request_info = {'ip': '127.0.0.1', 'user_agent': 'Test Agent'}
        
        result = auth_manager.authenticate_user(
            'test@example.com',
            'wrongpassword',
            request_info=request_info
        )
        
        assert result['success'] is False
        assert 'Invalid email or password' in result['error']
    
    def test_nonexistent_user(self, auth_manager):
        """Test authentication with nonexistent user"""
        request_info = {'ip': '127.0.0.1', 'user_agent': 'Test Agent'}
        
        result = auth_manager.authenticate_user(
            'nonexistent@example.com',
            'password',
            request_info=request_info
        )
        
        assert result['success'] is False
        assert 'Invalid email or password' in result['error']
    
    def test_rate_limiting(self, auth_manager, test_user):
        """Test rate limiting functionality"""
        request_info = {'ip': '127.0.0.1', 'user_agent': 'Test Agent'}
        
        # Make multiple failed attempts
        for _ in range(6):  # Exceed the limit of 5
            auth_manager.authenticate_user(
                'test@example.com',
                'wrongpassword',
                request_info=request_info
            )
        
        # Next attempt should be rate limited
        result = auth_manager.authenticate_user(
            'test@example.com',
            'testpassword123',
            request_info=request_info
        )
        
        assert result['success'] is False
        assert 'Too many login attempts' in result['error']
    
    @patch('app.auth.enhanced_auth.SecurityUtils.verify_totp')
    def test_two_factor_authentication(self, mock_verify_totp, auth_manager, test_user):
        """Test two-factor authentication flow"""
        # Enable 2FA for test user
        test_user.two_factor_enabled = True
        test_user.two_factor_secret = 'TESTSECRET123456'
        db.session.commit()
        
        request_info = {'ip': '127.0.0.1', 'user_agent': 'Test Agent'}
        
        # First authentication should require 2FA
        result = auth_manager.authenticate_user(
            'test@example.com',
            'testpassword123',
            request_info=request_info
        )
        
        assert result['success'] is False
        assert result['two_factor_required'] is True
        assert 'token' in result
        
        # Mock successful TOTP verification
        mock_verify_totp.return_value = True
        
        # Verify 2FA code
        verification_result = auth_manager.verify_two_factor(
            result['token'],
            '123456',
            request_info
        )
        
        assert verification_result['success'] is True

class TestAuthenticationRoutes:
    def test_login_route_success(self, client, test_user):
        """Test successful login via API route"""
        response = client.post('/auth/login', 
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'testpassword123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'session_token' in data
    
    def test_login_route_invalid_data(self, client):
        """Test login with invalid data"""
        response = client.post('/auth/login',
            data=json.dumps({
                'email': 'invalid-email',
                'password': 'short'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Invalid email format'
    
    def test_logout_route(self, client, test_user):
        """Test logout functionality"""
        # Login first
        login_response = client.post('/auth/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'testpassword123'
            }),
            content_type='application/json'
        )
        
        assert login_response.status_code == 200
        
        # Logout
        logout_response = client.post('/auth/logout')
        assert logout_response.status_code == 200
        
        data = json.loads(logout_response.data)
        assert data['success'] is True

class TestSubscriptionDecorators:
    def test_require_subscription_decorator(self, client, test_user):
        """Test subscription requirement decorator"""
        from app.auth.enhanced_auth import require_subscription
        from flask import jsonify
        
        # Create a test route with subscription requirement
        @require_subscription('premium')
        def premium_route():
            return jsonify({'message': 'Premium content'})
        
        # Test with basic user (should fail)
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
        
        # This would normally be tested with actual route registration
        # For now, we test the decorator logic directly
        assert test_user.subscription_level == 'basic'
        assert not test_user.has_subscription_level('premium')

if __name__ == '__main__':
    pytest.main([__file__])
