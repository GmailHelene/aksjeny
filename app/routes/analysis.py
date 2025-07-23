from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory, session
from flask_login import current_user, login_required
from ..services.analysis_service import AnalysisService
from ..services.advanced_technical_service import AdvancedTechnicalService
from ..services.ai_service import AIService
from ..services.data_service import DataService, OSLO_BORS_TICKERS, GLOBAL_TICKERS
from ..services.usage_tracker import usage_tracker
from ..utils.access_control import access_required, demo_access
from ..models.user import User
from ..models.portfolio import Portfolio, PortfolioStock
import random
import pandas as pd
import time
import logging
from datetime import datetime, timedelta

# Set up logger
logger = logging.getLogger(__name__)

def get_all_available_stocks():
    """Aggregate all available tickers from Oslo Børs, global, and crypto."""
    oslo = DataService.get_oslo_bors_overview() or {}
    global_ = DataService.get_global_stocks_overview() or {}
    crypto = DataService.get_crypto_overview() or {}
    # All dicts are {ticker: info}
    all_stocks = {}
    all_stocks.update(oslo)
    all_stocks.update(global_)
    all_stocks.update(crypto)
    return list(all_stocks.keys())


analysis = Blueprint('analysis', __name__, url_prefix='/analysis')

@analysis.route('/')
@access_required
def index():
    """Analysis main page - prevent redirect loops"""
    try:
        return render_template('analysis/index.html',
                             page_title="Analyse")
    except Exception as e:
        logger.error(f"Error in analysis index: {e}")
        flash('Kunne ikke laste analysesiden.', 'error')
        return render_template('analysis/index.html',
                             page_title="Analyse",
                             error="Siden kunne ikke lastes")

@analysis.route('/technical')
@analysis.route('/technical/')
@access_required  
def technical():
    """Advanced Technical analysis with comprehensive indicators and patterns"""
    try:
        symbol = request.args.get('symbol')
        
        if symbol:
            # Get comprehensive technical analysis
            technical_data = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
            
            # Convert to template-friendly format
            template_data = {
                'last_price': technical_data['current_price'],
                'change': technical_data['change'],
                'change_percent': technical_data['change_percent'],
                'volume': technical_data['volume'],
                'avg_volume': technical_data['avg_volume'],
                'rsi': technical_data['indicators']['rsi'],
                'macd': technical_data['indicators']['macd'],
                'macd_signal': technical_data['indicators']['macd_signal'],
                'sma20': technical_data['indicators']['sma_20'],
                'sma50': technical_data['indicators']['sma_50'],
                'sma200': technical_data['indicators']['sma_200'],
                'support': technical_data['support_resistance']['support_levels'][0]['level'] if technical_data['support_resistance']['support_levels'] else 0,
                'resistance': technical_data['support_resistance']['resistance_levels'][0]['level'] if technical_data['support_resistance']['resistance_levels'] else 0,
                'signal': technical_data['signals']['overall_signal'],
                'overall_signal': technical_data['signals']['overall_signal'],
                'signal_reason': technical_data['signals']['recommendation'],
                
                # Additional advanced data
                'patterns': technical_data['patterns'],
                'support_resistance': technical_data['support_resistance'],
                'sentiment': technical_data['sentiment'],
                'chart_data': technical_data['chart_data'],
                'stochastic_k': technical_data['indicators']['stochastic_k'],
                'williams_r': technical_data['indicators']['williams_r'],
                'bollinger_upper': technical_data['indicators']['bollinger_upper'],
                'bollinger_lower': technical_data['indicators']['bollinger_lower']
            }
            
            # Convert popular stocks to objects
            popular_stocks = []
            oslo_tickers = ['EQNR.OL', 'DNB.OL', 'YAR.OL', 'MOWI.OL', 'TEL.OL']
            global_tickers = ['AAPL', 'TSLA', 'MSFT', 'AMZN', 'GOOGL']
            
            for ticker in oslo_tickers + global_tickers:
                if ticker != symbol:  # Don't include current symbol
                    from types import SimpleNamespace
                    stock = SimpleNamespace()
                    stock.symbol = ticker
                    stock.name = ticker
                    popular_stocks.append(stock)
            
            return render_template('analysis/technical.html',
                                 symbol=symbol,
                                 technical_data=template_data,
                                 advanced_data=technical_data,
                                 popular_stocks=popular_stocks[:8],  # Limit to 8
                                 show_analysis=True)
        else:
            # Show technical analysis overview with popular stocks
            popular_stocks = []
            oslo_tickers = ['EQNR.OL', 'DNB.OL', 'YAR.OL', 'MOWI.OL', 'TEL.OL']
            global_tickers = ['AAPL', 'TSLA', 'MSFT', 'AMZN', 'GOOGL']
            
            for ticker in oslo_tickers + global_tickers:
                from types import SimpleNamespace
                stock = SimpleNamespace()
                stock.symbol = ticker
                stock.name = ticker
                popular_stocks.append(stock)
            
            return render_template('analysis/technical.html',
                                 popular_stocks=popular_stocks,
                                 show_analysis=False)
                                 
    except Exception as e:
        logger.error(f"Error in technical analysis: {e}")
        # Return fallback data
        fallback_data = {
            'last_price': 100.0,
            'change': 0.0,
            'change_percent': 0.0,
            'rsi': 50.0,
            'macd': 0.0,
            'signal': 'HOLD',
            'signal_reason': 'Teknisk analyse ikke tilgjengelig'
        }
        return render_template('analysis/technical.html',
                             symbol=request.args.get('symbol', ''),
                             technical_data=fallback_data,
                             show_analysis=bool(request.args.get('symbol')),
                             error="Kunne ikke laste teknisk analyse")

