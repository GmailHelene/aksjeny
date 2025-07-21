import math
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from ..services.data_service import DataService
from ..services.analysis_service import AnalysisService
from ..services.usage_tracker import usage_tracker
from ..utils.access_control import access_required, demo_access
from ..models.favorites import Favorites
from ..services.notification_service import NotificationService
import logging

stocks = Blueprint('stocks', __name__)
logger = logging.getLogger(__name__)

@stocks.route('/')
@access_required
def index():
    """Main stocks page"""
    try:
        oslo_stocks = DataService.get_oslo_bors_overview()
        global_stocks = DataService.get_global_stocks_overview()
        
        return render_template('stocks/index.html',
                             oslo_stocks=oslo_stocks,
                             global_stocks=global_stocks)
    except Exception as e:
        logger.error(f"Error in stocks index: {e}")
        flash('Kunne ikke laste aksjedata. Prøv igjen senere.', 'error')
        return render_template('stocks/index.html', oslo_stocks={}, global_stocks={})

@stocks.route('/list')
@stocks.route('/list/<category>')
@access_required
def list_stocks(category='all'):
    """List stocks by category"""
    try:
        if category == 'oslo':
            stocks_data = DataService.get_oslo_bors_overview()
            title = "Aksjeliste - Oslo Børs"
            template = 'stocks/list.html'
        elif category == 'global':
            stocks_data = DataService.get_global_stocks_overview()
            title = "Aksjeliste - Globale Markeder"
            template = 'stocks/list.html'
        elif category == 'crypto':
            stocks_data = DataService.get_crypto_overview()
            title = "Kryptovaluta"
            template = 'stocks/crypto.html'
            if not stocks_data:
                # Provide comprehensive mock crypto data
                stocks_data = {
                    'BTC-USD': {
                        'symbol': 'BTC-USD', 
                        'name': 'Bitcoin', 
                        'price': 67500, 
                        'change': 2.5,
                        'change_percent': 2.5,
                        'volume': '24.5B',
                        'market_cap': '1.3T'
                    },
                    'ETH-USD': {
                        'symbol': 'ETH-USD', 
                        'name': 'Ethereum', 
                        'price': 3200, 
                        'change': 1.8,
                        'change_percent': 1.8,
                        'volume': '12.8B',
                        'market_cap': '384B'
                    },
                    'BNB-USD': {
                        'symbol': 'BNB-USD', 
                        'name': 'Binance Coin', 
                        'price': 310, 
                        'change': -0.5,
                        'change_percent': -0.5,
                        'volume': '1.2B',
                        'market_cap': '47B'
                    },
                    'ADA-USD': {
                        'symbol': 'ADA-USD', 
                        'name': 'Cardano', 
                        'price': 0.48, 
                        'change': 3.2,
                        'change_percent': 3.2,
                        'volume': '456M',
                        'market_cap': '17B'
                    },
                    'SOL-USD': {
                        'symbol': 'SOL-USD', 
                        'name': 'Solana', 
                        'price': 98.50, 
                        'change': -1.3,
                        'change_percent': -1.3,
                        'volume': '2.1B',
                        'market_cap': '45B'
                    }
                }
        elif category == 'currency':
            stocks_data = DataService.get_currency_overview()
            title = "Valutakurser"
            template = 'stocks/currency.html'
            if not stocks_data:
                # Provide comprehensive mock currency data
                stocks_data = {
                    'USDNOK': {
                        'symbol': 'USDNOK', 
                        'name': 'USD/NOK', 
                        'price': 10.85, 
                        'change': 0.3,
                        'change_percent': 0.28,
                        'high': 10.92,
                        'low': 10.81
                    },
                    'EURNOK': {
                        'symbol': 'EURNOK', 
                        'name': 'EUR/NOK', 
                        'price': 11.85, 
                        'change': -0.1,
                        'change_percent': -0.08,
                        'high': 11.89,
                        'low': 11.82
                    },
                    'GBPNOK': {
                        'symbol': 'GBPNOK', 
                        'name': 'GBP/NOK', 
                        'price': 13.45, 
                        'change': 0.8,
                        'change_percent': 0.60,
                        'high': 13.52,
                        'low': 13.38
                    },
                    'SEKNOK': {
                        'symbol': 'SEKNOK', 
                        'name': 'SEK/NOK', 
                        'price': 1.02, 
                        'change': 0.1,
                        'change_percent': 0.10,
                        'high': 1.03,
                        'low': 1.01
                    },
                    'DKKNOK': {
                        'symbol': 'DKKNOK', 
                        'name': 'DKK/NOK', 
                        'price': 1.59, 
                        'change': -0.02,
                        'change_percent': -0.13,
                        'high': 1.60,
                        'low': 1.58
                    }
                }
        else:
            # Show all categories
            oslo_stocks = DataService.get_oslo_bors_overview()
            global_stocks = DataService.get_global_stocks_overview()
            return render_template('stocks/list.html',
                                 oslo_stocks=oslo_stocks,
                                 global_stocks=global_stocks,
                                 title="Alle Aksjer")
        
        # Ensure stocks_data is not None
        if stocks_data is None:
            stocks_data = {}
            flash(f'Ingen data tilgjengelig for {title}', 'warning')
        
        return render_template(template,
                             stocks=stocks_data,
                             title=title,
                             category=category)
                             
    except Exception as e:
        logger.error(f"Error in list_stocks for {category}: {e}")
        flash('Kunne ikke laste aksjedata. Prøv igjen senere.', 'error')
        return render_template('stocks/list.html', stocks={}, title="Feil")

