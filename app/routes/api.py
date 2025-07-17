import math
import logging
import random
from flask import Blueprint, jsonify, request, current_app, render_template
from flask_login import login_required, current_user
from ..services.data_service import DataService
from ..services.ai_service import AIService
from ..services.yahoo_finance_service import YahooFinanceService
from ..services.portfolio_service import get_ai_analysis
from ..utils.access_control import access_required, api_access_required, api_login_required
from ..models.user import User
from ..models.portfolio import Portfolio, PortfolioStock
from datetime import datetime, timedelta
import traceback

api = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api.route('/crypto/trending')
def get_crypto_trending():
    """API endpoint for trending crypto"""
    try:
        # Return mock trending crypto data
        trending_crypto = [
            {
                'symbol': 'BTC-USD',
                'name': 'Bitcoin',
                'price': 65432.10,
                'change': 1234.56,
                'change_percent': 1.93,
                'volume': 25000000000,
                'market_cap': 1280000000000
            },
            {
                'symbol': 'ETH-USD',
                'name': 'Ethereum',
                'price': 3456.78,
                'change': 67.89,
                'change_percent': 2.01,
                'volume': 15000000000,
                'market_cap': 415000000000
            }
        ]
        return jsonify({
            'success': True,
            'data': trending_crypto,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching trending crypto: {e}")
        return jsonify({'error': 'Failed to fetch trending crypto'}), 500

@api.route('/crypto/data')
def get_crypto_data():
    """API endpoint for detailed crypto data"""
    try:
        data = DataService.get_crypto_overview()
        return jsonify({
            'success': True,
            'data': data,
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
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching currency rates: {e}")
        return jsonify({'error': 'Failed to fetch currency rates'}), 500

@api.route('/dashboard/data')
def get_dashboard_data():
    """API endpoint for dashboard data"""
    try:
        # Aggregate data for dashboard
        dashboard_data = {
            'market_summary': {
                'osebx': {'value': 1234.56, 'change': 12.34, 'change_percent': 1.01},
                'sp500': {'value': 4567.89, 'change': -23.45, 'change_percent': -0.51},
                'nasdaq': {'value': 15678.90, 'change': 45.67, 'change_percent': 0.29}
            },
            'crypto_summary': {
                'bitcoin': {'value': 65432.10, 'change': 1234.56, 'change_percent': 1.93},
                'ethereum': {'value': 3456.78, 'change': 67.89, 'change_percent': 2.01}
            },
            'currency_summary': {
                'usdnok': {'value': 10.45, 'change': -0.15, 'change_percent': -1.42},
                'eurnok': {'value': 11.32, 'change': 0.08, 'change_percent': 0.71}
            }
        }
        return jsonify({
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500

@api.route('/financial/news')
def get_financial_news():
    """API endpoint for financial news"""
    try:
        financial_news = [
            {
                'id': 1,
                'title': 'Sentralbanken holder renten uendret',
                'summary': 'Norges Bank besluttet å holde styringsrenten på 4,5 prosent.',
                'content': 'I dagens rentemøte besluttet Norges Bank å holde styringsrenten uendret på 4,5 prosent...',
                'date': '2025-01-17',
                'category': 'monetary_policy',
                'source': 'Aksjeradar',
                'relevance_score': 95
            },
            {
                'id': 2,
                'title': 'Equinor med sterke kvartalstall',
                'summary': 'Equinor leverte bedre resultater enn ventet i fjerde kvartal.',
                'content': 'Equinor rapporterte et justert resultat på 6,2 milliarder dollar...',
                'date': '2025-01-16',
                'category': 'earnings',
                'source': 'Aksjeradar',
                'relevance_score': 88
            },
            {
                'id': 3,
                'title': 'Oslo Børs stiger på bred front',
                'summary': 'Hovedindeksen på Oslo Børs steg 1,2 prosent i dagens handel.',
                'content': 'OSEBX stengte opp 1,2 prosent til 1.234 poeng...',
                'date': '2025-01-15',
                'category': 'market_update',
                'source': 'Aksjeradar',
                'relevance_score': 82
            }
        ]
        
        return jsonify({
            'success': True,
            'data': financial_news,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching financial news: {e}")
        return jsonify({'error': 'Failed to fetch financial news'}), 500

@api.route('/economic/indicators')
def get_economic_indicators():
    """API endpoint for economic indicators"""
    try:
        indicators = {
            'norway': {
                'unemployment_rate': 3.2,
                'inflation_rate': 2.8,
                'gdp_growth': 1.4,
                'interest_rate': 4.5,
                'oil_fund_value': 15800000000000,
                'last_updated': '2025-01-15'
            },
            'global': {
                'us_unemployment': 3.7,
                'us_inflation': 2.1,
                'eu_inflation': 2.9,
                'china_gdp_growth': 5.2,
                'last_updated': '2025-01-15'
            },
            'market_indicators': {
                'vix': 18.5,
                'dollar_index': 103.2,
                'oil_price': 78.5,
                'gold_price': 2034.50,
                'last_updated': '2025-01-17'
            }
        }
        
        return jsonify({
            'success': True,
            'data': indicators,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching economic indicators: {e}")
        return jsonify({'error': 'Failed to fetch economic indicators'}), 500

@api.route('/market/sectors')
def get_market_sectors():
    """API endpoint for sector analysis"""
    try:
        sectors = {
            'energy': {
                'name': 'Energi',
                'performance_today': 2.1,
                'performance_week': 4.8,
                'performance_month': -1.2,
                'trend': 'bullish',
                'top_stocks': [
                    {'symbol': 'EQNR.OL', 'name': 'Equinor', 'change': 2.5},
                    {'symbol': 'AKA.OL', 'name': 'Aker ASA', 'change': 1.8}
                ]
            },
            'finance': {
                'name': 'Finans',
                'performance_today': 0.3,
                'performance_week': 1.2,
                'performance_month': 3.4,
                'trend': 'neutral',
                'top_stocks': [
                    {'symbol': 'DNB.OL', 'name': 'DNB Bank', 'change': 0.5},
                    {'symbol': 'NOR.OL', 'name': 'Nordea', 'change': 0.2}
                ]
            },
            'technology': {
                'name': 'Teknologi',
                'performance_today': -0.8,
                'performance_week': -2.1,
                'performance_month': 5.6,
                'trend': 'bearish',
                'top_stocks': [
                    {'symbol': 'AAPL', 'name': 'Apple', 'change': -1.2},
                    {'symbol': 'GOOGL', 'name': 'Alphabet', 'change': -0.5}
                ]
            },
            'healthcare': {
                'name': 'Helsevesen',
                'performance_today': 1.5,
                'performance_week': 2.8,
                'performance_month': 4.2,
                'trend': 'bullish',
                'top_stocks': [
                    {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'change': 1.8},
                    {'symbol': 'PFE', 'name': 'Pfizer', 'change': 1.2}
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'data': sectors,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching sector analysis: {e}")
        return jsonify({'error': 'Failed to fetch sector analysis'}), 500

@api.route('/insider/analysis/<symbol>')
def get_insider_analysis(symbol):
    """API endpoint for insider trading analysis"""
    try:
        # Return mock insider data
        insider_data = {
            'symbol': symbol.upper(),
            'recent_trades': [
                {
                    'date': '2025-01-15',
                    'insider': 'CEO John Doe',
                    'transaction': 'Buy',
                    'shares': 10000,
                    'price': 125.50
                },
                {
                    'date': '2025-01-10',
                    'insider': 'CFO Jane Smith',
                    'transaction': 'Sell',
                    'shares': 5000,
                    'price': 123.75
                }
            ],
            'sentiment': 'Positive',
            'score': 0.75
        }
        return jsonify({
            'success': True,
            'data': insider_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching insider analysis: {e}")
        return jsonify({'error': 'Failed to fetch insider analysis'}), 500

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
        # Return properly formatted currency data
        currency_data = {
            "EURNOK=X": {
                "change": 0.08,
                "change_percent": 0.71,
                "last_price": 11.32,
                "name": "EUR/NOK",
                "signal": "BUY",
                "ticker": "EURNOK=X",
                "volume": 1800000000
            },
            "USDNOK=X": {
                "change": -0.15,
                "change_percent": -1.42,
                "last_price": 10.45,
                "name": "USD/NOK",
                "signal": "HOLD",
                "ticker": "USDNOK=X",
                "volume": 2500000000
            },
            "GBPNOK=X": {
                "change": 0.05,
                "change_percent": 0.35,
                "last_price": 13.82,
                "name": "GBP/NOK",
                "signal": "BUY",
                "ticker": "GBPNOK=X",
                "volume": 850000000
            },
            "SEKUSD=X": {
                "change": -0.002,
                "change_percent": -0.18,
                "last_price": 0.095,
                "name": "SEK/USD",
                "signal": "HOLD",
                "ticker": "SEKUSD=X", 
                "volume": 650000000
            },
            "DKKUSD=X": {
                "change": 0.001,
                "change_percent": 0.08,
                "last_price": 0.145,
                "name": "DKK/USD",
                "signal": "HOLD",
                "ticker": "DKKUSD=X",
                "volume": 420000000
            }
        }
        
        return jsonify(currency_data)
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
@api_access_required
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
@api_access_required
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
@api_access_required
def get_stock_analysis(symbol):
    """Get AI analysis for a stock"""
    try:
        analysis = get_ai_analysis(symbol)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error getting analysis for {symbol}: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@api.route('/market/overview')
@api_access_required
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

@api.route('/market-data/realtime')
@api_access_required
def market_data_realtime():
    """API endpoint for realtime market data"""
    try:
        # Get realtime market data  
        data = {
            'oslo_realtime': DataService.get_oslo_stocks()[:3],
            'global_realtime': DataService.get_global_stocks()[:3],
            'crypto_realtime': DataService.get_crypto_data()[:2],
            'indices_realtime': DataService.get_global_indices(),
            'last_updated': datetime.utcnow().isoformat()
        }
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"Error fetching realtime market data: {str(e)}")
        return jsonify({'error': 'Failed to fetch realtime market data'}), 500

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

# Public API endpoints - no authentication required
@api.route('/public/market/data')
def get_public_market_data():
    """Get public market data for dashboard"""
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
                    'currency': 'USD'
                },
                {
                    'event': 'Norwegian GDP Release',
                    'time': '2025-07-18T08:00:00Z',
                    'impact': 'medium',
                    'currency': 'NOK'
                }
            ],
            'stocks': DataService.get_market_overview(),
            'crypto': DataService.get_crypto_overview(),
            'currencies': DataService.get_currency_overview()
        }
        
        return jsonify({
            'success': True,
            'dashboard_data': dashboard_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting public market data: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get market data'
        }), 500

@api.route('/public/economic/indicators')
def get_public_economic_indicators():
    """Get public economic indicators"""
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

@api.route('/public/market/sectors')
def get_public_sector_analysis():
    """Get public sector analysis"""
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
                'volume': 85000000
            },
            'finance': {
                'symbols': ['DNB.OL'],
                'performance': '+0.9%',
                'trend': 'neutral',
                'change': 0.9,
                'volume': 45000000
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

@api.route('/public/news/financial')
def get_public_financial_news():
    """Get public financial news"""
    try:
        symbols = request.args.getlist('symbols')
        sources = request.args.getlist('sources')
        limit = request.args.get('limit', 50, type=int)
        
        # For now, return demo news data
        news_articles = [
            {
                'id': 1,
                'title': 'Equinor rapporterer sterke Q2-resultater',
                'summary': 'Equinor overgår forventningene med økte oljeinntekter og reduserte kostnader.',
                'content': 'Equinor ASA rapporterte sterke resultater for andre kvartal...',
                'source': 'E24',
                'url': 'https://e24.no/equinor-q2-results',
                'published_at': '2025-07-14T08:00:00Z',
                'sentiment': 'positive',
                'symbols': ['EQNR.OL'],
                'category': 'earnings'
            },
            {
                'id': 2,
                'title': 'Norges Bank holder styringsrenten uendret',
                'summary': 'Sentralbanken holder renten på 4.50% som forventet av analytikere.',
                'content': 'Norges Bank besluttet å holde styringsrenten uendret...',
                'source': 'DN',
                'url': 'https://dn.no/norges-bank-rente',
                'published_at': '2025-07-14T10:00:00Z',
                'sentiment': 'neutral',
                'symbols': ['DNB.OL', 'EQNR.OL'],
                'category': 'monetary_policy'
            }
        ]
        
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

@api.route('/public/crypto/trending')
def get_public_crypto_trending():
    """Get public trending crypto data"""
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
            'trending_crypto': trending_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching trending crypto: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch trending crypto'}), 500

@api.route('/public/insider/analysis/<symbol>')
def get_public_insider_analysis(symbol):
    """Get public insider analysis for a symbol"""
    try:
        # Mock insider trading data
        insider_data = {
            'ticker': symbol.upper(),
            'insider_trades': [
                {
                    'date': '2025-07-10',
                    'insider': 'John Smith',
                    'title': 'CEO',
                    'transaction': 'Purchase',
                    'shares': 10000,
                    'price': 156.50,
                    'value': 1565000
                },
                {
                    'date': '2025-07-08',
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
        logger.error(f"Error fetching insider analysis for {symbol}: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch insider analysis'}), 500

@api.route('/public/market/comprehensive', methods=['POST'])
def get_public_market_comprehensive():
    """Get public comprehensive market data"""
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

@api.route('/public/crypto/data')
def get_public_crypto_data():
    """Get public crypto data"""
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
            'success': True,
            'crypto_data': formatted_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching crypto data: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch crypto data'}), 500

@api.route('/public/currency/rates')
def get_public_currency_rates():
    """Get public currency rates"""
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
            'success': True,
            'currency_rates': formatted_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching currency rates: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch currency rates'}), 500

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

@api.route('/stocks/<symbol>')
@api_access_required  
def get_stock_symbol_data(symbol):
    """Get detailed stock data for a specific symbol"""
    try:
        stock_data = DataService.get_stock_info(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
        
        return jsonify({
            'success': True,
            'data': stock_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return jsonify({'error': 'Failed to fetch stock data'}), 500

@api.route('/stocks/<symbol>/history')
@api_access_required
def get_stock_history(symbol):
    """Get historical data for a specific stock"""
    try:
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        history_data = DataService.get_stock_data(symbol, period=period, interval=interval)
        if not history_data:
            return jsonify({'error': 'No historical data found'}), 404
            
        return jsonify({
            'success': True,
            'data': history_data,
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        return jsonify({'error': 'Failed to fetch historical data'}), 500

@api.route('/market/summary')
def market_summary():
    """API endpoint for market summary"""
    try:
        summary = {
            'oslo_bors': {
                'index': 'OSEBX',
                'value': 1345.67,
                'change': 12.34,
                'changePercent': 0.93,
                'volume': 2500000,
                'top_gainers': DataService.get_oslo_stocks()[:3],
                'top_losers': DataService.get_oslo_stocks()[3:6]
            },
            'global_markets': {
                'sp500': {
                    'value': 4567.89,
                    'change': 23.45,
                    'changePercent': 0.52
                },
                'nasdaq': {
                    'value': 15678.90,
                    'change': -45.67,
                    'changePercent': -0.29
                },
                'dow': {
                    'value': 35123.45,
                    'change': 78.90,
                    'changePercent': 0.23
                }
            },
            'crypto_summary': {
                'total_market_cap': 2350000000000,
                'btc_dominance': 42.5,
                'top_cryptos': DataService.get_crypto_data()[:3]
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        logger.error(f"Error fetching market summary: {e}")
        return jsonify({'error': 'Failed to fetch market summary'}), 500

@api.route('/news')
def get_news():
    """API endpoint for general news"""
    try:
        news_data = DataService.get_general_news()
        return jsonify({
            'success': True,
            'data': news_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return jsonify({'error': 'Failed to fetch news'}), 500