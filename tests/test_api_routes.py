import pytest
import json
from unittest.mock import patch, MagicMock
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

class TestAPIRoutes:
    @patch('app.services.stock_service.StockService.get_stock_data')
    def test_quick_prices_endpoint(self, mock_stock_data, client):
        """Test quick prices API endpoint"""
        # Mock stock data response
        mock_stock_data.return_value = {
            'regularMarketPrice': 100.50,
            'regularMarketChangePercent': 2.5,
            'regularMarketChange': 2.45,
            'regularMarketVolume': 1000000,
            'marketState': 'OPEN'
        }
        
        response = client.get('/api/stocks/quick-prices?tickers=AAPL,GOOGL')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'AAPL' in data['data']
    
    def test_quick_prices_no_tickers(self, client):
        """Test quick prices with no tickers"""
        response = client.get('/api/stocks/quick-prices')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'No tickers provided' in data['error']
    
    def test_quick_prices_too_many_tickers(self, client):
        """Test quick prices with too many tickers"""
        tickers = ','.join([f'STOCK{i}' for i in range(15)])
        response = client.get(f'/api/stocks/quick-prices?tickers={tickers}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Too many tickers requested' in data['error']
    
    @patch('app.services.stock_service.StockService.get_stock_data')
    def test_homepage_market_data(self, mock_stock_data, client):
        """Test homepage market data endpoint"""
        mock_stock_data.return_value = {
            'regularMarketPrice': 150.25,
            'regularMarketChangePercent': 1.5,
        }
        
        response = client.get('/api/homepage/market-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'oslo' in data['data']
        assert 'global' in data['data']
    
    @patch('app.services.news_service.NewsService.get_latest_news')
    def test_latest_news_endpoint(self, mock_news_service, client):
        """Test latest news API endpoint"""
        mock_news_service.return_value = [
            {
                'title': 'Test News',
                'description': 'Test Description',
                'url': 'https://example.com',
                'source': 'Test Source',
                'published_at': '2024-01-01T12:00:00Z',
                'sentiment': 'positive'
            }
        ]
        
        response = client.get('/api/news/latest?limit=3&category=norwegian')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['articles']) == 1
        assert data['articles'][0]['title'] == 'Test News'
    
    def test_market_status_endpoint(self, client):
        """Test market status endpoint"""
        response = client.get('/api/market/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'oslo' in data['data']
        assert 'nyse' in data['data']
        assert 'current_time' in data['data']

class TestAPIRateLimiting:
    def test_rate_limiting(self, client):
        """Test API rate limiting"""
        # Make multiple requests quickly
        for i in range(125):  # Exceed the rate limit
            response = client.get('/api/stocks/quick-prices?tickers=AAPL')
            if response.status_code == 429:
                break
        
        # Should eventually get rate limited
        assert response.status_code == 429
        data = json.loads(response.data)
        assert 'Rate limit exceeded' in data['error']

if __name__ == '__main__':
    pytest.main([__file__])
