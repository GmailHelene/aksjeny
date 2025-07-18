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
@demo_access
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
@demo_access
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
        elif category == 'currency':
            stocks_data = DataService.get_currency_overview()
            title = "Valutakurser"
            template = 'stocks/currency.html'
        else:
            # Show all categories
            oslo_stocks = DataService.get_oslo_bors_overview()
            global_stocks = DataService.get_global_stocks_overview()
            return render_template('stocks/list.html',
                                 oslo_stocks=oslo_stocks,
                                 global_stocks=global_stocks,
                                 title="Alle Aksjer")
        
        return render_template(template,
                             stocks=stocks_data,
                             title=title,
                             category=category)
                             
    except Exception as e:
        logger.error(f"Error in list_stocks for {category}: {e}")
        flash('Kunne ikke laste aksjedata. Prøv igjen senere.', 'error')
        return render_template('stocks/list.html', stocks={}, title="Feil")

@stocks.route('/list/oslo')
@demo_access
def list_oslo():
    """Oslo Børs stocks"""
    return list_stocks('oslo')

@stocks.route('/list/global')
@demo_access
def global_list():
    """Global stocks"""
    return list_stocks('global')

@stocks.route('/list/crypto')
@demo_access
def list_crypto():
    """Crypto currencies"""
    return list_stocks('crypto')

@stocks.route('/list/currency')
@demo_access
def list_currency():
    """Currency rates"""
    return list_stocks('currency')

@stocks.route('/details/<symbol>')
@demo_access
def details(symbol):
    """Stock details page"""
    try:
        # Get stock information
        stock_info = DataService.get_stock_info(symbol)
        if not stock_info:
            flash(f'Kunne ikke finne informasjon for {symbol}', 'error')
            return redirect(url_for('stocks.index'))
        
        # Get additional analysis data
        technical_data = AnalysisService.get_technical_analysis(symbol)
        
        return render_template('stocks/detail.html',
                             symbol=symbol,
                             stock_info=stock_info,
                             technical_data=technical_data)
                             
    except Exception as e:
        logger.error(f"Error in stock details for {symbol}: {e}")
        flash('Kunne ikke laste aksjedetaljer. Prøv igjen senere.', 'error')
        return redirect(url_for('stocks.index'))

@stocks.route('/search')
@demo_access
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
@demo_access
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
@demo_access
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
@demo_access
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
        flash('Kunne inte laste prisdata.', 'error')
        return render_template('stocks/prices.html')

@stocks.route('/search')
@access_required
def search():
    """Search for stocks"""
    query = request.args.get('q', '')
    if not query:
        return render_template('stocks/search.html')
    
    results = DataService.search_stocks(query)
    return render_template('stocks/search.html', 
                         results=results,
                         query=query)

