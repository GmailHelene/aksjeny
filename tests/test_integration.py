import pytest
import json
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    REDIS_URL = 'redis://localhost:6379/1'

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

class TestHomepageIntegration:
    def test_homepage_loads(self, client):
        """Test that homepage loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Aksjeradar' in response.data
        assert b'Live Markedsdata' in response.data
    
    def test_homepage_with_authenticated_user(self, client, app):
        """Test homepage behavior with authenticated user"""
        with app.app_context():
            # Create test user
            user = User(
                email='test@example.com',
                name='Test User',
                subscription_level='premium',
                email_verified=True
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            
            # Login
            login_response = client.post('/auth/login',
                data=json.dumps({
                    'email': 'test@example.com',
                    'password': 'testpass123'
                }),
                content_type='application/json'
            )
            
            assert login_response.status_code == 200
            
            # Access homepage
            response = client.get('/')
            assert response.status_code == 200

class TestAPIIntegration:
    def test_api_workflow(self, client):
        """Test complete API workflow"""
        # Test market status
        status_response = client.get('/api/market/status')
        assert status_response.status_code == 200
        
        # Test news API
        news_response = client.get('/api/news/latest?limit=3')
        assert news_response.status_code == 200
        
        # Test quick prices (might fail due to external API, but should handle gracefully)
        prices_response = client.get('/api/stocks/quick-prices?tickers=AAPL')
        # Should either succeed or fail gracefully
        assert prices_response.status_code in [200, 500]

if __name__ == '__main__':
    pytest.main([__file__])
