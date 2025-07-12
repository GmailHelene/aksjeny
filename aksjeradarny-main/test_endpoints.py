from flask import Flask, render_template
from typing import Dict, Any
import pytest
import unittest
from app import create_app
from app.extensions import db

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error: Any) -> tuple[Dict[str, str], int]:
    return {"error": "Resource not found"}, 404


@app.route('/')
def root() -> None:
    return render_template('index.html')


@app.route('/test')
def test_endpoint() -> Dict[str, str]:
    return {'status': 'ok'}


@app.route('/health')
def health_check() -> Dict[str, str]:
    return {'status': 'healthy'}


@app.route('/version')
def version() -> Dict[str, str]:
    return {'version': '1.0.0'}


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


def test_basic_endpoint(client) -> None:
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}


def test_health_check(client) -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy'}


def test_version(client) -> None:
    response = client.get('/version')
    assert response.status_code == 200
    assert response.json == {'version': '1.0.0'}


def test_not_found(client) -> None:
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert response.json == {'error': 'Resource not found'}


def test_root_endpoint(client) -> None:
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the API' in response.data


class TestEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'healthy'})

    def test_market_overview(self):
        """Test the market overview endpoint"""
        response = self.client.get('/market-overview')
        self.assertEqual(response.status_code, 200)
        self.assertIn('market_data', response.json)

    def test_stock_details(self):
        """Test the stock details endpoint"""
        response = self.client.get('/stock/AAPL')
        self.assertEqual(response.status_code, 200)
        self.assertIn('stock_data', response.json)

    def test_export_csv(self):
        """Test the CSV export endpoint"""
        data = {'symbols': ['AAPL', 'MSFT']}
        response = self.client.post('/export/csv', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('filepath', response.json)

    def test_export_pdf(self):
        """Test the PDF export endpoint"""
        data = {'report_type': 'market_overview'}
        response = self.client.post('/export/pdf', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('filepath', response.json)

    def test_invalid_stock_symbol(self):
        """Test invalid stock symbol handling"""
        response = self.client.get('/stock/INVALID')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)

    def test_invalid_export_request(self):
        """Test invalid export request handling"""
        response = self.client.post('/export/csv', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_api_rate_limit(self):
        """Test API rate limiting"""
        for _ in range(100):  # Assuming rate limit is less than 100
            response = self.client.get('/stock/AAPL')
        self.assertEqual(response.status_code, 429)  # Too Many Requests

    def test_authentication_required(self):
        """Test endpoints requiring authentication"""
        response = self.client.get('/user/portfolio')
        self.assertEqual(response.status_code, 401)  # Unauthorized

    def test_invalid_http_method(self):
        """Test invalid HTTP method handling"""
        response = self.client.post('/market-overview')  # GET only endpoint
        self.assertEqual(response.status_code, 405)  # Method Not Allowed


def list_all_routes():
    """List all registered routes in the application"""
    app = create_app()

    routes = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        routes.append({
            'endpoint': rule.endpoint,
            'methods': methods,
            'path': str(rule)
        })

    # Sort by path
    routes.sort(key=lambda x: x['path'])

    print("\n=== ALL REGISTERED ENDPOINTS ===\n")
    print(f"{'Path':<50} {'Methods':<10} {'Endpoint'}")
    print("-" * 100)

    for route in routes:
        print(f"{route['path']:<50} {route['methods']:<10} {route['endpoint']}")

    print(f"\nTotal endpoints: {len(routes)}")

    # Group by blueprint
    blueprints = {}
    for route in routes:
        blueprint = route['endpoint'].split('.')[0] if '.' in route['endpoint'] else 'main'
        if blueprint not in blueprints:
            blueprints[blueprint] = []
        blueprints[blueprint].append(route)

    print("\n=== ENDPOINTS BY BLUEPRINT ===\n")
    for bp, bp_routes in blueprints.items():
        print(f"\n{bp.upper()} ({len(bp_routes)} endpoints):")
        for route in bp_routes:
            print(f"  {route['path']:<45} [{route['methods']}]")

if __name__ == '__main__':
    app.run(debug=True)
    list_all_routes()
