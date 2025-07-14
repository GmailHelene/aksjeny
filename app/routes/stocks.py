import math
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from ..services.data_service import DataService
from ..services.analysis_service import AnalysisService
from ..services.usage_tracker import usage_tracker
from ..utils.access_control import access_required
from ..models.favorites import Favorites
from ..services.notification_service import NotificationService

stocks = Blueprint('stocks', __name__, url_prefix='/stocks')

# Min profil-side
@stocks.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@stocks.route('/')
@access_required
def index():
    """Show stocks landing page with links to all markets"""
    return render_template('stocks/index.html')

@stocks.route('/list')
@access_required
def list_stocks():
    """List stocks with real-time data"""
    try:
        category = request.args.get('category', 'all')
        
        # Get real data from DataService
        if category == 'oslo':
            stocks_data = DataService.get_oslo_bors_overview()
        elif category == 'global':
            stocks_data = DataService.get_global_stocks_overview()
        elif category == 'crypto':
            stocks_data = DataService.get_crypto_overview()
        else:
            # Get all categories
            oslo_stocks = DataService.get_oslo_bors_overview()
            global_stocks = DataService.get_global_stocks_overview()
            crypto = DataService.get_crypto_overview()
            
            stocks_data = {
                'oslo': oslo_stocks,
                'global': global_stocks,
                'crypto': crypto
            }
        
        return render_template('stocks/list.html', 
                             stocks=stocks_data,
                             category=category)
                             
    except Exception as e:
        current_app.logger.error(f"Error in list_stocks: {str(e)}")
        return render_template('error.html', 
                             error="Kunne ikke hente aksjedata. Prøv igjen senere.")

@stocks.route('/list/<category>')
@access_required
def list_stocks_by_category(category):
    """List stocks by category"""
    try:
        if category == 'oslo':
            stocks = DataService.get_oslo_bors_overview()
            title = 'Oslo Børs'
            # Get "mest omsatte" data for Oslo Børs - sorted by volume
            all_oslo_stocks = DataService.get_oslo_bors_overview()
            most_traded_list = sorted(all_oslo_stocks.items(), 
                                    key=lambda x: float(x[1].get('volume', 0)), 
                                    reverse=True)[:10]  # Top 10 most traded
            mest_omsatte = dict(most_traded_list)
        elif category == 'global':
            stocks = DataService.get_global_stocks_overview()
            title = 'Globale Aksjer'
            mest_omsatte = None
        else:
            stocks = {}
            title = 'Ukjent kategori'
            mest_omsatte = None
            
        return render_template('stocks/list.html',
                             stocks=stocks,
                             category=category,
                             title=title,
                             mest_omsatte=mest_omsatte)
    except Exception as e:
        current_app.logger.error(f"Error listing stocks: {str(e)}")
        return render_template('error.html', error=str(e))

