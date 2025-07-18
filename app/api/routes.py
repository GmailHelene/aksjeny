from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user
from functools import wraps
import time
from datetime import datetime, timedelta
import redis
import json
from ..services.stock_service import StockService
from ..services.news_service import NewsService
from ..utils.cache import cache_manager
from ..utils.rate_limiter import rate_limit

api = Blueprint('api', __name__, url_prefix='/api')

# Rate limiting decorator
def api_rate_limit(max_requests=60, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not rate_limit(request.remote_addr, max_requests, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window} seconds'
                }), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@api.route('/stocks/quick-prices')
@api_rate_limit(max_requests=120, window=60)
def get_quick_prices():
    """Optimized endpoint for quick price updates on homepage"""
    try:
        tickers = request.args.get('tickers', '').split(',')
        tickers = [t.strip() for t in tickers if t.strip()]
        
        if not tickers:
            return jsonify({'error': 'No tickers provided'}), 400
            
        if len(tickers) > 10:
            return jsonify({'error': 'Too many tickers requested'}), 400
            
        # Mock data for now - replace with actual data service
        results = {}
        for ticker in tickers:
            results[ticker] = {
                'price': 100.0 + hash(ticker) % 500,
                'change_percent': (hash(ticker) % 200 - 100) / 10,
                'change': (hash(ticker) % 50 - 25) / 10,
                'volume': hash(ticker) % 10000000,
                'market_state': 'OPEN'
            }
                
        return jsonify({
            'success': True,
            'data': results,
            'cached': False,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Quick prices API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/homepage/market-data')
@api_rate_limit(max_requests=30, window=60)
def get_homepage_market_data():
    """Optimized endpoint for homepage market overview tables"""
    try:
        oslo_tickers = ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'NHY.OL', 'YAR.OL']
        global_tickers = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN']
        
        oslo_data = []
        global_data = []
        
        # Generate mock data
        for ticker in oslo_tickers:
            oslo_data.append({
                'ticker': ticker,
                'name': get_company_name(ticker),
                'price': 200.0 + hash(ticker) % 300,
                'change_percent': (hash(ticker) % 100 - 50) / 10,
                'currency': 'NOK',
                'signal': generate_mock_signal({'regularMarketChangePercent': (hash(ticker) % 100 - 50) / 10})
            })
        
        for ticker in global_tickers:
            global_data.append({
                'ticker': ticker,
                'name': get_company_name(ticker),
                'price': 100.0 + hash(ticker) % 200,
                'change_percent': (hash(ticker) % 80 - 40) / 10,
                'currency': 'USD',
                'signal': generate_mock_signal({'regularMarketChangePercent': (hash(ticker) % 80 - 40) / 10})
            })
        
        result = {
            'oslo': oslo_data,
            'global': global_data,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': result,
            'cached': False,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Homepage market data API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/news/latest')
@api_rate_limit(max_requests=20, window=60)
def get_latest_news():
    """Optimized endpoint for latest financial news"""
    try:
        limit = min(int(request.args.get('limit', 6)), 20)
        category = request.args.get('category', 'general')
        
        # Mock Norwegian financial news
        mock_articles = [
            {
                'title': 'Equinor rapporterer sterke kvartalstall',
                'summary': 'Norges største oljeselskap overgår forventningene med økt produksjon.',
                'description': 'Equinor leverte sterke resultater for andre kvartal...',
                'url': 'https://e24.no/equinor-kvartal',
                'source': 'E24',
                'published_at': datetime.now().isoformat(),
                'sentiment': 'positive',
                'relevance_score': 0.9
            },
            {
                'title': 'Oslo Børs åpner med oppgang',
                'summary': 'Hovedindeksen starter uken positivt med støtte fra energisektoren.',
                'description': 'Oslo Børs åpnet med bred oppgang mandag morgen...',
                'url': 'https://finansavisen.no/oslo-bors-oppgang',
                'source': 'Finansavisen',
                'published_at': datetime.now().isoformat(),
                'sentiment': 'positive',
                'relevance_score': 0.8
            },
            {
                'title': 'Fed holder rentene uendret',
                'summary': 'Den amerikanske sentralbanken opprettholder renten som ventet.',
                'description': 'Federal Reserve besluttet å holde federal funds rate uendret...',
                'url': 'https://reuters.com/fed-rates',
                'source': 'Reuters',
                'published_at': datetime.now().isoformat(),
                'sentiment': 'neutral',
                'relevance_score': 0.7
            }
        ]
        
        return jsonify({
            'success': True,
            'articles': mock_articles[:limit],
            'cached': False,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Latest news API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/market/status')
@api_rate_limit(max_requests=30, window=60)
def get_market_status():
    """Get current market status for Oslo Børs and NYSE"""
    try:
        now = datetime.now()
        oslo_hour = now.hour
        oslo_minute = now.minute
        oslo_weekday = now.weekday()
        
        oslo_open = (
            oslo_weekday < 5 and
            ((oslo_hour > 9) or (oslo_hour == 9 and oslo_minute >= 0)) and
            ((oslo_hour < 16) or (oslo_hour == 16 and oslo_minute <= 30))
        )
        
        nyse_open = (
            oslo_weekday < 5 and
            ((oslo_hour > 15) or (oslo_hour == 15 and oslo_minute >= 30)) and
            (oslo_hour < 22)
        )
        
        result = {
            'oslo': {
                'open': oslo_open,
                'name': 'Oslo Børs',
                'timezone': 'Europe/Oslo',
                'hours': '09:00-16:30 CET/CEST'
            },
            'nyse': {
                'open': nyse_open,
                'name': 'NYSE',
                'timezone': 'America/New_York',
                'hours': '09:30-16:00 ET (15:30-22:00 Oslo)'
            },
            'current_time': now.isoformat(),
            'oslo_time': now.strftime('%H:%M')
        }
        
        return jsonify({
            'success': True,
            'data': result,
            'cached': False,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Market status API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/crypto/trending')
@api_rate_limit(max_requests=20, window=60)
def get_trending_crypto():
    """Get trending cryptocurrencies"""
    try:
        trending_cryptos = [
            {
                'symbol': 'BTC-USD',
                'name': 'Bitcoin',
                'price': 65432.10,
                'change_percent': 2.5,
                'volume': 25000000000,
                'market_cap': 1200000000000
            },
            {
                'symbol': 'ETH-USD',
                'name': 'Ethereum',
                'price': 3456.78,
                'change_percent': 1.8,
                'volume': 15000000000,
                'market_cap': 400000000000
            },
            {
                'symbol': 'ADA-USD',
                'name': 'Cardano',
                'price': 0.485,
                'change_percent': 3.2,
                'volume': 750000000,
                'market_cap': 15000000000
            }
        ]
        
        return jsonify({
            'success': True,
            'trending_crypto': trending_cryptos,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Trending crypto API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/economic/indicators')
@api_rate_limit(max_requests=10, window=60)
def get_economic_indicators():
    """Get key economic indicators"""
    try:
        indicators = {
            'norway': {
                'inflation_rate': 2.8,
                'unemployment_rate': 3.4,
                'interest_rate': 4.5,
                'gdp_growth': 2.1,
                'oil_price_brent': 85.4
            },
            'global': {
                'us_inflation': 3.2,
                'us_unemployment': 3.8,
                'fed_rate': 5.25,
                'eur_usd': 1.08,
                'gold_price': 2015.5
            },
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'indicators': indicators,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Economic indicators API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/market/sectors')
@api_rate_limit(max_requests=20, window=60)
def get_sector_analysis():
    """Get sector-wise market analysis"""
    try:
        sectors = [
            {
                'name': 'Energi',
                'performance': 2.5,
                'volume': 15000000000,
                'top_stocks': ['EQNR.OL', 'AKERBP.OL'],
                'sentiment': 'positive'
            },
            {
                'name': 'Teknologi',
                'performance': 1.8,
                'volume': 8000000000,
                'top_stocks': ['AAPL', 'GOOGL', 'MSFT'],
                'sentiment': 'positive'
            },
            {
                'name': 'Finans',
                'performance': -0.5,
                'volume': 6000000000,
                'top_stocks': ['DNB.OL', 'JPM'],
                'sentiment': 'neutral'
            }
        ]
        
        return jsonify({
            'success': True,
            'sectors': sectors,
            'timestamp': time.time()
        })
        
    except Exception as e:
        current_app.logger.error(f"Sector analysis API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/currency')
def get_currency_rates():
    """Get formatted currency rates"""
    try:
        currency_data = {
            'USDNOK=X': {
                'ticker': 'USDNOK=X',
                'name': 'USD/NOK',
                'last_price': 10.45,
                'change': -0.15,
                'change_percent': -1.42,
                'signal': 'HOLD',
                'volume': 2500000000
            },
            'EURNOK=X': {
                'ticker': 'EURNOK=X', 
                'name': 'EUR/NOK',
                'last_price': 11.32,
                'change': 0.08,
                'change_percent': 0.71,
                'signal': 'BUY',
                'volume': 1800000000
            }
        }
        
        return jsonify(currency_data)
        
    except Exception as e:
        current_app.logger.error(f"Currency API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@api.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@api.errorhandler(429)
def api_rate_limit_exceeded(error):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests, please try again later'
    }), 429