@analysis.route('/api/technical/<symbol>')
@access_required
def api_technical_data(symbol):
    """API endpoint for real-time technical data"""
    try:
        # Get comprehensive analysis
        analysis = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
        
        # Return JSON data for AJAX requests
        return jsonify({
            'success': True,
            'data': {
                'ticker': analysis['ticker'],
                'current_price': analysis['current_price'],
                'change': analysis['change'],
                'change_percent': analysis['change_percent'],
                'volume': analysis['volume'],
                'indicators': {
                    'rsi': round(analysis['indicators']['rsi'], 1),
                    'macd': round(analysis['indicators']['macd'], 3),
                    'macd_signal': round(analysis['indicators']['macd_signal'], 3),
                    'sma_20': round(analysis['indicators']['sma_20'], 2),
                    'sma_50': round(analysis['indicators']['sma_50'], 2),
                    'sma_200': round(analysis['indicators']['sma_200'], 2)
                },
                'signals': analysis['signals'],
                'sentiment': analysis['sentiment'],
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in API technical data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis.route('/api/chart-data/<symbol>')
@access_required
def api_chart_data(symbol):
    """API endpoint for advanced chart data with multiple timeframes"""
    try:
        timeframe = request.args.get('timeframe', '1M')
        chart_type = request.args.get('chart_type', 'line')
        
        # Get comprehensive analysis
        analysis = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
        
        # Generate timeframe-specific data
        chart_data = AdvancedTechnicalService._generate_chart_data_for_timeframe(
            symbol, timeframe, chart_type
        )
        
        return jsonify({
            'success': True,
            'data': {
                'chart_data': chart_data,
                'support_resistance': analysis['support_resistance'],
                'indicators': analysis['indicators'],
                'timeframe': timeframe,
                'chart_type': chart_type,
                'patterns': analysis['patterns'],
                'volume_profile': analysis.get('volume_profile', {}),
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in API chart data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis.route('/api/indicators/<symbol>')
@access_required  
def api_indicators(symbol):
    """API endpoint for technical indicators only"""
    try:
        # Get specific indicators
        analysis = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
        
        return jsonify({
            'success': True,
            'data': {
                'rsi': analysis['indicators']['rsi'],
                'macd': analysis['indicators']['macd'],
                'macd_signal': analysis['indicators']['macd_signal'],
                'macd_histogram': analysis['indicators'].get('macd_histogram', 0),
                'stochastic_k': analysis['indicators']['stochastic_k'],
                'stochastic_d': analysis['indicators'].get('stochastic_d', 0),
                'williams_r': analysis['indicators']['williams_r'],
                'cci': analysis['indicators'].get('cci', 0),
                'atr': analysis['indicators'].get('atr', 0),
                'adx': analysis['indicators'].get('adx', 0),
                'bollinger_upper': analysis['indicators']['bollinger_upper'],
                'bollinger_lower': analysis['indicators']['bollinger_lower'],
                'bollinger_position': analysis['indicators'].get('bollinger_position', 'middle'),
                'sma_20': analysis['indicators']['sma_20'],
                'sma_50': analysis['indicators']['sma_50'],
                'sma_200': analysis['indicators']['sma_200'],
                'ema_12': analysis['indicators'].get('ema_12', 0),
                'ema_26': analysis['indicators'].get('ema_26', 0),
                'volume_sma': analysis['indicators'].get('volume_sma', 0),
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in API indicators for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis.route('/api/patterns/<symbol>')
@access_required
def api_patterns(symbol):
    """API endpoint for pattern detection"""
    try:
        analysis = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
        
        return jsonify({
            'success': True,
            'data': {
                'candlestick_patterns': analysis['patterns']['candlestick_patterns'],
                'chart_patterns': analysis['patterns']['chart_patterns'],
                'trend_patterns': analysis['patterns'].get('trend_patterns', []),
                'reversal_signals': analysis['patterns'].get('reversal_signals', []),
                'continuation_signals': analysis['patterns'].get('continuation_signals', []),
                'pattern_strength': analysis['patterns'].get('pattern_strength', 'medium'),
                'pattern_reliability': analysis['patterns'].get('pattern_reliability', 0.6),
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in API patterns for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis.route('/api/sentiment/<symbol>')
@access_required
def api_sentiment(symbol):
    """API endpoint for market sentiment analysis"""
    try:
        analysis = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
        
        return jsonify({
            'success': True,
            'data': {
                'overall_sentiment': analysis['sentiment']['sentiment'],
                'sentiment_score': analysis['sentiment']['score'],
                'sentiment_reasons': analysis['sentiment'].get('reasons', []),
                'market_mood': analysis['sentiment'].get('market_mood', 'neutral'),
                'fear_greed_index': analysis['sentiment'].get('fear_greed_index', 50),
                'social_sentiment': analysis['sentiment'].get('social_sentiment', {}),
                'institutional_flow': analysis['sentiment'].get('institutional_flow', 'neutral'),
                'retail_sentiment': analysis['sentiment'].get('retail_sentiment', 'neutral'),
                'options_flow': analysis['sentiment'].get('options_flow', {}),
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in API sentiment for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis.route('/api/realtime/<symbol>')
@access_required
def api_realtime_data(symbol):
    """API endpoint for real-time streaming data"""
    try:
        # Get latest data
        analysis = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
        
        # Simulate real-time price movement
        import random
        base_price = analysis['current_price']
        price_change = random.uniform(-0.02, 0.02)  # ±2% movement
        new_price = base_price * (1 + price_change)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol.upper(),
                'price': round(new_price, 2),
                'change': round(new_price - base_price, 2),
                'change_percent': round(price_change * 100, 2),
                'volume': analysis['volume'] + random.randint(-50000, 100000),
                'bid': round(new_price * 0.999, 2),
                'ask': round(new_price * 1.001, 2),
                'high_24h': round(max(base_price, new_price) * 1.02, 2),
                'low_24h': round(min(base_price, new_price) * 0.98, 2),
                'timestamp': datetime.now().isoformat(),
                'market_status': 'open'  # Would be actual market status
            }
        })
        
    except Exception as e:
        logger.error(f"Error in API realtime data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis.route('/api/alerts/<symbol>')
@access_required
def api_trading_alerts(symbol):
    """API endpoint for AI-generated trading alerts"""
    try:
        analysis = AdvancedTechnicalService.get_comprehensive_analysis(symbol.upper())
        
        # Generate AI trading alerts based on analysis
        alerts = []
        
        # RSI alerts
        rsi = analysis['indicators']['rsi']
        if rsi > 75:
            alerts.append({
                'type': 'warning',
                'indicator': 'RSI',
                'message': f'RSI overkjøpt på {rsi:.1f} - vurder salg',
                'severity': 'high',
                'action': 'sell_signal'
            })
        elif rsi < 25:
            alerts.append({
                'type': 'opportunity',
                'indicator': 'RSI',
                'message': f'RSI oversolgt på {rsi:.1f} - kjøpsmulighet',
                'severity': 'high',
                'action': 'buy_signal'
            })
        
        # MACD alerts
        macd = analysis['indicators']['macd']
        macd_signal = analysis['indicators']['macd_signal']
        if macd > macd_signal and macd > 0:
            alerts.append({
                'type': 'bullish',
                'indicator': 'MACD',
                'message': 'MACD bullish crossover - oppgang forventet',
                'severity': 'medium',
                'action': 'buy_signal'
            })
        elif macd < macd_signal and macd < 0:
            alerts.append({
                'type': 'bearish',
                'indicator': 'MACD',
                'message': 'MACD bearish crossover - nedgang forventet',
                'severity': 'medium',
                'action': 'sell_signal'
            })
        
        # Pattern alerts
        for pattern in analysis['patterns']['chart_patterns']:
            if pattern['type'] in ['breakout', 'triangle_breakout']:
                alerts.append({
                    'type': 'pattern',
                    'indicator': 'Pattern',
                    'message': f'{pattern["name"]} detektert - potensielt utbrudd',
                    'severity': 'high',
                    'action': 'watch_signal'
                })
        
        # Volume alerts
        if analysis['volume'] > analysis.get('avg_volume', 0) * 1.5:
            alerts.append({
                'type': 'volume',
                'indicator': 'Volume',
                'message': 'Uvanlig høyt volum - økt interesse',
                'severity': 'medium',
                'action': 'watch_signal'
            })
        
        return jsonify({
            'success': True,
            'data': {
                'alerts': alerts,
                'alert_count': len(alerts),
                'high_severity_count': len([a for a in alerts if a['severity'] == 'high']),
                'recommended_action': analysis['signals']['overall_signal'],
                'confidence_score': analysis['signals'].get('confidence', 0.7),
                'timestamp': analysis['timestamp']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in API alerts for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    except Exception as e:
        logger.error(f"Error in API chart data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analysis.route('/market-overview')
@access_required
def market_overview():
    """Market overview page with fixed styling"""
    try:
        # Get all market data
        oslo_data = DataService.get_oslo_bors_overview() or {}
        global_data = DataService.get_global_stocks_overview() or {}
        crypto_data = DataService.get_crypto_overview() or {}
        currency_data = DataService.get_currency_overview() or {}
        
        # Convert dictionaries to objects with attributes for template compatibility
        from types import SimpleNamespace
        
        # Convert crypto data to have proper attributes
        converted_crypto = {}
        for symbol, data in crypto_data.items():
            if isinstance(data, dict):
                converted_crypto[symbol] = SimpleNamespace(
                    price=data.get('price', 0),
                    change_24h=data.get('change_24h', data.get('change_percent', 0)),
                    volume=data.get('volume', 0),
                    signal=data.get('signal', 'HOLD')
                )
            else:
                converted_crypto[symbol] = data
                
        # Convert currency data to have proper attributes  
        converted_currency = {}
        for symbol, data in currency_data.items():
            if isinstance(data, dict):
                converted_currency[symbol] = SimpleNamespace(
                    last_price=data.get('last_price', 0),
                    change_24h=data.get('change_24h', data.get('change_percent', 0)),
                    change=data.get('change', 0),
                    volume=data.get('volume', 0),
                    signal=data.get('signal', 'HOLD'),
                    name=data.get('name', symbol)
                )
            else:
                converted_currency[symbol] = data
        
        # Get market summaries with proper structure for template
        market_summaries = SimpleNamespace()
        market_summaries.oslo = SimpleNamespace(
            index_value=1567.8,
            change=12.4,
            change_percent=0.8
        )
        market_summaries.global_market = SimpleNamespace(
            index_value=4592.1,
            change=-23.7,
            change_percent=-0.5
        )
        market_summaries.crypto = SimpleNamespace(
            change_percent=2.3,
            change=15.4,
            total_market_cap=2500000000000
        )
        market_summaries.currency = SimpleNamespace(
            usd_nok=10.8,
            usd_nok_change=0.05
        )
        
        return render_template('analysis/market_overview.html',
                             oslo_stocks=oslo_data,
                             global_stocks=global_data,
                             crypto_data=converted_crypto,
                             currency_data=converted_currency,
                             market_summaries=market_summaries)
                             
    except Exception as e:
        logger.error(f"Error in market overview: {e}")
        # Create proper fallback SimpleNamespace objects for error handling
        from types import SimpleNamespace
        fallback_summaries = SimpleNamespace()
        fallback_summaries.oslo = SimpleNamespace(index_value=0, change=0, change_percent=0)
        fallback_summaries.global_market = SimpleNamespace(index_value=0, change=0, change_percent=0)
        fallback_summaries.crypto = SimpleNamespace(change_percent=0, change=0, total_market_cap=0)
        fallback_summaries.currency = SimpleNamespace(usd_nok=0, usd_nok_change=0)
        
        flash('Kunne ikke laste markedsdata. Prøv igjen senere.', 'error')
        return render_template('analysis/market_overview.html',
                             oslo_stocks={},
                             global_stocks={},
                             crypto_data={},
                             currency_data={},
                             market_summaries=fallback_summaries,
                             error=True)

@analysis.route('/warren-buffett', methods=['GET', 'POST'])
@access_required
def warren_buffett():
    """Warren Buffett analysis with improved error handling"""
    try:
        ticker = request.args.get('ticker') or request.form.get('ticker')
        
        if ticker and request.method in ['GET', 'POST']:
            try:
                # Import the service here to avoid circular imports
                from ..services.buffett_analysis_service import BuffettAnalysisService
                analysis_data = BuffettAnalysisService.analyze_stock(ticker)
                
                if analysis_data:
                    return render_template('analysis/warren_buffett.html',
                                         analysis=analysis_data,
                                         ticker=ticker)
                else:
                    flash(f'Kunne ikke analysere {ticker}. Prøv en annen aksje.', 'warning')
            except ImportError:
                logger.error("BuffettAnalysisService not available")
                flash('Analyse-tjenesten er midlertidig utilgjengelig.', 'error')
            except Exception as e:
                logger.error(f"Error in Warren Buffett analysis for {ticker}: {e}")
                flash('Feil ved analyse. Prøv igjen senere.', 'error')
        
        # Show selection page
        try:
            oslo_stocks = DataService.get_oslo_bors_overview() or {}
            global_stocks = DataService.get_global_stocks_overview() or {}
            
            return render_template('analysis/warren_buffett.html',
                                 oslo_stocks=oslo_stocks,
                                 global_stocks=global_stocks,
                                 analysis=None)
        except Exception as e:
            logger.error(f"Error loading Warren Buffett selection page: {e}")
            # Return minimal safe template
            return render_template('analysis/warren_buffett.html',
                                 oslo_stocks={},
                                 global_stocks={},
                                 analysis=None,
                                 error="Kunne ikke laste aksjedata")
                                 
    except Exception as e:
        logger.error(f"Critical error in Warren Buffett route: {e}")
        flash('Siden kunne ikke lastes. Prøv igjen senere.', 'error')
        return redirect(url_for('analysis.index'))

@analysis.route('/benjamin-graham', methods=['GET', 'POST'])
@access_required
def benjamin_graham():
    """Benjamin Graham analysis with improved error handling"""
    try:
        ticker = request.args.get('ticker') or request.form.get('ticker')
        
        if ticker and request.method in ['GET', 'POST']:
            try:
                # Import the service here to avoid circular imports
                from ..services.graham_analysis_service import GrahamAnalysisService
                analysis_data = GrahamAnalysisService.analyze_stock(ticker)
                
                if analysis_data and not analysis_data.get('error'):
                    logger.info(f"Successfully analyzed {ticker} using Graham Analysis")
                    return render_template('analysis/benjamin_graham.html',
                                         analysis=analysis_data,
                                         ticker=ticker)
                else:
                    logger.warning(f'Graham analysis failed for {ticker}')
                    flash(f'Kunne ikke analysere {ticker}. Prøv en annen aksje.', 'warning')
            except ImportError:
                logger.error("GrahamAnalysisService not available")
                flash('Analyse-tjenesten er midlertidig utilgjengelig.', 'error')
            except Exception as e:
                logger.error(f"Error in Benjamin Graham analysis for {ticker}: {e}")
                flash('Feil ved analyse. Prøv igjen senere.', 'error')
        
        # Show selection page
        try:
            oslo_stocks = DataService.get_oslo_bors_overview() or {}
            global_stocks = DataService.get_global_stocks_overview() or {}
            
            return render_template('analysis/benjamin_graham.html',
                                 oslo_stocks=oslo_stocks,
                                 global_stocks=global_stocks,
                                 analysis=None)
        except Exception as e:
            logger.error(f"Error loading Benjamin Graham selection page: {e}")
            # Return minimal safe template
            return render_template('analysis/benjamin_graham.html',
                                 oslo_stocks={},
                                 global_stocks={},
                                 analysis=None,
                                 error="Kunne ikke laste aksjedata")
                                 
    except Exception as e:
        logger.error(f"Critical error in Benjamin Graham route: {e}")
        flash('Siden kunne ikke lastes. Prøv igjen senere.', 'error')
        return redirect(url_for('analysis.index'))
    
    # GET request
    try:
        # Get popular stocks from Oslo Børs data
        oslo_stocks = DataService.get_oslo_bors_overview() or {}
        popular_stocks = list(oslo_stocks.keys())[:10] if oslo_stocks else ['EQNR.OL', 'DNB.OL', 'MOWI.OL']
        
        # Ensure we always have some popular stocks
        if not popular_stocks:
            popular_stocks = ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL']
        
        logger.info(f"Loading Benjamin Graham page with {len(popular_stocks)} popular stocks")
        return render_template('analysis/benjamin_graham.html',
                             popular_stocks=popular_stocks,
                             show_results=False)
    except Exception as e:
        logger.error(f"Error loading Benjamin Graham page: {e}")
        return render_template('analysis/benjamin_graham.html',
                             popular_stocks=['EQNR.OL', 'DNB.OL', 'TEL.OL'],
                             show_results=False,
                             error="Noen funksjoner kan være begrenset")

@analysis.route('/sentiment-view')
@access_required
def sentiment_view():
    """Social sentiment analysis"""
    try:
        ticker = request.args.get('ticker')
        
        if ticker:
            # Return sentiment analysis for specific ticker
            sentiment_data = {
                'ticker': ticker.upper(),
                'company_name': ticker.upper(),
                'overall_sentiment': random.choice(['Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative']),
                'sentiment_score': round(random.uniform(0, 100), 1),
                'sources': {
                    'reddit': {'score': round(random.uniform(0, 100), 1), 'posts': random.randint(50, 500)},
                    'twitter': {'score': round(random.uniform(0, 100), 1), 'tweets': random.randint(100, 1000)},
                    'news': {'score': round(random.uniform(0, 100), 1), 'articles': random.randint(10, 50)},
                    'forums': {'score': round(random.uniform(0, 100), 1), 'discussions': random.randint(20, 200)}
                },
                'trending_topics': ['earnings', 'growth', 'competition', 'innovation'],
                'recommendation': random.choice(['Buy', 'Hold', 'Sell']),
                'analysis_date': datetime.now().strftime('%Y-%m-%d')
            }
            return render_template('analysis/sentiment.html', 
                                 sentiment=sentiment_data, 
                                 ticker=ticker)
        
        return render_template('analysis/sentiment.html')
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        flash("En feil oppstod ved lasting av sentiment-analysen.", "error")
        return redirect(url_for('analysis.index'))

@analysis.route('/screener')
@access_required  
def screener():
    """Redirect to screener view"""
    return redirect(url_for('analysis.screener_view'))

@analysis.route('/screener-view', methods=['GET', 'POST'])
@demo_access
def screener_view():
    """Advanced stock screening tool with Finviz integration"""
    try:
        # Import finviz service
        from app.services.finviz_service import FinvizScreenerService
        finviz_service = FinvizScreenerService()
        
        # Get available filters and presets
        available_filters = finviz_service.get_available_filters()
        preset_screens = finviz_service.get_preset_screens()
        
        results = []
        selected_filters = []
        show_results = False
        
        # Filter display name function for template
        def get_filter_display_name(filter_key):
            filter_names = {
                'cap_mega': 'Mega Cap (>$200B)',
                'cap_large': 'Large Cap (>$10B)', 
                'cap_mid': 'Mid Cap ($2B-$10B)',
                'cap_small': 'Small Cap (<$2B)',
                'nasdaq': 'NASDAQ',
                'nyse': 'NYSE',
                'sp500': 'S&P 500',
                'sp400': 'S&P 400',
                'sp600': 'S&P 600',
                'nasdaq100': 'NASDAQ 100',
                'russell2000': 'Russell 2000',
                'tech': 'Teknologi',
                'healthcare': 'Helsevesen',
                'finance': 'Finans',
                'energy': 'Energi',
                'consumer': 'Forbruksvarer',
                'industrial': 'Industri',
                'utilities': 'Utilities',
                'realestate': 'Eiendom',
                'materials': 'Materialer',
                'pe_low': 'Lav P/E (<15)',
                'pe_profitable': 'Profitabel (P/E>0)',
                'pe_high': 'Høy P/E (>50)',
                'peg_low': 'Lav PEG (<1)',
                'pb_low': 'Lav P/B (<1)',
                'ps_low': 'Lav P/S (<1)',
                'perf_week_up': 'Uke +',
                'perf_month_up': 'Måned +',
                'perf_ytd_up': 'YTD +',
                'perf_year_up': 'År +',
                'rsi_oversold': 'RSI Oversolgt (<30)',
                'rsi_overbought': 'RSI Overkjøpt (>70)',
                'price_near_high': 'Nær 52W høy',
                'price_near_low': 'Nær 52W lav',
                'volume_high': 'Høyt volum (>2M)',
                'dividend_yield': 'Utbytte >0%',
                'dividend_high': 'Høyt utbytte (>5%)',
                'roe_high': 'ROE >0%',
                'roa_high': 'ROA >0%',
                'debt_low': 'Lav gjeld (<0.5)',
                'current_ratio_high': 'Høy likviditet (>1.5)',
                'sales_growth': 'Salgsvekst 5Y+',
                'eps_growth': 'EPS vekst 5Y+',
                'earnings_growth': 'Inntjeningsvekst+'
            }
            return filter_names.get(filter_key, filter_key)
        
        if request.method == 'POST':
            show_results = True
            
            # Check for preset selection
            preset = request.form.get('preset')
            if preset and preset in preset_screens:
                # Use preset filters
                selected_filters = list(preset_screens[preset])
                results = finviz_service.screen_stocks(selected_filters)
                flash(f'Bruker preset: {preset}', 'info')
            else:
                # Use custom filters
                selected_filters = request.form.getlist('filters')
                if selected_filters:
                    # Build filter dict from selected filters  
                    # Just pass the list directly since screen_stocks expects a list
                    results = finviz_service.screen_stocks(selected_filters)
                    if results:
                        flash(f'Fant {len(results)} aksjer som oppfyller kriteriene', 'success')
                    else:
                        flash('Ingen gyldige filtere valgt', 'warning')
                else:
                    flash('Velg minst ett filter eller preset', 'warning')
        
        return render_template('analysis/screener.html',
                             available_filters=available_filters,
                             preset_screens=preset_screens,
                             results=results,
                             selected_filters=selected_filters,
                             show_results=show_results,
                             get_filter_display_name=get_filter_display_name)
    
    except Exception as e:
        logger.error(f"Screener error: {str(e)}")
        flash('Det oppstod en feil med screeneren. Prøv igjen senere.', 'error')
        return render_template('analysis/screener.html',
                             available_filters={},
                             preset_screens={},
                             results=[],
                             selected_filters=[],
                             show_results=False,
                             get_filter_display_name=lambda x: x)

# Removed duplicate short-analysis-view route to avoid conflicts

@analysis.route('/currency-overview')
@access_required
def currency_overview():
    """Currency market overview page"""
    try:
        # Get currency data
        currency_data = DataService.get_currency_overview()
        
        # Get economic indicators that affect currencies
        indicators = DataService.get_economic_indicators()
        
        return render_template('analysis/currency_overview.html',
                             currency_data=currency_data,
                             indicators=indicators)
                             
    except Exception as e:
        logger.error(f"Error in currency overview: {e}")
        flash('Kunne ikke laste valutaoversikt.', 'error')
        return redirect(url_for('analysis.index'))

@analysis.route('/prediction', methods=['GET', 'POST'])
@access_required
def prediction():
    """Show price predictions for multiple stocks"""
    try:
        # Tickers vi vet fungerer
        tickers_oslo = ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL']
        tickers_global = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA']
        
        predictions_oslo = {}
        predictions_global = {}
        
        # Legg til konkrete demoprediksjoner for Oslo Børs
        for ticker in tickers_oslo:
            predictions_oslo[ticker] = {
                'ticker': ticker,
                'last_price': round(300 + 10 * tickers_oslo.index(ticker), 2),
                'next_price': round(300 + 10 * tickers_oslo.index(ticker) * 1.02, 2),
                'change_percent': round(2.0 - 0.2 * tickers_oslo.index(ticker), 2),
                'trend': 'UP' if tickers_oslo.index(ticker) % 3 != 0 else 'DOWN',
                'confidence': 'HIGH' if tickers_oslo.index(ticker) % 3 == 0 else ('MEDIUM' if tickers_oslo.index(ticker) % 3 == 1 else 'LOW'),
                'last_update': '2025-06-17',
                'volatility': round(2.0 + 0.5 * tickers_oslo.index(ticker), 2),
                'trend_period': '5 dager',
                'data_period': '60 dager',
                'prediction_reason': f"Begrunnelse: Sterk positiv trend siste 5 dager • Kursen er over 50-dagers glidende gjennomsnitt • {tickers_oslo.index(ticker) % 3 == 0 and 'Høy' or 'Moderat'} volatilitet indikerer {tickers_oslo.index(ticker) % 3 == 0 and 'usikkerhet' or 'stabilitet'}"
            }
        
        # Legg til konkrete demoprediksjoner for globale aksjer
        for ticker in tickers_global:
            predictions_global[ticker] = {
                'ticker': ticker,
                'last_price': round(150 + 20 * tickers_global.index(ticker), 2),
                'next_price': round((150 + 20 * tickers_global.index(ticker)) * (1 + ((-1) ** tickers_global.index(ticker)) * 0.01), 2),
                'change_percent': round(((-1) ** tickers_global.index(ticker)) * (1.5 + 0.2 * tickers_global.index(ticker)), 2),
                'trend': 'UP' if tickers_global.index(ticker) % 2 == 0 else 'DOWN',
                'confidence': 'HIGH' if tickers_global.index(ticker) % 3 == 0 else ('MEDIUM' if tickers_global.index(ticker) % 3 == 1 else 'LOW'),
                'last_update': '2025-06-17',
                'volatility': round(1.5 + 0.3 * tickers_global.index(ticker), 2),
                'trend_period': '5 dager',
                'data_period': '60 dager',
                'prediction_reason': f"Begrunnelse: {tickers_global.index(ticker) % 2 == 0 and 'Positiv' or 'Negativ'} trend siste 5 dager • Kursen er {tickers_global.index(ticker) % 2 == 0 and 'over' or 'under'} 50-dagers glidende gjennomsnitt • {tickers_global.index(ticker) % 3 == 0 and 'Høy' or 'Moderat'} konfidens i prognosen"
            }
        
        return render_template(
            'analysis/prediction.html',
            predictions_oslo=predictions_oslo,
            predictions_global=predictions_global
        )
    except Exception as e:
        print(f"Error in prediction route: {str(e)}")
        return render_template(
            'error.html', 
            error=f"Det oppstod en feil ved generering av prediksjoner: {str(e)}"
        )

@analysis.route('/recommendation')
@access_required
def recommendation():
    ticker = request.args.get('ticker')
    if not ticker:
        # Vis velg-ticker-side
        oslo_stocks = DataService.get_oslo_bors_overview()
        global_stocks = DataService.get_global_stocks_overview()
        return render_template('analysis/recommendation_select.html',
                               oslo_stocks=oslo_stocks,
                               global_stocks=global_stocks)
    try:
        # Hent anbefaling fra AnalysisService
        recommendation = AnalysisService.get_recommendation(ticker)
        if not recommendation:
            return render_template('analysis/recommendation.html',
                                   ticker=ticker,
                                   error="Ingen anbefaling tilgjengelig for denne aksjen akkurat nå.")
        return render_template('analysis/recommendation.html',
                               ticker=ticker,
                               recommendation=recommendation.get('recommendation'),
                               summary=recommendation.get('summary'),
                               technical_signal=recommendation.get('technical_signal'),
                               rsi=recommendation.get('rsi'),
                               macd=recommendation.get('macd'),
                               volume=recommendation.get('volume'),
                               details=recommendation.get('details'))
    except Exception as e:
        current_app.logger.error(f"Error in recommendation for {ticker}: {str(e)}")
        return render_template('analysis/recommendation.html',
                               ticker=ticker,
                               error="Beklager, en feil oppstod. Vi jobber med å løse problemet...")

@analysis.route('/ai', methods=['GET', 'POST'])
@access_required
def ai():
    """AI analysis view with popular stocks"""
    ticker = request.args.get('ticker')
    
    # Define popular stocks for AI analysis
    popular_stocks = {
        'oslo': ['EQNR.OL', 'DNB.OL', 'MOWI.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
        'global': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'],
        'crypto': ['BTC-USD', 'ETH-USD', 'ADA-USD']
    }
    
    if not ticker:
        usage_summary = usage_tracker.get_usage_summary()
        return render_template('analysis/ai.html', 
                             ticker=None, 
                             usage_summary=usage_summary,
                             popular_stocks=popular_stocks)
    
    # Check if user can make analysis requests
    can_analyze, daily_limit, remaining = usage_tracker.can_make_analysis_request()
    
    if not can_analyze:
        flash(f'Du har brukt opp dine {daily_limit} daglige analyser. Oppgrader for ubegrenset tilgang.', 'warning')
        return redirect(url_for('pricing.pricing'))
    
    # Track the analysis request
    usage_tracker.track_analysis_request(ticker)
    
    try:
        # Get AI analysis
        analysis = AIService.get_stock_analysis(ticker)
        usage_summary = usage_tracker.get_usage_summary()
        return render_template('analysis/ai.html', 
                              ticker=ticker,
                              analysis=analysis,
                              usage_summary=usage_summary,
                              popular_stocks=popular_stocks)
    except Exception as e:
        print(f"Error in AI analysis route: {str(e)}")
        return render_template('analysis/ai.html', 
                              error=f"En feil oppstod: {str(e)}",
                              ticker=ticker,
                              popular_stocks=popular_stocks)
    

# Add new routes
@analysis.route('/api/analysis/indicators', methods=['GET'])
def get_indicators():
    """Get technical indicators for a stock"""
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400
    
    # Check if user can make analysis requests
    can_analyze, daily_limit, remaining = usage_tracker.can_make_analysis_request()
    
    if not can_analyze:
        return jsonify({
            "error": f"Daily analysis limit reached ({daily_limit}/day). Upgrade for unlimited access.",
            "limit_reached": True,
            "daily_limit": daily_limit,
            "remaining": remaining
        }), 429
    
    # Track the analysis request
    usage_tracker.track_analysis_request(symbol)
    
    try:
        # Endre til å bruke DataService.get_stock_data istedenfor get_stock_data
        stock_data = DataService.get_stock_data(symbol)
        
        # Calculate indicators
        indicators = AnalysisService.get_technical_indicators(stock_data)
        
        # Convert pandas Series to lists for JSON serialization
        result = {}
        for key, value in indicators.items():
            if isinstance(value, pd.Series):
                # Take last 30 days for frontend display
                result[key] = value.tail(30).tolist()
            else:
                result[key] = value
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis.route('/api/analysis/signals', methods=['GET'])
def get_trading_signals():
    """Get trading signals for a stock"""
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400
    
    # Check if user can make analysis requests
    can_analyze, daily_limit, remaining = usage_tracker.can_make_analysis_request()
    
    if not can_analyze:
        return jsonify({
            "error": f"Daily analysis limit reached ({daily_limit}/day). Upgrade for unlimited access.",
            "limit_reached": True,
            "daily_limit": daily_limit,
            "remaining": remaining
        }), 429
    
    # Track the analysis request
    usage_tracker.track_analysis_request(symbol)
    
    try:
        # Endre til å bruke DataService.get_stock_data istedenfor get_stock_data
        stock_data = DataService.get_stock_data(symbol)
        
        # Generate signals
        signals = AnalysisService.generate_trading_signals(stock_data)
        
        return jsonify({
            "success": True,
            "signals": signals
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analysis.route('/api/market-summary', methods=['GET'])
def get_market_summary():
    """Get AI-generated market summary"""
    sector = request.args.get('sector')
    
    # Get AI summary
    summary = AIService.generate_market_summary(sector)
    
    return jsonify(summary)

# @analysis.route('/api/export/csv', methods=['POST'])
# @subscription_required
# def export_csv():
#     """Export data to CSV"""
#     data = request.json.get('data')
#     filename = request.json.get('filename')
    
#     if not data:
#         return jsonify({"error": "No data provided"}), 400
    
#     result = ExportService.export_to_csv(data, filename)
    
#     return jsonify(result)

# @analysis.route('/api/export/pdf', methods=['POST'])
# @subscription_required
# def export_pdf():
#     """Export data to PDF"""
#     data = request.json.get('data')
#     title = request.json.get('title', 'Aksjeradar Rapport')
#     filename = request.json.get('filename')
    
#     if not data:
#         return jsonify({"error": "No data provided"}), 400
    
#     result = ExportService.export_to_pdf(data, title, filename)
    
#     return jsonify(result)

# @analysis.route('/api/email/send', methods=['POST'])
# @subscription_required
# def send_email():
#     """Send email with report"""
#     recipient = request.json.get('recipient')
#     subject = request.json.get('subject', 'Din rapport fra Aksjeradar')
#     body = request.json.get('body', '<p>Her er din rapport fra Aksjeradar.</p>')
#     attachments = request.json.get('attachments', [])
    
#     if not recipient:
#         return jsonify({"error": "Recipient email is required"}), 400
    
#     result = ExportService.send_email(recipient, subject, body, attachments)
    
#     return jsonify(result)

# @analysis.route('/api/email/schedule', methods=['POST'])
# @subscription_required
# def schedule_email():
#     """Schedule daily email report"""
#     user_id = request.json.get('user_id')
#     report_type = request.json.get('report_type', 'portfolio')
#     email = request.json.get('email')
    
#     if not user_id:
#         return jsonify({"error": "User ID is required"}), 400
    
#     result = ExportService.schedule_daily_report(user_id, report_type, email)
    
#     return jsonify(result)

@analysis.route('/downloads/<path:filename>')
def download_file(filename):
    """Download exported files"""
    return send_from_directory(current_app.config['EXPORT_FOLDER'], filename, as_attachment=True)

@analysis.route('/short-analysis', methods=['GET', 'POST'])
@access_required
def short_analysis():
    """Short selling analysis"""
    if request.method == 'GET':
        available_stocks = {
            'oslo_stocks': ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
            'global_stocks': ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'NFLX']
        }
        return render_template('analysis/short-analysis.html', available_stocks=available_stocks)
    
    # Handle POST request
    ticker = request.form.get('ticker')
    if not ticker:
        flash('Vennligst velg en aksje', 'error')
        return redirect(url_for('analysis.short_analysis'))
    
    try:
        # Generate short analysis with demo data
        stock_data = {
            'ticker': ticker,
            'company_name': f"Selskap {ticker}",
            'current_price': 245.80,
            'short_interest': 8.5,
            'days_to_cover': 3.2,
            'short_ratio': 2.8,
            'float_shorted': 12.3,
            'insider_selling': 15.2,
            'analyst_downgrades': 2,
            'short_score': 65,
            'recommendation': 'SHORT' if ticker in ['TSLA', 'NVDA', 'META'] else 'NEUTRAL',
            'analysis': {
                'short_signals': [
                    'Høy short interest (8.5%)',
                    'Oververdsatt i forhold til fundamentals',
                    'Teknisk svakhet i kursmønster',
                    'Sektorrotasjon bort fra vekstaksjer'
                ],
                'risks': [
                    'Squeeze potential ved positive nyheter',
                    'Høy volatilitet',
                    'Begrenset oppsidepotensial',
                    'Høye lånekostnader for shorting'
                ],
                'key_metrics': {
                    'short_interest_trend': 'Økende',
                    'institutional_sentiment': 'Bearish',
                    'technical_indicators': 'Svake',
                    'fundamental_valuation': 'Oververdsatt'
                },
                'risk_factors': {
                    'squeeze_risk': 'Medium',
                    'borrowing_cost': 'Høy',
                    'liquidity': 'God',
                    'volatility': 'Høy'
                }
            }
        }
        
        available_stocks = {
            'oslo_stocks': ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
            'global_stocks': ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'NFLX']
        }
        
        return render_template('analysis/short-analysis.html', 
                             stock_data=stock_data, 
                             available_stocks=available_stocks)
    except Exception as e:
        current_app.logger.error(f"Error in short analysis for {ticker}: {str(e)}")
        flash('En feil oppstod ved lasting av short analysen. Prøv igjen senere.', 'error')
        return render_template('analysis/short-analysis.html', 
                             available_stocks={
                                 'oslo_stocks': ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
                                 'global_stocks': ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'NFLX']
                             },
                             error=True)

@analysis.route('/fundamental', methods=['GET', 'POST'])
@access_required
def fundamental():
    """Fundamental analysis page"""
    if request.method == 'POST':
        try:
            symbol = request.form.get('symbol', '').strip().upper()
            if symbol:
                # Get fundamental analysis data
                analysis_data = AnalysisService.get_fundamental_analysis(symbol)
                stock_info = DataService.get_stock_info(symbol)
                analysis_score = AnalysisService.calculate_fundamental_score(symbol)
                
                return render_template('analysis/fundamental.html',
                                     symbol=symbol,
                                     analysis_data=analysis_data,
                                     stock_info=stock_info,
                                     analysis_score=analysis_score)
            else:
                flash('Vennligst skriv inn et aksjesymbol.', 'warning')
        except Exception as e:
            logger.error(f"Error in fundamental analysis for {symbol}: {e}")
            flash('Feil ved fundamental analyse. Prøv igjen senere.', 'error')
    
    # GET request or fallback
    return render_template('analysis/fundamental.html',
                         symbol=None,
                         analysis_data=None,
                         stock_info=None,
                         analysis_score=None)

@analysis.route('/sentiment')
@access_required
def sentiment():
    """Market sentiment analysis with fixed dropdown"""
    try:
        selected_symbol = request.args.get('symbol', '')
        
        # Get sentiment data
        if selected_symbol:
            sentiment_data = AnalysisService.get_sentiment_analysis(selected_symbol)
        else:
            sentiment_data = AnalysisService.get_market_sentiment_overview()
        
        # Get popular stocks for dropdown from Oslo Børs data
        oslo_stocks = DataService.get_oslo_bors_overview() or {}
        popular_stocks = list(oslo_stocks.keys())[:10] if oslo_stocks else ['EQNR.OL', 'DNB.OL', 'MOWI.OL']
        
        return render_template('analysis/sentiment.html',
                             sentiment_data=sentiment_data,
                             popular_stocks=popular_stocks,
                             selected_symbol=selected_symbol)
                             
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        return render_template('analysis/sentiment.html',
                             sentiment_data={},
                             popular_stocks=[],
                             selected_symbol='',
                             error="Kunne ikke laste sentiment data")

@analysis.route('/api/sentiment/<symbol>')
@access_required
def api_sentiment(symbol):
    """API endpoint for sentiment data"""
    try:
        sentiment_data = AnalysisService.get_sentiment_analysis(symbol)
        return jsonify({
            'success': True,
            'data': sentiment_data,
            'symbol': symbol
        })
    except Exception as e:
        logger.error(f"Error in sentiment API for {symbol}: {e}")
        return jsonify({'error': 'Failed to get sentiment data'}), 500

@analysis.route('/insider-trading')
@access_required
def insider_trading():
    """Insider trading analysis page"""
    try:
        return render_template('analysis/insider_trading.html',
                             page_title="Innsidehandel Intelligens")
    except Exception as e:
        logger.error(f"Error in insider trading page: {e}")
        flash('Kunne ikke laste innsidehandel-siden.', 'error')
        return render_template('analysis/insider_trading.html',
                             page_title="Innsidehandel Intelligens",
                             error="Siden kunne ikke lastes")