@stocks.route('/details/<ticker>')
@access_required
def details(ticker):
    """Stock details page"""
    try:
        from ..services.data_service import DataService
        
        # Ensure we get comprehensive stock data
        stock_data = DataService.get_stock_info(ticker)
        
        # Always ensure we have meaningful data
        if not stock_data or not isinstance(stock_data, dict) or len(stock_data) < 2:
            stock_data = DataService.get_fallback_stock_info(ticker)
        
        # Enhance data with additional fallback values for display
        enhanced_stock_data = {
            'ticker': ticker,
            'shortName': stock_data.get('shortName', ticker),
            'longName': stock_data.get('longName', stock_data.get('shortName', ticker)),
            'regularMarketPrice': stock_data.get('regularMarketPrice', 0),
            'regularMarketChange': stock_data.get('regularMarketChange', 0),
            'regularMarketChangePercent': stock_data.get('regularMarketChangePercent', 0),
            'marketCap': stock_data.get('marketCap', 'N/A'),
            'volume': stock_data.get('volume', 0),
            'averageVolume': stock_data.get('averageVolume', stock_data.get('volume', 0)),
            'fiftyTwoWeekHigh': stock_data.get('fiftyTwoWeekHigh', stock_data.get('regularMarketPrice', 0) * 1.2),
            'fiftyTwoWeekLow': stock_data.get('fiftyTwoWeekLow', stock_data.get('regularMarketPrice', 0) * 0.8),
            'peRatio': stock_data.get('trailingPE', stock_data.get('forwardPE', 'N/A')),
            'eps': stock_data.get('trailingEps', 'N/A'),
            'dividendYield': stock_data.get('dividendYield', stock_data.get('trailingAnnualDividendYield', 'N/A')),
            'sector': stock_data.get('sector', 'N/A'),
            'industry': stock_data.get('industry', 'N/A'),
            'currency': stock_data.get('currency', 'USD' if not ticker.endswith('.OL') else 'NOK'),
            'exchange': stock_data.get('exchange', 'OSE' if ticker.endswith('.OL') else 'NASDAQ'),
            'beta': stock_data.get('beta', 'N/A'),
            'bookValue': stock_data.get('bookValue', 'N/A'),
            'priceToBook': stock_data.get('priceToBook', 'N/A'),
            'website': stock_data.get('website', ''),
            'businessSummary': stock_data.get('longBusinessSummary', f'Informasjon om {ticker} vil bli oppdatert snart.'),
            'employees': stock_data.get('fullTimeEmployees', 'N/A'),
            'country': stock_data.get('country', 'Norge' if ticker.endswith('.OL') else 'USA')
        }
        
        # Copy any additional fields from original stock_data
        for key, value in stock_data.items():
            if key not in enhanced_stock_data:
                enhanced_stock_data[key] = value
        
        # Get technical analysis
        try:
            from ..services.analysis_service import AnalysisService
            technical_data = AnalysisService.get_technical_analysis(ticker)
        except Exception as e:
            current_app.logger.warning(f"Could not get technical analysis for {ticker}: {e}")
            technical_data = {
                'rsi': 'N/A',
                'macd': 'N/A',
                'bollinger_bands': 'N/A',
                'moving_averages': {},
                'recommendation': 'HOLD'
            }
        
        # Get financial news (enhanced)
        try:
            from ..services.data_service import DataService
            news = DataService.get_stock_news(ticker)
        except Exception:
            news = [{
                'title': f'Markedsoppdatering for {ticker}',
                'summary': f'Følg med på utviklingen for {enhanced_stock_data["shortName"]} og andre relaterte aksjer.',
                'url': '#',
                'published': datetime.utcnow().isoformat(),
                'source': 'Aksjeradar'
            }]
        
        return render_template('stocks/details.html',
                             ticker=ticker,
                             stock=enhanced_stock_data,
                             stock_info=enhanced_stock_data,
                             technical=technical_data,
                             news=news,
                             last_updated=datetime.utcnow())
                             
    except Exception as e:
        current_app.logger.error(f"Error loading stock details for {ticker}: {e}")
        
        # Emergency fallback - create minimal but functional data
        fallback_data = {
            'ticker': ticker,
            'shortName': ticker,
            'longName': ticker,
            'regularMarketPrice': 'N/A',
            'regularMarketChange': 'N/A',
            'regularMarketChangePercent': 'N/A',
            'currency': 'NOK' if ticker.endswith('.OL') else 'USD',
            'businessSummary': f'Aksjedata for {ticker} er midlertidig utilgjengelig. Prøv igjen senere.',
            'error_message': 'Data midlertidig utilgjengelig'
        }
        
        return render_template('stocks/details.html',
                             ticker=ticker,
                             stock=fallback_data,
                             stock_info=fallback_data,
                             technical={},
                             news=[],
                             last_updated=datetime.utcnow(),
                             error='Aksjedata er midlertidig utilgjengelig. Vi jobber med å løse problemet.')

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
            title="Oslo Børs",
            market_type="oslo"
        )
    except Exception as e:
        current_app.logger.error(f"Error in oslo_list: {str(e)}")
        flash("En feil oppstod ved henting av Oslo Børs data. Vennligst prøv igjen senere.", "error")
        return render_template('stocks/list.html', title="Oslo Børs", market_type="oslo")

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
            title="Globale markeder"
        )
    except Exception as e:
        current_app.logger.error(f"Error in global stocks list: {str(e)}")
        flash("Kunne ikke hente globale markedsdata. Vennligst prøv igjen senere.", "error")
        return render_template('stocks/list.html', stocks={}, title="Globale markeder", market_type="global")

@stocks.route('/list/crypto')
@access_required
def list_crypto():
    """List cryptocurrencies"""
    try:
        stocks = DataService.get_crypto_overview()
        return render_template(
            'stocks/crypto.html',
            stocks=stocks,
            market_type="crypto",
            title="Kryptovaluta"
        )
    except Exception as e:
        current_app.logger.error(f"Error in crypto list: {str(e)}")
        flash("Kunne ikke hente kryptovalutadata. Vennligst prøv igjen senere.", "error")
        return render_template('stocks/crypto.html', stocks={}, title="Kryptovaluta", market_type="crypto")

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
        
        # Get currency data
        currencies = DataService.get_currency_overview(base=base_currency)
        
        # Ensure we always have a dictionary
        if not isinstance(currencies, dict):
            currencies = {}
        
        # Render template with the data and explicit error state
        return render_template(
            'stocks/currency.html',
            currencies=currencies,
            base_currency=base_currency,
            error=None if currencies else "Kunne ikke hente valutakurser for øyeblikket.",
            title="Valutakurser"
        )
    except Exception as e:
        current_app.logger.error(f"Error in currency_list: {str(e)}")
        # Return template with error state
        return render_template(
            'stocks/currency.html',
            currencies={},
            base_currency=base_currency if base_currency else 'NOK',
            error="En feil oppstod ved henting av valutakurser. Vennligst prøv igjen senere.",
            title="Valutakurser"
        )

@stocks.route('/api/stock/<ticker>')
@access_required
def api_stock(ticker):
    """API endpoint for stock data"""
    try:
        period = request.args.get('period', '1d')
        interval = request.args.get('interval', '1m')
        data = DataService.get_stock_data(ticker, period, interval)
        
        if data.empty:
            return jsonify({'error': 'Ingen data funnet for denne aksjen'}), 404
        
        # Convert DataFrame to JSON-serializable format
        data_reset = data.reset_index()
        result = []
        for _, row in data_reset.iterrows():
            result.append({
                'Date': row['Date'].isoformat() if hasattr(row['Date'], 'isoformat') else str(row['Date']),
                'Open': float(row['Open']),
                'High': float(row['High']),
                'Low': float(row['Low']),
                'Close': float(row['Close']),
                'Volume': int(row['Volume']) if 'Volume' in row else 0
            })
        
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"Error in stock API for {ticker}: {str(e)}")
        return jsonify({'error': 'Kunne ikke hente aksjedata'}), 500

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

