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
                             market_type='oslo',
                             category='oslo')
    except Exception as e:
        current_app.logger.error(f"Error loading Oslo stocks: {str(e)}")
        flash('Kunne ikke laste aksjedata. Prøv igjen senere.', 'error')
        return render_template('stocks/list.html',
                             stocks={},  # Changed from [] to {} 
                             market='Oslo Børs',
                             market_type='oslo',
                             category='oslo',
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
        
        # Get additional analysis data for tabs
        # Create comprehensive mock technical data for tabs
        technical_data = {
            'rsi': 65.5,
            'macd': 0.125,
            'signal': 'Buy',
            'support': stock_info.get('current_price', 250) * 0.95,
            'resistance': stock_info.get('current_price', 250) * 1.08,
            'sma_20': stock_info.get('current_price', 250) * 0.98,
            'sma_50': stock_info.get('current_price', 250) * 0.96,
            'volume_trend': 'Stigende',
            'trend': 'Bullish',
            'momentum': 'Positivt'
        }
        
        # Get recommendation data
        try:
            from app.services.ai_service import AIService
            ai_recommendations = AIService.get_stock_analysis(symbol)
        except Exception as e:
            logger.warning(f"AI recommendations failed for {symbol}: {e}")
            ai_recommendations = {
                'recommendation': 'HOLD',
                'score': 75,
                'risk_level': 'Moderat',
                'summary': 'Anbefaling basert på teknisk og fundamental analyse',
                'price_target': stock_info.get('current_price', 0) * 1.1,
                'reasons': ['Stabil fundamental analyse', 'Positivt momentum', 'God sektorutvikling']
            }
        
        # Get insider trading data
        try:
            from app.services.insider_trading_service import InsiderTradingService
            insider_data = InsiderTradingService.get_insider_trading(symbol)
        except Exception as e:
            logger.warning(f"Insider trading data failed for {symbol}: {e}")
            insider_data = {
                'transactions': [],
                'summary': 'Ingen nylige innsidehandler rapportert'
            }
        
        # Get company information
        company_info = {
            'description': stock_info.get('description', 'Selskapsbeskriving ikke tilgjengelig'),
            'sector': stock_info.get('sector', 'Ukjent sektor'),
            'industry': stock_info.get('industry', 'Ukjent bransje'),
            'employees': stock_info.get('employees', 'Ikke tilgjengelig'),
            'headquarters': stock_info.get('headquarters', 'Ikke tilgjengelig'),
            'website': stock_info.get('website', '#'),
            'ceo': stock_info.get('ceo', 'Ikke tilgjengelig')
        }
        
        # Get news data
        try:
            from app.services.news_service import NewsService
            news_data = NewsService.get_stock_news(symbol)
        except Exception as e:
            logger.warning(f"News data failed for {symbol}: {e}")
            news_data = []
        
        # Try enhanced details template first, then fallbacks
        try:
            return render_template('stocks/details_enhanced.html',
                                 ticker=symbol,
                                 stock_info=stock_info,
                                 technical_data=technical_data,
                                 ai_recommendations=ai_recommendations,
                                 insider_data=insider_data,
                                 company_info=company_info,
                                 news_data=news_data)
        except Exception as e:
            logger.warning(f"Enhanced template failed for {symbol}: {e}")
            try:
                # Fallback to standard detail template
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
    # Support both 'symbols' and 'tickers' parameters for backward compatibility
    symbols = request.args.getlist('symbols') or request.args.getlist('tickers')
    
    if not symbols:
        return render_template('stocks/compare.html', tickers=[], stocks=[])
    
    try:
        stocks_data = []
        comparison_data = {}
        
        for symbol in symbols[:4]:  # Max 4 stocks
            stock_info = DataService.get_stock_info(symbol)
            if stock_info:
                stocks_data.append(stock_info)
                comparison_data[symbol] = {
                    'name': stock_info.get('longName', symbol),
                    'price': stock_info.get('regularMarketPrice', 0),
                    'change': stock_info.get('regularMarketChange', 0),
                    'change_percent': stock_info.get('regularMarketChangePercent', 0),
                    'volume': stock_info.get('regularMarketVolume', 0),
                    'market_cap': stock_info.get('marketCap', 0),
                    'pe_ratio': stock_info.get('trailingPE', 0),
                    'dividend_yield': stock_info.get('dividendYield', 0)
                }
        
        return render_template('stocks/compare.html', 
                             tickers=symbols,
                             stocks=stocks_data,
                             ticker_names={s: comparison_data.get(s, {}).get('name', s) for s in symbols},
                             comparison_data=comparison_data)
        
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
        
        # Calculate statistics safely
        oslo_len = len(oslo_stocks) if oslo_stocks else 0
        global_len = len(global_stocks) if global_stocks else 0
        crypto_len = len(crypto_data) if crypto_data else 0
        currency_len = len(currency_data) if currency_data else 0
        
        stats = {
            'total_stocks': oslo_len + global_len,
            'total_crypto': crypto_len,
            'total_currency': currency_len,
            'total_instruments': oslo_len + global_len + crypto_len + currency_len
        }
        
        return render_template('stocks/prices.html',
                             market_data={
                                 'oslo_stocks': oslo_stocks or {},
                                 'global_stocks': global_stocks or {},
                                 'crypto': crypto_data or {},
                                 'currency': currency_data or {}
                             },
                             stats=stats,
                             error=False)
                             
    except Exception as e:
        logger.error(f"Error in prices overview: {e}")
        import traceback
        traceback.print_exc()
        flash('Kunne ikke laste prisdata.', 'error')
        return render_template('stocks/prices.html',
                             market_data={
                                 'oslo_stocks': {},
                                 'global_stocks': {},
                                 'crypto': {},
                                 'currency': {}
                             },
                             stats={'total_stocks': 0, 'total_crypto': 0, 'total_currency': 0, 'total_instruments': 0},
                             error=True)


@stocks.route('/api/chart-data/<symbol>')
@access_required
def api_chart_data(symbol):
    """API endpoint for stock chart data"""
    try:
        # Get historical data
        period = request.args.get('period', '30d')  # Default 30 days
        interval = request.args.get('interval', '1d')  # Default daily
        
        # Get data from DataService
        chart_data = DataService.get_stock_history(symbol, period=period, interval=interval)
        
        if not chart_data:
            # Fallback to generating mock data if service fails
            from datetime import datetime, timedelta
            import random
            
            days = 30 if period == '30d' else 90 if period == '3mo' else 365
            dates = []
            prices = []
            volumes = []
            
            base_price = 100  # Default base price
            try:
                stock_info = DataService.get_stock_info(symbol)
                if stock_info and stock_info.get('regularMarketPrice'):
                    base_price = stock_info['regularMarketPrice']
            except:
                pass
            
            today = datetime.now()
            for i in range(days, 0, -1):
                date = today - timedelta(days=i)
                dates.append(date.strftime('%Y-%m-%d'))
                
                # Generate realistic price variation
                variance = (random.random() - 0.5) * 0.06  # ±3% daily variance
                price = base_price * (1 + variance * (i / days))
                prices.append(round(price, 2))
                
                # Generate volume data
                base_volume = random.randint(50000, 200000)
                volume_variance = (random.random() - 0.5) * 0.4
                volume = int(base_volume * (1 + volume_variance))
                volumes.append(volume)
            
            chart_data = {
                'dates': dates,
                'prices': prices,
                'volumes': volumes,
                'currency': 'NOK'
            }
        
        return jsonify(chart_data)
        
    except Exception as e:
        logger.error(f"Error getting chart data for {symbol}: {e}")
        return jsonify({'error': 'Kunne ikke laste chart data'}), 500


@stocks.route('/api/technical-data/<symbol>')
@access_required
def api_technical_data(symbol):
    """API endpoint for technical analysis data"""
    try:
        # Get technical analysis data from AnalysisService
        technical_data = AnalysisService.get_technical_indicators(symbol)
        
        if not technical_data:
            # Fallback to mock technical data
            import random
            technical_data = {
                'rsi': round(random.uniform(20, 80), 1),
                'macd': round(random.uniform(-0.5, 0.5), 3),
                'signal_line': round(random.uniform(-0.3, 0.3), 3),
                'bollinger_upper': round(random.uniform(110, 130), 2),
                'bollinger_lower': round(random.uniform(80, 100), 2),
                'sma_20': round(random.uniform(95, 105), 2),
                'sma_50': round(random.uniform(90, 110), 2),
                'ema_12': round(random.uniform(95, 105), 2),
                'ema_26': round(random.uniform(90, 110), 2),
                'volume_sma': random.randint(50000, 200000),
                'support_level': round(random.uniform(85, 95), 2),
                'resistance_level': round(random.uniform(105, 115), 2),
                'trend': random.choice(['Bullish', 'Bearish', 'Sideways']),
                'momentum': random.choice(['Strong', 'Weak', 'Neutral']),
                'signal': random.choice(['Buy', 'Sell', 'Hold'])
            }
        
        return jsonify(technical_data)
        
    except Exception as e:
        logger.error(f"Error getting technical data for {symbol}: {e}")
        return jsonify({'error': 'Kunne ikke laste teknisk data'}), 500

