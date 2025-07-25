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
from ..services.insider_trading_service import InsiderTradingService
import logging

stocks = Blueprint('stocks', __name__)
logger = logging.getLogger(__name__)

# Initialize insider trading service
insider_service = InsiderTradingService()

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
@demo_access
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
        
        # Try enhanced details template first, then fallback
        try:
            return render_template('stocks/details_enhanced.html',
                                 ticker=symbol,
                                 stock_info=stock_info,
                                 technical_data=technical_data)
        except Exception as e:
            logger.warning(f"Enhanced template failed for {symbol}: {e}")
            try:
                return render_template('stocks/detail.html',
                                     symbol=symbol,
                                     stock_info=stock_info,
                                     technical_data=technical_data)
            except Exception as e2:
                logger.error(f"All templates failed for {symbol}: {e2}")
                flash(f'Template error for {symbol}. Redirecting to stock list.', 'error')
                return redirect(url_for('stocks.index'))
                             
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
        flash('Kunne ikke laste prisdata.', 'error')
        return render_template('stocks/prices.html',
                             oslo_stocks={},
                             global_stocks={},
                             crypto_data={},
                             currency_data={})

from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..services.data_service import DataService
from ..services.insider_trading_service import InsiderTradingService
from ..utils.access_control import demo_access
import logging

insider_trading = Blueprint('insider_trading', __name__)
logger = logging.getLogger(__name__)

# Initialize insider trading service for this blueprint too
insider_service_2 = InsiderTradingService()

@insider_trading.route('/')
@demo_access
def index():
    """Enhanced insider trading main page with comprehensive data and analytics"""
    try:
        # Get recent insider trading data
        insider_data = DataService.get_insider_trading_data() or []
        
        # Get popular stocks for search dropdown - enhanced with activity data
        popular_stocks = DataService.get_popular_stocks() or []
        
        # Enhance popular stocks with mock recent activity
        for i, stock in enumerate(popular_stocks[:12]):
            if isinstance(stock, dict):
                stock['recent_activity'] = str(12 - i) if i < 3 else None
            else:
                # If it's an object, add attribute
                setattr(stock, 'recent_activity', str(12 - i) if i < 3 else None)
        
        # Market statistics
        market_stats = {
            'total_buys': 127,
            'total_sells': 89,
            'total_value': '1.2B'
        }
        
        # Top active stocks
        top_active_stocks = [
            {'symbol': 'EQNR', 'activity': '12'},
            {'symbol': 'TEL', 'activity': '8'},
            {'symbol': 'NOK', 'activity': '6'},
            {'symbol': 'DNB', 'activity': '5'},
            {'symbol': 'MOWI', 'activity': '4'}
        ]
        
        # Dashboard stats
        dashboard_stats = {
            'hot_stocks_count': 24,
            'signal_count': 12,
            'alerts_count': 7
        }
        
        return render_template('insider_trading/index.html',
                             insider_data=insider_data,
                             popular_stocks=popular_stocks,
                             selected_symbol=None,
                             market_stats=market_stats,
                             top_active_stocks=top_active_stocks,
                             **dashboard_stats)
                             
    except Exception as e:
        logger.error(f"Error in insider trading index: {e}")
        return render_template('insider_trading/index.html',
                             insider_data=[],
                             popular_stocks=[],
                             error="Kunne ikke laste innsidehandel data",
                             market_stats={},
                             top_active_stocks=[],
                             hot_stocks_count=0,
                             signal_count=0,
                             alerts_count=0)

