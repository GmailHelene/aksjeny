from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user
from functools import wraps
import time
from datetime import datetime, timedelta
import redis
import json
from ..services.stock_service import StockService
from ..services.news_service import NewsService
from ..utils.cache_manager import cache_manager
from ..utils.rate_limiter import rate_limit

api = Blueprint('api', __name__, url_prefix='/api')

# Helper functions
def get_company_name(ticker):
    """Get company name for ticker - mock implementation"""
    company_names = {
        'EQNR.OL': 'Equinor ASA',
        'DNB.OL': 'DNB Bank ASA',
        'TEL.OL': 'Telenor ASA',
        'NHY.OL': 'Norsk Hydro ASA',
        'YAR.OL': 'Yara International ASA',
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'TSLA': 'Tesla Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com Inc.'
    }
    return company_names.get(ticker, ticker.replace('.OL', ''))

def generate_mock_signal(data):
    """Generate mock trading signal based on change percent"""
    change_percent = data.get('regularMarketChangePercent', 0)
    if change_percent > 5:
        return {'signal': 'STRONG_BUY', 'confidence': 0.9}
    elif change_percent > 2:
        return {'signal': 'BUY', 'confidence': 0.7}
    elif change_percent < -5:
        return {'signal': 'STRONG_SELL', 'confidence': 0.9}
    elif change_percent < -2:
        return {'signal': 'SELL', 'confidence': 0.7}
    else:
        return {'signal': 'HOLD', 'confidence': 0.5}

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

# Insider Trading API endpoints
@api.route('/insider-trading/latest')
@api_rate_limit(max_requests=60, window=60)
def insider_trading_latest():
    """API endpoint for latest insider trading data"""
    try:
        from ..services.data_service import DataService
        from ..utils.access_control import _is_exempt_user, _has_active_subscription
        
        # Check access level - exempt users or subscribers get access
        has_access = _is_exempt_user() or _has_active_subscription()
        if not has_access:
            return jsonify({
                'error': 'Access denied',
                'message': 'Premium subscription required',
                'demo': True
            }), 403
        
        limit = request.args.get('limit', 25, type=int)
        insider_data = DataService.get_insider_trading_data() or []
        
        # Format for JSON response
        transactions = []
        for trade in insider_data[:limit]:
            # Handle both dict and InsiderTransaction objects
            if hasattr(trade, '__dict__'):  # InsiderTransaction object
                transactions.append({
                    'symbol': getattr(trade, 'symbol', 'N/A'),
                    'date': getattr(trade, 'transaction_date', 'N/A'),
                    'time': '12:45',  # Mock time
                    'person': getattr(trade, 'insider_name', 'Ukjent'),
                    'role': getattr(trade, 'title', 'Officer'),
                    'transaction_type': getattr(trade, 'transaction_type', 'KJØP'),
                    'quantity': getattr(trade, 'shares', 0),
                    'price': getattr(trade, 'price', 0),
                    'total_value': getattr(trade, 'value', 0)
                })
            else:  # Dict object
                transactions.append({
                    'symbol': trade.get('symbol', 'N/A'),
                    'date': trade.get('date', 'N/A'),
                    'time': '12:45',  # Mock time
                    'person': trade.get('person', 'Ukjent'),
                    'role': trade.get('role', 'Officer'),
                    'transaction_type': trade.get('transaction_type', 'KJØP'),
                    'quantity': trade.get('quantity', 0),
                    'price': trade.get('price', 0),
                    'total_value': trade.get('total_value', 0)
                })
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'count': len(transactions)
        })
    except Exception as e:
        current_app.logger.error(f"Error in insider trading API: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/insider-trading/trending')
@api_rate_limit(max_requests=30, window=60)
def insider_trading_trending():
    """Get trending insider trading stocks"""
    try:
        # Mock trending data - can be enhanced with real analysis
        trending = [
            {'symbol': 'EQNR', 'recent_activity': '12', 'trend': 'bullish'},
            {'symbol': 'TEL', 'recent_activity': '8', 'trend': 'bearish'},
            {'symbol': 'NOK', 'recent_activity': '6', 'trend': 'neutral'},
            {'symbol': 'DNB', 'recent_activity': '5', 'trend': 'bullish'},
            {'symbol': 'MOWI', 'recent_activity': '4', 'trend': 'neutral'},
            {'symbol': 'YAR', 'recent_activity': '3', 'trend': 'bullish'},
            {'symbol': 'SALM', 'recent_activity': '3', 'trend': 'bearish'},
            {'symbol': 'STL', 'recent_activity': '2', 'trend': 'neutral'}
        ]
        
        return jsonify({'success': True, 'trending': trending})
    except Exception as e:
        current_app.logger.error(f"Error in trending endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/insider-trading/export')
@api_rate_limit(max_requests=10, window=60)
def insider_trading_export():
    """Export insider trading data"""
    try:
        from ..utils.access_control import verify_demo_access
        
        if not verify_demo_access():
            return jsonify({
                'error': 'Access denied', 
                'message': 'Demo access required'
            }), 403
            
        # Mock export functionality
        return jsonify({
            'success': True,
            'download_url': '/downloads/insider_trading_export.csv',
            'message': 'Export ready for download'
        })
    except Exception as e:
        current_app.logger.error(f"Error in export endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api.route('/insider-trading/stats')
@api_rate_limit(max_requests=30, window=60)
def insider_trading_stats():
    """Get insider trading statistics"""
    try:
        # Mock statistics data
        stats = {
            'total_transactions': 2547,
            'buy_sell_ratio': 1.43,
            'average_transaction_value': 2500000,
            'most_active_stock': 'EQNR',
            'top_sectors': [
                {'sector': 'Oil & Gas', 'count': 45},
                {'sector': 'Telecommunications', 'count': 38},
                {'sector': 'Banking', 'count': 32}
            ]
        }
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        current_app.logger.error(f"Error in stats endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