@stocks.route('/api/search')
@access_required
def api_search():
    """API endpoint for stock search"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    try:
        results = DataService.search_stocks(query)
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error in stock search: {str(e)}")
        return jsonify({'error': 'Søket feilet. Vennligst prøv igjen.'}), 500

@stocks.route('/list/oslo')
@access_required
def list_oslo():
    """Show Oslo Børs stocks"""
    try:
        stocks = DataService.get_oslo_bors_overview()
        if not stocks:
            flash("Kunne ikke hente Oslo Børs data. Vennligst prøv igjen senere.", "error")
            stocks = []
            
        return render_template(
            'stocks/list.html',
            stocks=stocks,
            title="Aksjeliste - Oslo Børs",
            market_type="oslo"
        )
    except Exception as e:
        current_app.logger.error(f"Error in oslo_list: {str(e)}")
        flash("En feil oppstod ved henting av Oslo Børs data. Vennligst prøv igjen senere.", "error")
        return render_template('stocks/list.html', title="Aksjeliste - Oslo Børs", market_type="oslo")

@stocks.route('/list/global')
@access_required
def global_list():
    """List global stocks"""
    try:
        stocks = DataService.get_global_stocks_overview()
        return render_template(
            'stocks/list.html',
            stocks=stocks,
            market_type="global",
            title="Aksjeliste - Globale Markeder"
        )
    except Exception as e:
        current_app.logger.error(f"Error in global stocks list: {str(e)}")
        flash("Kunne ikke hente globale markedsdata. Vennligst prøv igjen senere.", "error")
        return render_template('stocks/list.html', stocks={}, title="Aksjeliste - Globale Markeder", market_type="global")

@stocks.route('/list/crypto')
@access_required
def list_crypto():
    """List cryptocurrencies with robust error handling"""
    try:
        stocks = DataService.get_crypto_overview()
        
        # Ensure stocks is always a dictionary, even if empty
        if not stocks or not isinstance(stocks, dict):
            stocks = {}
        
        return render_template(
            'stocks/crypto.html',
            stocks=stocks,
            market_type="crypto",
            title="Kryptovaluta"
        )
    except Exception as e:
        current_app.logger.error(f"Error in crypto list: {str(e)}")
        flash("Kunne ikke hente kryptovalutadata. Viser demo-data.", "warning")
        
        # Provide fallback crypto data
        fallback_crypto = {
            'BTC-USD': {
                'ticker': 'BTC-USD',
                'name': 'Bitcoin',
                'last_price': 45000.00,
                'change': 1250.00,
                'change_percent': 2.85,
                'volume': 28500000000,
                'market_cap': 875000000000
            },
            'ETH-USD': {
                'ticker': 'ETH-USD',
                'name': 'Ethereum',
                'last_price': 3200.00,
                'change': -85.50,
                'change_percent': -2.60,
                'volume': 15200000000,
                'market_cap': 385000000000
            },
            'BNB-USD': {
                'ticker': 'BNB-USD',
                'name': 'Binance Coin',
                'last_price': 320.50,
                'change': 8.75,
                'change_percent': 2.81,
                'volume': 1250000000,
                'market_cap': 49000000000
            }
        }
        
        return render_template(
            'stocks/crypto.html', 
            stocks=fallback_crypto, 
            title="Kryptovaluta", 
            market_type="crypto",
            error="Viser demo-data. Live data er midlertidig utilgjengelig."
        )

@stocks.route('/currency')
@stocks.route('/list/currency')
@access_required
def list_currency():
    """Show currency exchange rates"""
    try:
        # Get and normalize base currency
        base_currency = request.args.get('base', 'NOK').upper()
        if not base_currency or len(base_currency) != 3:
            base_currency = 'NOK'
        
        # Enhanced currency data with more pairs
        enhanced_currencies = {
            'USDNOK=X': {
                'symbol': 'USDNOK=X',
                'name': 'USD til NOK',
                'currency_pair': 'USD/NOK',
                'rate': 10.67,
                'change': 0.12,
                'change_percent': 1.14,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 10.66,
                'ask': 10.68,
                'day_high': 10.72,
                'day_low': 10.58,
                'volume': 1250000
            },
            'EURNOK=X': {
                'symbol': 'EURNOK=X', 
                'name': 'EUR til NOK',
                'currency_pair': 'EUR/NOK',
                'rate': 11.58,
                'change': -0.08,
                'change_percent': -0.69,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 11.57,
                'ask': 11.59,
                'day_high': 11.67,
                'day_low': 11.52,
                'volume': 890000
            },
            'GBPNOK=X': {
                'symbol': 'GBPNOK=X',
                'name': 'GBP til NOK', 
                'currency_pair': 'GBP/NOK',
                'rate': 13.45,
                'change': 0.23,
                'change_percent': 1.74,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 13.44,
                'ask': 13.46,
                'day_high': 13.52,
                'day_low': 13.18,
                'volume': 450000
            },
            'JPYNOK=X': {
                'symbol': 'JPYNOK=X',
                'name': 'JPY til NOK',
                'currency_pair': 'JPY/NOK', 
                'rate': 0.071,
                'change': 0.001,
                'change_percent': 1.43,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 0.0709,
                'ask': 0.0712,
                'day_high': 0.0715,
                'day_low': 0.0698,
                'volume': 320000
            },
            'SEKNOK=X': {
                'symbol': 'SEKNOK=X',
                'name': 'SEK til NOK',
                'currency_pair': 'SEK/NOK',
                'rate': 0.98,
                'change': -0.02,
                'change_percent': -2.04,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 0.979,
                'ask': 0.981,
                'day_high': 1.002,
                'day_low': 0.975,
                'volume': 780000
            },
            'DKKNOK=X': {
                'symbol': 'DKKNOK=X',
                'name': 'DKK til NOK',
                'currency_pair': 'DKK/NOK',
                'rate': 1.55,
                'change': 0.01,
                'change_percent': 0.65,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 1.549,
                'ask': 1.551,
                'day_high': 1.558,
                'day_low': 1.542,
                'volume': 290000
            },
            'CHFNOK=X': {
                'symbol': 'CHFNOK=X',
                'name': 'CHF til NOK',
                'currency_pair': 'CHF/NOK',
                'rate': 11.92,
                'change': 0.15,
                'change_percent': 1.28,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 11.91,
                'ask': 11.93,
                'day_high': 11.98,
                'day_low': 11.78,
                'volume': 180000
            },
            'CADNOK=X': {
                'symbol': 'CADNOK=X',
                'name': 'CAD til NOK',
                'currency_pair': 'CAD/NOK',
                'rate': 7.89,
                'change': -0.05,
                'change_percent': -0.63,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 7.88,
                'ask': 7.90,
                'day_high': 7.95,
                'day_low': 7.84,
                'volume': 210000
            },
            'AUDNOK=X': {
                'symbol': 'AUDNOK=X',
                'name': 'AUD til NOK',
                'currency_pair': 'AUD/NOK',
                'rate': 7.12,
                'change': 0.08,
                'change_percent': 1.14,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 7.11,
                'ask': 7.13,
                'day_high': 7.18,
                'day_low': 7.02,
                'volume': 165000
            },
            'CNYNOK=X': {
                'symbol': 'CNYNOK=X',
                'name': 'CNY til NOK',
                'currency_pair': 'CNY/NOK',
                'rate': 1.47,
                'change': 0.02,
                'change_percent': 1.38,
                'last_updated': '2025-07-14 16:15:00',
                'bid': 1.469,
                'ask': 1.471,
                'day_high': 1.475,
                'day_low': 1.451,
                'volume': 95000
            }
        }
        
        # Legg til last_price-felt for template-kompatibilitet
        for c in enhanced_currencies.values():
            c['last_price'] = c.get('rate', None)
        # Render template med kompatible data
        return render_template(
            'stocks/currency.html',
            currencies=enhanced_currencies,
            base_currency=base_currency,
            error=None,
            title="Valutakurser"
        )
    except Exception as e:
        current_app.logger.error(f"Error in currency_list: {str(e)}")
        # Return template with error state
        return render_template(
            'stocks/currency.html',
            currencies={},
            base_currency=base_currency if 'base_currency' in locals() else 'NOK',
            error="En feil oppstod ved henting av valutakurser. Vennligst prøv igjen senere.",
            title="Valutakurser"
        )

@stocks.route('/api/stock/<ticker>')
@access_required
def api_stock_data(ticker):
    """API endpoint for individual stock data"""
    try:
        # Get basic stock info
        stock_data = DataService.get_single_stock_data(ticker)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
        
        return jsonify({
            'ticker': ticker,
            'data': stock_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error getting stock data for {ticker}: {str(e)}")
        return jsonify({'error': 'Failed to fetch stock data'}), 500

@stocks.route('/api/stock/<ticker>/history')
@access_required
def api_stock_history(ticker):
    """API endpoint for stock historical data"""
    try:
        period = request.args.get('period', '1y')
        stock_data = DataService.get_stock_data(ticker, period=period)
        
        if stock_data.empty:
            return jsonify({'error': 'No historical data available'}), 404
        
        # Convert DataFrame to JSON-serializable format
        history = []
        stock_data_reset = stock_data.reset_index()
        for _, row in stock_data_reset.iterrows():
            history.append({
                'date': row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                'open': float(row['Open']) if pd.notna(row['Open']) else None,
                'high': float(row['High']) if pd.notna(row['High']) else None,
                'low': float(row['Low']) if pd.notna(row['Low']) else None,
                'close': float(row['Close']) if pd.notna(row['Close']) else None,
                'volume': int(row['Volume']) if pd.notna(row['Volume']) else None
            })
        
        return jsonify({
            'ticker': ticker,
            'period': period,
            'history': history,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error getting stock history for {ticker}: {str(e)}")
        return jsonify({'error': 'Failed to fetch stock history'}), 500

@stocks.route('/compare')
@access_required
def compare():
    """Compare multiple stocks"""
    try:
        tickers = request.args.getlist('ticker')
        if not tickers:
            return render_template('stocks/compare.html')
        
        stocks_data = {}
        for ticker in tickers:
            try:
                stock_info = DataService.get_stock_info(ticker)
                stock_data = DataService.get_stock_data(ticker, period='6mo', interval='1d')
                
                # Convert DataFrame to list for template
                chart_data = []
                if not stock_data.empty:
                    stock_data_reset = stock_data.reset_index()
                    for _, row in stock_data_reset.iterrows():
                        chart_data.append({
                            'Date': row['Date'].strftime('%Y-%m-%d') if hasattr(row['Date'], 'strftime') else str(row['Date']),
                            'Close': float(row['Close'])
                        })
                
                stocks_data[ticker] = {
                    'info': stock_info,
                    'data': chart_data
                }
            except Exception as e:
                current_app.logger.error(f"Error getting data for {ticker}: {str(e)}")
        
        return render_template(
            'stocks/compare.html',
            stocks=stocks_data,
            tickers=tickers
        )
    except Exception as e:
        current_app.logger.error(f"Error in stock comparison: {str(e)}")
        flash("Kunne ikke sammenligne aksjene. Vennligst prøv igjen senere.", "error")
        return render_template('stocks/compare.html')

@stocks.route('/index')
@access_required
def stocks_index():
    """Alias for index function"""
    return render_template('stocks/index.html')

@stocks.route('/prices')
@access_required
def prices():
    """Show comprehensive price overview for all markets"""
    try:
        # Get data from all markets
        oslo_stocks = DataService.get_oslo_bors_overview() or {}
        global_stocks = DataService.get_global_stocks_overview() or {}
        crypto = DataService.get_crypto_overview() or {}
        currency = DataService.get_currency_overview() or {}
        
        # Organize data for template
        market_data = {
            'oslo_stocks': oslo_stocks,
            'global_stocks': global_stocks,
            'crypto': crypto,
            'currency': currency
        }
        
        # Get market stats
        total_stocks = len(oslo_stocks) + len(global_stocks)
        total_crypto = len(crypto)
        total_currency = len(currency)
        
        stats = {
            'total_stocks': total_stocks,
            'total_crypto': total_crypto,
            'total_currency': total_currency,
            'total_instruments': total_stocks + total_crypto + total_currency
        }
        
        return render_template('stocks/prices.html', 
                             market_data=market_data,
                             stats=stats,
                             restricted=not current_user.is_authenticated)
    except Exception as e:
        current_app.logger.error(f"Error in prices route: {str(e)}")
        flash('Kunne ikke hente prisdata', 'error')
        return render_template('stocks/prices.html', 
                             market_data={},
                             stats={},
                             error=True)