@insider_trading.route('/search', methods=['GET', 'POST'])
@demo_access
def search():
    """Enhanced insider trading search with advanced filtering"""
    symbol = request.args.get('symbol', '').strip().upper()
    transaction_type = request.args.get('transaction_type', '')
    period = int(request.args.get('period', 30))
    min_value = request.args.get('min_value', type=float)
    role = request.args.get('role', '')
    sort = request.args.get('sort', 'date_desc')
    company_name = request.args.get('company_name', '')
    insider_name = request.args.get('insider_name', '')
    significant_only = request.args.get('significant_only') == '1'
    
    # Handle POST requests from the search form
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').strip().upper()
        transaction_type = request.form.get('transaction_type', '')
        period = int(request.form.get('period', 30))
        min_value = request.form.get('min_value', type=float)
        role = request.form.get('role', '')
        sort = request.form.get('sort', 'date_desc')
        significant_only = request.form.get('significant_only') == '1'
    
    if not symbol:
        flash('Vennligst velg en aksje for å søke etter innsidehandel.', 'warning')
        popular_stocks = DataService.get_popular_stocks() or []
        
        # Add default market stats
        market_stats = {
            'total_buys': 127,
            'total_sells': 89,
            'total_value': '1.2B'
        }
        
        # Default top active stocks
        top_active_stocks = [
            {'symbol': 'EQNR', 'activity': '12'},
            {'symbol': 'TEL', 'activity': '8'},
            {'symbol': 'NOK', 'activity': '6'},
            {'symbol': 'DNB', 'activity': '5'},
            {'symbol': 'MOWI', 'activity': '4'}
        ]
        
        return render_template('insider_trading/index.html',
                             insider_data=[],
                             popular_stocks=popular_stocks,
                             market_stats=market_stats,
                             top_active_stocks=top_active_stocks,
                             hot_stocks_count=24,
                             signal_count=12,
                             search_performed=False)
    
    try:
        # Get insider trading data for specific symbol using enhanced filtering
        insider_transactions = insider_service_2.get_insider_transactions(symbol) or []
        
        # Apply filters
        filtered_transactions = []
        for transaction in insider_transactions:
            # Date filter
            if period:
                transaction_date = datetime.strptime(transaction.get('date', '2024-01-01'), '%Y-%m-%d')
                cutoff_date = datetime.now() - timedelta(days=period)
                if transaction_date < cutoff_date:
                    continue
            
            # Transaction type filter
            if transaction_type and transaction.get('transaction_type') != transaction_type:
                continue
                
            # Minimum value filter
            if min_value and transaction.get('value', 0) < min_value:
                continue
                
            # Role filter
            if role and transaction.get('role') != role:
                continue
                
            # Significant transactions only
            if significant_only and transaction.get('value', 0) < 1000000:  # 1M threshold
                continue
                
            filtered_transactions.append(transaction)
        
        # Sort transactions
        if sort == 'date_desc':
            filtered_transactions.sort(key=lambda x: x.get('date', ''), reverse=True)
        elif sort == 'date_asc':
            filtered_transactions.sort(key=lambda x: x.get('date', ''))
        elif sort == 'value_desc':
            filtered_transactions.sort(key=lambda x: x.get('value', 0), reverse=True)
        elif sort == 'value_asc':
            filtered_transactions.sort(key=lambda x: x.get('value', 0))
        
        popular_stocks = DataService.get_popular_stocks() or []
        
        # Transform and enhance transactions for display
        insider_data = []
        total_buys = total_sells = total_value = unique_insiders = 0
        insider_names = set()
        
        for transaction in insider_transactions:
            transaction_data = {
                'date': transaction.transaction_date if hasattr(transaction, 'transaction_date') else 'N/A',
                'time': '12:45',  # Can be enhanced with actual time data
                'person': transaction.insider_name if hasattr(transaction, 'insider_name') else 'Ukjent',
                'role': transaction.title if hasattr(transaction, 'title') else 'Officer',
                'transaction_type': 'KJØP' if 'buy' in str(transaction.transaction_type).lower() or 'purchase' in str(transaction.transaction_type).lower() else 'SALG',
                'quantity': transaction.shares if hasattr(transaction, 'shares') else 0,
                'price': transaction.price if hasattr(transaction, 'price') else 0,
                'total_value': transaction.value if hasattr(transaction, 'value') else 0,
                'symbol': symbol
            }
            
            insider_data.append(transaction_data)
            
            # Calculate summary statistics
            if transaction_data['transaction_type'] == 'KJØP':
                total_buys += 1
            else:
                total_sells += 1
                
            total_value += float(transaction_data['total_value'] or 0)
            insider_names.add(transaction_data['person'])
        
        unique_insiders = len(insider_names)
        
        # Apply sorting
        if sort == 'date_desc':
            insider_data.sort(key=lambda x: x['date'], reverse=True)
        elif sort == 'date_asc':
            insider_data.sort(key=lambda x: x['date'])
        elif sort == 'value_desc':
            insider_data.sort(key=lambda x: float(x['total_value'] or 0), reverse=True)
        elif sort == 'value_asc':
            insider_data.sort(key=lambda x: float(x['total_value'] or 0))
        
        # Calculate summary stats
        insider_summary = {
            'total_buys': total_buys,
            'total_sells': total_sells,
            'net_value': f"{total_value:,.0f}",
            'unique_insiders': unique_insiders
        }
        
        # Market statistics for sidebar
        market_stats = {
            'total_buys': 127,
            'total_sells': 89,
            'total_value': '1.2B'
        }
        
        # Top active stocks
        top_active_stocks = [
            {'symbol': 'EQNR', 'activity': '12'},
            {'symbol': 'TEL', 'activity': '8'},
            {'symbol': 'NOK', 'activity': '6'},
            {'symbol': 'DNB', 'activity': '5'},
            {'symbol': 'MOWI', 'activity': '4'}
        ]
        
        if not insider_data:
            flash(f'Ingen innsidehandel data funnet for {symbol} med de valgte filtrene.', 'info')
        
        return render_template('insider_trading/index.html',
                             insider_data=insider_data,
                             popular_stocks=popular_stocks,
                             selected_symbol=symbol,
                             insider_summary=insider_summary,
                             market_stats=market_stats,
                             top_active_stocks=top_active_stocks,
                             hot_stocks_count=24,
                             signal_count=12,
                             alerts_count=7,
                             search_params={
                                 'transaction_type': transaction_type,
                                 'period': period,
                                 'min_value': min_value,
                                 'role': role,
                                 'sort': sort,
                                 'company_name': company_name,
                                 'insider_name': insider_name,
                                 'significant_only': significant_only
                             })
                             
    except Exception as e:
        logger.error(f"Error searching insider trading for {symbol}: {e}")
        flash('Feil ved søk etter innsidehandel data.', 'error')
        return redirect(url_for('insider_trading.index'))