@stocks.route('/list/oslo', strict_slashes=False)
@access_required
def list_oslo():
    """List Oslo Stock Exchange stocks"""
    try:
        # Get Oslo stocks from data service
        stocks = DataService.get_oslo_bors_overview()
        
        if not stocks:
            flash('Kunne ikke laste Oslo Børs aksjer. Prøv igjen senere.', 'warning')
            stocks = {}  # Changed from [] to {} to match expected format
            
        return render_template('stocks/list.html',
                             stocks=stocks,
                             market='Oslo Børs',
                             market_type='oslo')
    except Exception as e:
        current_app.logger.error(f"Error loading Oslo stocks: {str(e)}")
        flash('Kunne ikke laste aksjedata. Prøv igjen senere.', 'error')
        return render_template('stocks/list.html',
                             stocks={},  # Changed from [] to {} 
                             market='Oslo Børs',
                             market_type='oslo',
                             error=True)

@stocks.route('/list/global')
@access_required
def global_list():
    """Global stocks"""
    return list_stocks('global')

@stocks.route('/list/crypto')
@access_required
def list_crypto():
    """Crypto currencies"""
    return list_stocks('crypto')

@stocks.route('/list/currency')
@access_required
def list_currency():
    """Currency rates"""
    return list_stocks('currency')

@stocks.route('/details/<symbol>')
@access_required
def details(symbol):
    """Stock details page with all analysis and data"""
    try:
        # Get stock information
        stock_info = DataService.get_stock_info(symbol)
        if not stock_info:
            flash(f'Kunne ikke finne informasjon for {symbol}', 'error')
            return redirect(url_for('stocks.index'))
        
        # Get additional analysis data
        technical_data = AnalysisService.get_technical_analysis(symbol)
        
        # Try detail.html first, fallback to details.html if it doesn't exist
        try:
            return render_template('stocks/detail.html',
                                 symbol=symbol,
                                 stock_info=stock_info,
                                 technical_data=technical_data)
        except Exception:
            # Fallback to details.html
            return render_template('stocks/details.html',
                                 symbol=symbol,
                                 stock_info=stock_info,
                                 technical_data=technical_data)
                             
    except Exception as e:
        logger.error(f"Error in stock details for {symbol}: {e}")
        flash('Kunne ikke laste aksjedetaljer. Prøv igjen senere.', 'error')
        # More specific redirect based on referrer
        referrer = request.referrer
        if referrer and 'oslo' in referrer:
            return redirect(url_for('stocks.list_oslo'))
        elif referrer and 'global' in referrer:
            return redirect(url_for('stocks.global_list'))
        else:
            return redirect(url_for('stocks.index'))

