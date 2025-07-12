
from flask import Blueprint, jsonify, request, current_app, render_template
from flask_login import login_required, current_user
from app.services.data_service import DataService
from app.services.ai_service import AIService
from app.services.yahoo_finance_service import YahooFinanceService
from app.services.portfolio_service import get_ai_analysis
from app.utils.access_control import access_required
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
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching currency overview: {e}")
        return jsonify({'error': 'Failed to fetch currency overview'}), 500

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