# New API endpoints for enhanced functionality
@insider_trading.route('/api/latest')
@demo_access
def api_latest():
    """API endpoint for latest insider trading data"""
    try:
        limit = request.args.get('limit', 25, type=int)
        insider_data = DataService.get_insider_trading_data() or []
        
        # Format for JSON response
        transactions = []
        for trade in insider_data[:limit]:
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
        logger.error(f"Error in API latest endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@insider_trading.route('/api/export')
@demo_access
def api_export():
    """Export insider trading data"""
    try:
        symbol = request.args.get('symbol', '')
        format_type = request.args.get('format', 'csv')
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol required'}), 400
        
        # Get data
        insider_transactions = insider_service.get_insider_transactions(symbol) or []
        
        if format_type == 'csv':
            # Generate CSV
            import csv
            import io
            from flask import Response
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Date', 'Insider', 'Role', 'Transaction Type', 'Quantity', 'Price', 'Total Value'])
            
            for transaction in insider_transactions:
                writer.writerow([
                    getattr(transaction, 'transaction_date', 'N/A'),
                    getattr(transaction, 'insider_name', 'Ukjent'),
                    getattr(transaction, 'title', 'Officer'),
                    'KJØP' if 'buy' in str(getattr(transaction, 'transaction_type', '')).lower() else 'SALG',
                    getattr(transaction, 'shares', 0),
                    getattr(transaction, 'price', 0),
                    getattr(transaction, 'value', 0)
                ])
            
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=insider_trading_{symbol}.csv'}
            )
        else:
            return jsonify({'success': False, 'error': 'Unsupported format'}), 400
            
    except Exception as e:
        logger.error(f"Error in export endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@insider_trading.route('/api/stats')
@demo_access
def api_stats():
    """Get market statistics for insider trading"""
    try:
        # Mock statistics - can be enhanced with real data
        stats = {
            'total_buys': 127,
            'total_sells': 89,
            'total_value': '1.2B',
            'hot_stocks_count': 24,
            'signal_count': 12,
            'alerts_count': 7,
            'top_active_stocks': [
                {'symbol': 'EQNR', 'activity': '12'},
                {'symbol': 'TEL', 'activity': '8'},
                {'symbol': 'NOK', 'activity': '6'},
                {'symbol': 'DNB', 'activity': '5'},
                {'symbol': 'MOWI', 'activity': '4'}
            ]
        }
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@insider_trading.route('/api/trending')
@demo_access
def api_trending():
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
        logger.error(f"Error in trending endpoint: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500