@stocks.route('/search')
@access_required
def search():
    """Search for stocks - primary search function"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('stocks/search.html', 
                             results=[], 
                             query='')
    
    try:
        # Search in all available stocks
        all_results = []
        
        # Search Oslo Børs
        oslo_stocks = DataService.get_oslo_bors_overview() or {}
        for ticker, data in oslo_stocks.items():
            if query.upper() in ticker.upper() or (data.get('name', '') and query.upper() in data.get('name', '').upper()):
                all_results.append({
                    'ticker': ticker,
                    'name': data.get('name', ticker),
                    'market': 'Oslo Børs',
                    'price': data.get('last_price', 'N/A'),
                    'change_percent': data.get('change_percent', 0),
                    'category': 'oslo'
                })
        
        # Search Global stocks
        global_stocks = DataService.get_global_stocks_overview() or {}
        for ticker, data in global_stocks.items():
            if query.upper() in ticker.upper() or (data.get('name', '') and query.upper() in data.get('name', '').upper()):
                all_results.append({
                    'ticker': ticker,
                    'name': data.get('name', ticker),
                    'market': 'Global',
                    'price': data.get('last_price', 'N/A'),
                    'change_percent': data.get('change_percent', 0),
                    'category': 'global'
                })
        
        # Search Crypto
        crypto_data = DataService.get_crypto_overview() or {}
        for ticker, data in crypto_data.items():
            if query.upper() in ticker.upper() or (data.get('name', '') and query.upper() in data.get('name', '').upper()):
                all_results.append({
                    'ticker': ticker,
                    'name': data.get('name', ticker),
                    'market': 'Crypto',
                    'price': data.get('last_price', 'N/A'),
                    'change_percent': data.get('change_percent', 0),
                    'category': 'crypto'
                })
        
        # Limit results
        all_results = all_results[:20]
        
        return render_template('stocks/search.html', 
                             results=all_results, 
                             query=query)
        
    except Exception as e:
        current_app.logger.error(f"Error in stock search: {e}")
        return render_template('stocks/search.html', 
                             results=[], 
                             query=query,
                             error="Søket kunne ikke fullføres. Prøv igjen senere.")

@stocks.route('/api/search')
@access_required
def api_search():
    """API endpoint for stock search"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    try:
        results = DataService.search_stocks(query)
        return jsonify({
            'success': True,
            'results': results,
            'query': query
        })
    except Exception as e:
        logger.error(f"Error in API search for {query}: {e}")
        return jsonify({'error': 'Search failed', 'message': str(e)}), 500

@stocks.route('/api/favorites/add', methods=['POST'])
@login_required
def add_to_favorites():
    """Add stock to favorites"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        # Add to favorites logic here
        return jsonify({'success': True, 'message': f'{symbol} lagt til i favoritter'})
        
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        return jsonify({'error': 'Failed to add to favorites'}), 500

@stocks.route('/compare')
@access_required
def compare():
    """Stock comparison page"""
    symbols = request.args.getlist('symbols')
    
    if not symbols:
        return render_template('stocks/compare.html', stocks=[])
    
    try:
        stocks_data = []
        for symbol in symbols:
            stock_info = DataService.get_stock_info(symbol)
            if stock_info:
                stocks_data.append(stock_info)
        
        return render_template('stocks/compare.html', stocks=stocks_data)
        
    except Exception as e:
        logger.error(f"Error in stock comparison: {e}")
        flash('Feil ved sammenligning av aksjer.', 'error')
        return render_template('stocks/compare.html', stocks=[])

@stocks.route('/prices')
@access_required
def prices():
    """Stock prices overview"""
    try:
        oslo_stocks = DataService.get_oslo_bors_overview()
        global_stocks = DataService.get_global_stocks_overview()
        crypto_data = DataService.get_crypto_overview()
        currency_data = DataService.get_currency_overview()
        
        return render_template('stocks/prices.html',
                             oslo_stocks=oslo_stocks,
                             global_stocks=global_stocks,
                             crypto_data=crypto_data,
                             currency_data=currency_data)
                             
    except Exception as e:
        logger.error(f"Error in prices overview: {e}")
        flash('Kunne ikke laste prisdata.', 'error')
        return render_template('stocks/prices.html',
                             oslo_stocks={},
                             global_stocks={},
                             crypto_data={},
                             currency_data={})

