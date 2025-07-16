import math
from flask import Blueprint, jsonify, request, current_app, render_template
from flask_login import login_required, current_user
from ..services.data_service import DataService
from ..services.ai_service import AIService
from ..services.yahoo_finance_service import YahooFinanceService
from ..services.portfolio_service import get_ai_analysis
from ..utils.access_control import access_required
from ..models.user import User
from ..models.portfolio import Portfolio, PortfolioStock
from datetime import datetime, timedelta
import traceback
import logging

api = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api.route('/crypto')
def get_crypto():
    """API endpoint for crypto overview"""
    try:
        data = DataService.get_crypto_overview()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching crypto overview: {e}")
        return jsonify({'error': 'Failed to fetch crypto overview'}), 500

@api.route('/currency')
def get_currency():
    """API endpoint for currency overview"""
    try:
        data = DataService.get_currency_overview()
        
        # Ensure proper JSON response
        if not data:
            return jsonify({
                'error': 'No currency data available',
                'data': {}
            }), 204
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching currency overview: {e}")
        return jsonify({
            'error': 'Failed to fetch currency overview',
            'message': str(e)
        }), 500

@api.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api.route('/search')
@access_required
def search():
    """Search for stocks"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'results': []})
        
        results = YahooFinanceService.search_stocks(query)
        return jsonify({'results': results})
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed', 'results': []}), 500

@api.route('/stocks/search')
def search_stocks():
    """API endpoint for stock search"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    try:
        # Search for stocks using Yahoo Finance service
        results = YahooFinanceService.search_stocks(query)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        logger.error(f"Error searching stocks: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@api.route('/stock/<symbol>')
@access_required
def get_stock_data(symbol):
    """Get stock data for a specific symbol"""
    try:
        stock_data = DataService.get_stock_info(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
        
        return jsonify(stock_data)
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return jsonify({'error': 'Failed to fetch stock data'}), 500

@api.route('/stock/<symbol>/price')
@access_required
def get_stock_price(symbol):
    """Get current price for a stock"""
    try:
        price_data = DataService.get_stock_price(symbol)
        if not price_data:
            return jsonify({'error': 'Price data not available'}), 404
        
        return jsonify(price_data)
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return jsonify({'error': 'Failed to fetch price data'}), 500

@api.route('/stock/<symbol>/analysis')
@access_required
def get_stock_analysis(symbol):
    """Get AI analysis for a stock"""
    try:
        analysis = get_ai_analysis(symbol)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error getting analysis for {symbol}: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@api.route('/market/overview')
@access_required
def market_overview():
    """Get market overview data"""
    try:
        overview = {
            'oslo_stocks': DataService.get_oslo_bors_overview(),
            'global_stocks': DataService.get_global_stocks_overview(),
            'crypto': DataService.get_crypto_overview(),
            'currency': DataService.get_currency_overview(),
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(overview)
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        return jsonify({'error': 'Failed to fetch market overview'}), 500

@api.route('/market-data')
def market_data():
    """API endpoint for market data"""
    try:
        # Get market overview data
        data = {
            'oslo': DataService.get_oslo_stocks()[:5],
            'global': DataService.get_global_stocks()[:5],
            'crypto': DataService.get_crypto_data()[:3],
            'indices': DataService.get_global_indices()
        }
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Error fetching market data: {str(e)}")
        return jsonify({'error': 'Failed to fetch market data'}), 500

@api.route('/user/watchlist')
@login_required
def get_user_watchlist():
    """Get user's watchlist"""
    try:
        # Implementation would fetch from database
        watchlist = []  # Placeholder
        return jsonify({'watchlist': watchlist})
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        return jsonify({'error': 'Failed to fetch watchlist'}), 500

@api.route('/user/portfolio')
@login_required
def get_user_portfolio():
    """Get user's portfolio"""
    try:
        # Implementation would fetch from database
        portfolio = []  # Placeholder
        return jsonify({'portfolio': portfolio})
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        return jsonify({'error': 'Failed to fetch portfolio'}), 500

@api.route('/feedback', methods=['POST'])
@login_required
def feedback():
    """Motta tilbakemelding fra bruker"""
    data = request.get_json()
    text = data.get('feedback', '').strip()
    if not text or len(text) < 5:
        return jsonify({'success': False, 'error': 'Skriv en tilbakemelding på minst 5 tegn.'}), 400
    # Lagre til fil eller database, evt. send e-post
    try:
        with open('user_feedback.log', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} | {current_user.email}: {text}\n")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        return jsonify({'success': False, 'error': 'Kunne ikke lagre tilbakemelding.'}), 500

@api.route('/realtime/price/<ticker>')
def realtime_price(ticker):
    """Get real-time price for a ticker"""
    try:
        # Mock data for now - replace with actual data service
        import random
        price_data = {
            'ticker': ticker,
            'price': round(random.uniform(50, 500), 2),
            'change': round(random.uniform(-10, 10), 2),
            'change_percent': round(random.uniform(-5, 5), 2),
            'volume': random.randint(100000, 10000000),
            'timestamp': datetime.utcnow().isoformat()
        }
        return jsonify(price_data)
    except Exception as e:
        current_app.logger.error(f"Error getting realtime price for {ticker}: {e}")
        return jsonify({'error': 'Could not fetch price data'}), 500

@api.route('/realtime/batch-updates', methods=['POST'])
def realtime_batch_updates():
    """Get batch updates for multiple tickers"""
    try:
        data = request.get_json() or {}
        tickers = data.get('tickers', [])
        
        if not tickers:
            return jsonify({'error': 'No tickers provided'}), 400
        
        # Mock updates
        import random
        updates = {}
        for ticker in tickers[:20]:  # Limit to 20 tickers
            updates[ticker] = {
                'price': round(random.uniform(50, 500), 2),
                'change': round(random.uniform(-10, 10), 2),
                'change_percent': round(random.uniform(-5, 5), 2),
                'volume': random.randint(100000, 10000000)
            }
        
        return jsonify({
            'success': True,
            'updates': updates,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error in batch updates: {e}")
        return jsonify({'error': 'Could not process batch update'}), 500

@api.route('/market/sectors')
def get_sector_analysis():
    """Get sector-wise market analysis"""
    try:
        # Sector data would be calculated from individual stocks
        sector_data = {
            'technology': {
                'symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
                'performance': '+2.3%',
                'trend': 'bullish',
                'change': 2.3,
                'volume': 125000000
            },
            'energy': {
                'symbols': ['EQNR.OL', 'AKERBP.OL'],
                'performance': '+1.8%',
                'trend': 'bullish',
                'change': 1.8,
                'volume': 45000000
            },
            'finance': {
                'symbols': ['DNB.OL'],
                'performance': '+0.9%',
                'trend': 'neutral',
                'change': 0.9,
                'volume': 30000000
            },
            'telecommunications': {
                'symbols': ['TEL.OL'],
                'performance': '-0.5%',
                'trend': 'bearish',
                'change': -0.5,
                'volume': 20000000
            },
            'healthcare': {
                'symbols': ['JNJ', 'PFE'],
                'performance': '+1.2%',
                'trend': 'bullish',
                'change': 1.2,
                'volume': 85000000
            },
            'consumer_goods': {
                'symbols': ['PG', 'KO'],
                'performance': '+0.6%',
                'trend': 'neutral',
                'change': 0.6,
                'volume': 65000000
            }
        }
        
        return jsonify({
            'success': True,
            'sector_analysis': sector_data,
            'last_updated': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting sector analysis: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get sector analysis'
        }), 500

@api.route('/news/financial')
def get_financial_news_api():
    """Get financial news from multiple sources"""
    try:
        symbols = request.args.getlist('symbols')
        sources = request.args.getlist('sources')
        limit = request.args.get('limit', 50, type=int)
        
        # For now, return demo news data
        news_articles = [
            {
                'title': 'Marked stiger på positiv teknologi-utvikling',
                'summary': 'Teknologiaksjer opplevde sterk vekst i dag etter positive kvartalsrapporter',
                'sentiment': 'positive',
                'source': 'Finansavisen',
                'published_at': datetime.utcnow().isoformat(),
                'url': 'https://aksjeradar.trade/news/teknologi-marked-oppgang',
                'symbol': symbols[0] if symbols else 'AAPL'
            },
            {
                'title': 'Energisektoren under press',
                'summary': 'Olje- og gasspriser faller på grunn av global økonomisk usikkerhet',
                'sentiment': 'negative',
                'source': 'E24',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'url': 'https://aksjeradar.trade/news/energi-sektor-press',
                'symbol': 'EQNR.OL'
            },
            {
                'title': 'Sentralbanken holder renten uendret',
                'summary': 'Norges Bank besluttet å holde styringsrenten på dagens nivå',
                'sentiment': 'neutral',
                'source': 'DN',
                'published_at': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                'url': 'https://aksjeradar.trade/news/sentralbank-rente-beslutning',
                'symbol': 'DNB.OL'
            },
            {
                'title': 'Kryptovaluta marked volatilt',
                'summary': 'Bitcoin og andre kryptovalutaer opplever store svingninger',
                'sentiment': 'neutral',
                'source': 'CryptoNews',
                'published_at': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                'url': 'https://aksjeradar.trade/news/krypto-volatilitet',
                'symbol': 'BTC-USD'
            }
        ]
        
        # Filter by symbols if provided
        if symbols:
            filtered_news = [article for article in news_articles 
                           if any(symbol in article['symbol'] for symbol in symbols)]
            if filtered_news:
                news_articles = filtered_news
        
        # Limit results
        news_articles = news_articles[:limit]
        
        return jsonify({
            'success': True,
            'news': news_articles,
            'total': len(news_articles)
        })
        
    except Exception as e:
        logger.error(f"Error getting financial news: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get financial news'
        }), 500

@api.route('/economic/indicators')
def get_economic_indicators():
    """Get key economic indicators"""
    try:
        indicators = [
            {
                'indicator': 'Styringsrente',
                'value': '4.50',
                'unit': '%',
                'date': '2025-07-14',
                'source': 'Norges Bank',
                'change': '+0.25'
            },
            {
                'indicator': 'Inflasjon',
                'value': '3.2',
                'unit': '%',
                'date': '2025-06-30',
                'source': 'SSB',
                'change': '-0.1'
            },
            {
                'indicator': 'Arbeidsledighet',
                'value': '3.8',
                'unit': '%',
                'date': '2025-06-30',
                'source': 'NAV',
                'change': '+0.2'
            },
            {
                'indicator': 'BNP Vekst',
                'value': '2.1',
                'unit': '%',
                'date': '2025-Q2',
                'source': 'SSB',
                'change': '+0.3'
            },
            {
                'indicator': 'Oljepris (Brent)',
                'value': '82.50',
                'unit': ' USD/fat',
                'date': '2025-07-14',
                'source': 'Reuters',
                'change': '+1.20'
            }
        ]
        
        return jsonify({
            'success': True,
            'economic_indicators': indicators
        })
        
    except Exception as e:
        logger.error(f"Error getting economic indicators: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get economic indicators'
        }), 500

@api.route('/dashboard/data', methods=['GET'])
def get_dashboard_data():
    """Get aggregated data for dashboard display"""
    try:
        # Generate realistic demo dashboard data
        dashboard_data = {
            'portfolio_summary': {
                'total_value': 1250000,  # NOK
                'daily_change': 2.3,     # %
                'daily_change_value': 28750,  # NOK
                'stocks_count': 7,
                'sectors': {
                    'Technology': 45.2,
                    'Energy': 32.1,
                    'Finance': 22.7
                }
            },
            'market_indicators': {
                'vix': 18.5,
                'fear_greed_index': 68,
                'market_sentiment': 'bullish'
            },
            'top_gainers': [
                {'symbol': 'TSLA', 'change': 5.2, 'price': 245.30},
                {'symbol': 'NVDA', 'change': 3.8, 'price': 118.50},
                {'symbol': 'EQNR.OL', 'change': 2.1, 'price': 285.60}
            ],
            'top_losers': [
                {'symbol': 'META', 'change': -2.3, 'price': 485.20},
                {'symbol': 'DNB.OL', 'change': -1.1, 'price': 225.80}
            ],
            'economic_calendar': [
                {
                    'event': 'Federal Reserve Interest Rate Decision',
                    'time': '2025-07-16T14:00:00Z',
                    'impact': 'high',
                    'forecast': '5.25%'
                },
                {
                    'event': 'Norwegian GDP Release',
                    'time': '2025-07-17T08:00:00Z',
                    'impact': 'medium',
                    'forecast': '2.1%'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'dashboard_data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get dashboard data'
        }), 500

@api.route('/crypto/data')
def get_crypto_data():
    """API endpoint for detailed crypto data"""
    try:
        data = DataService.get_crypto_overview()
        if not data:
            return jsonify({'error': 'No crypto data available'}), 404
        
        # Format data for API response
        formatted_data = {}
        for ticker, crypto_info in data.items():
            # Handle both dict and object formats
            if isinstance(crypto_info, dict):
                formatted_data[ticker] = {
                    'ticker': ticker,
                    'last_price': float(crypto_info.get('last_price', 0)),
                    'change': float(crypto_info.get('change', 0)),
                    'change_percent': float(crypto_info.get('change_percent', 0)),
                    'volume': float(crypto_info.get('volume', 0)),
                    'market_cap': float(crypto_info.get('market_cap', 0)),
                    'signal': crypto_info.get('signal', 'HOLD')
                }
            else:
                formatted_data[ticker] = {
                    'ticker': ticker,
                    'last_price': float(crypto_info.last_price) if hasattr(crypto_info, 'last_price') and crypto_info.last_price else 0,
                    'change': float(crypto_info.change) if hasattr(crypto_info, 'change') and crypto_info.change else 0,
                    'change_percent': float(crypto_info.change_percent) if hasattr(crypto_info, 'change_percent') and crypto_info.change_percent else 0,
                    'volume': float(crypto_info.volume) if hasattr(crypto_info, 'volume') and crypto_info.volume else 0,
                    'market_cap': float(crypto_info.market_cap) if hasattr(crypto_info, 'market_cap') and crypto_info.market_cap else 0,
                    'signal': crypto_info.signal if hasattr(crypto_info, 'signal') else 'HOLD'
                }
        
        return jsonify({
            'status': 'success',
            'data': formatted_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching crypto data: {e}")
        return jsonify({'error': 'Failed to fetch crypto data'}), 500

@api.route('/currency/rates')
def get_currency_rates():
    """API endpoint for currency exchange rates"""
    try:
        data = DataService.get_currency_overview()
        if not data:
            return jsonify({'error': 'No currency data available'}), 404
        
        # Format data for API response
        formatted_data = {}
        for ticker, currency_info in data.items():
            # Handle both dict and object formats
            if isinstance(currency_info, dict):
                formatted_data[ticker] = {
                    'pair': ticker,
                    'rate': float(currency_info.get('rate', currency_info.get('last_price', 0))),
                    'change': float(currency_info.get('change', 0)),
                    'change_percent': float(currency_info.get('change_percent', 0)),
                    'bid': float(currency_info.get('bid', 0)),
                    'ask': float(currency_info.get('ask', 0)),
                    'volume': float(currency_info.get('volume', 0))
                }
            else:
                formatted_data[ticker] = {
                    'pair': ticker,
                    'rate': float(currency_info.last_price) if hasattr(currency_info, 'last_price') and currency_info.last_price else 0,
                    'change': float(currency_info.change) if hasattr(currency_info, 'change') and currency_info.change else 0,
                    'change_percent': float(currency_info.change_percent) if hasattr(currency_info, 'change_percent') and currency_info.change_percent else 0,
                    'bid': float(currency_info.bid) if hasattr(currency_info, 'bid') and currency_info.bid else 0,
                    'ask': float(currency_info.ask) if hasattr(currency_info, 'ask') and currency_info.ask else 0,
                    'volume': float(currency_info.volume) if hasattr(currency_info, 'volume') and currency_info.volume else 0
                }
        
        return jsonify({
            'status': 'success',
            'data': formatted_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching currency rates: {e}")
        return jsonify({'error': 'Failed to fetch currency rates'}), 500

@api.route('/insider/analysis')
def get_general_insider_analysis():
    """API endpoint for general insider trading analysis"""
    try:
        # Demo insider trading data
        insider_data = {
            'recent_transactions': [
                {
                    'ticker': 'EQNR.OL',
                    'company': 'Equinor ASA',
                    'insider_name': 'Anders Opedal',
                    'position': 'CEO',
                    'transaction_type': 'Buy',
                    'shares': 5000,
                    'price': 285.50,
                    'value': 1427500,
                    'date': '2025-07-10',
                    'sentiment': 'Bullish'
                },
                {
                    'ticker': 'DNB.OL', 
                    'company': 'DNB Bank ASA',
                    'insider_name': 'Kjerstin Braathen',
                    'position': 'CEO',
                    'transaction_type': 'Sell',
                    'shares': 2000,
                    'price': 195.25,
                    'value': 390500,
                    'date': '2025-07-08',
                    'sentiment': 'Neutral'
                },
                {
                    'ticker': 'TEL.OL',
                    'company': 'Telenor ASA',
                    'insider_name': 'Sigve Brekke',
                    'position': 'CEO',
                    'transaction_type': 'Buy',
                    'shares': 3000,
                    'price': 145.75,
                    'value': 437250,
                    'date': '2025-07-05',
                    'sentiment': 'Bullish'
                }
            ],
            'summary': {
                'total_transactions': 15,
                'buy_transactions': 9,
                'sell_transactions': 6,
                'net_sentiment': 'Bullish',
                'most_active_sector': 'Energy'
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': insider_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching insider analysis: {e}")
        return jsonify({'error': 'Failed to fetch insider analysis'}), 500

@api.route('/crypto/trending')
@access_required
def crypto_trending():
    """Get trending crypto currencies"""
    try:
        # Get trending crypto data
        trending_data = {
            'BTC-USD': {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'price': 65432.1,
                'change_percent': 1.87,
                'volume': 25000000000,
                'market_cap': 1200000000000,
                'trend_score': 95
            },
            'ETH-USD': {
                'name': 'Ethereum',
                'symbol': 'ETH',
                'price': 3456.78,
                'change_percent': 1.67,
                'volume': 15000000000,
                'market_cap': 400000000000,
                'trend_score': 88
            },
            'XRP-USD': {
                'name': 'Ripple',
                'symbol': 'XRP',
                'price': 0.632,
                'change_percent': 0.32,
                'volume': 2000000000,
                'market_cap': 35000000000,
                'trend_score': 72
            }
        }
        
        return jsonify({
            'success': True,
            'data': trending_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching trending crypto: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch trending crypto'}), 500

@api.route('/insider/analysis/<ticker>')
@access_required  
def insider_analysis(ticker):
    """Get insider trading analysis for a ticker"""
    try:
        # Mock insider trading data
        insider_data = {
            'ticker': ticker.upper(),
            'insider_trades': [
                {
                    'date': '2025-01-10',
                    'insider': 'John Smith',
                    'title': 'CEO',
                    'transaction': 'Purchase',
                    'shares': 10000,
                    'price': 156.50,
                    'value': 1565000
                },
                {
                    'date': '2025-01-08',
                    'insider': 'Jane Doe',
                    'title': 'CFO',
                    'transaction': 'Sale',
                    'shares': 5000,
                    'price': 158.20,
                    'value': 791000
                }
            ],
            'analysis': {
                'insider_sentiment': 'Positive',
                'recent_activity': 'Increased buying',
                'confidence_score': 7.5,
                'recommendation': 'Watch'
            }
        }
        
        return jsonify({
            'success': True,
            'data': insider_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching insider analysis for {ticker}: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch insider analysis'}), 500

@api.route('/market/comprehensive', methods=['POST'])
@access_required
def market_comprehensive():
    """Get comprehensive market data for multiple symbols"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        market_data = {}
        for symbol in symbols:
            # Get stock data using DataService
            stock_data = DataService.get_single_stock_data(symbol)
            if stock_data:
                market_data[symbol] = {
                    'name': stock_data.get('shortName', symbol),
                    'price': stock_data.get('last_price', 0),
                    'change': stock_data.get('change', 0),
                    'change_percent': stock_data.get('change_percent', 0),
                    'volume': stock_data.get('volume', 0),
                    'market_cap': stock_data.get('market_cap', 0)
                }
        
        return jsonify({
            'success': True,
            'market_data': market_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching comprehensive market data: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch market data'}), 500

@api.before_request
def before_api_request():
    """Ensure API requests are handled properly"""
    # Set JSON content type for API responses
    pass

@api.after_request
def after_api_request(response):
    """Ensure API responses have correct headers"""
    if response.content_type.startswith('text/html'):
        # If HTML is being returned from an API endpoint, convert to JSON error
        return jsonify({
            'success': False,
            'message': 'API endpoint error - authentication required',
            'redirect': '/login'
        }), 401
    return response

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint ikke funnet', 'message': 'API-endepunktet du prøver å nå eksisterer ikke'}), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Intern serverfeil', 'message': 'En uventet feil oppstod på serveren'}), 500

@api.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Ikke autorisert', 'message': 'Du må være innlogget for å bruke denne funksjonen'}), 401

@api.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Ingen tilgang', 'message': 'Du har ikke tilgang til denne ressursen'}), 403