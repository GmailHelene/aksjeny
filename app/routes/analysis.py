from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory, session
from flask_login import current_user, login_required
from ..services.analysis_service import AnalysisService
from ..services.ai_service import AIService
from ..services.data_service import DataService, OSLO_BORS_TICKERS, GLOBAL_TICKERS
from ..services.usage_tracker import usage_tracker
from ..utils.access_control import access_required
from ..models.user import User
from ..models.portfolio import Portfolio, PortfolioStock
import random
import pandas as pd
import time
from datetime import datetime, timedelta

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
    oslo_stocks = DataService.get_oslo_bors_overview()
    global_stocks = DataService.get_global_stocks_overview()
    crypto = DataService.get_crypto_overview()
    currency = DataService.get_currency_overview()

    # Tell signalene
    buy_signals = sum(1 for d in oslo_stocks.values() if d.get('signal') == 'BUY')
    buy_signals += sum(1 for d in global_stocks.values() if d.get('signal') == 'BUY')
    sell_signals = sum(1 for d in oslo_stocks.values() if d.get('signal') == 'SELL')
    sell_signals += sum(1 for d in global_stocks.values() if d.get('signal') == 'SELL')
    neutral_signals = sum(1 for d in oslo_stocks.values() if d.get('signal') not in ['BUY', 'SELL'])
    neutral_signals += sum(1 for d in global_stocks.values() if d.get('signal') not in ['BUY', 'SELL'])

    # Markedssentiment (velg selv logikk, her: flest signaler vinner)
    if buy_signals > sell_signals and buy_signals > neutral_signals:
        market_sentiment = "Bullish"
    elif sell_signals > buy_signals and sell_signals > neutral_signals:
        market_sentiment = "Bearish"
    elif neutral_signals > 0:
        market_sentiment = "Neutral"
    else:
        market_sentiment = "Nøytral"

    # Determine if banner should be shown
    EXEMPT_EMAILS = {'helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com', 'tonjekit91@gmail.com'}
    show_banner = False
    try:
        if current_user.is_authenticated:
            # Exempt emails never see banners
            if current_user.email in EXEMPT_EMAILS:
                show_banner = False
            elif hasattr(current_user, 'has_active_subscription') and current_user.has_active_subscription():
                # Active subscription - no banner
                show_banner = False
            else:
                # No subscription - hide banner (trial period removed)
                show_banner = False
        else:
            # Not logged in - hide banner (trial period removed)
            show_banner = False
    except Exception:
        show_banner = False

    return render_template(
        'analysis/index.html',
        oslo_stocks=oslo_stocks,
        global_stocks=global_stocks,
        crypto=crypto,
        currency=currency,
        buy_signals=buy_signals,
        sell_signals=sell_signals,
        neutral_signals=neutral_signals,
        market_sentiment=market_sentiment,
        show_banner=show_banner
    )

@analysis.route('/technical')
@access_required
def technical(ticker=None):
    """Technical analysis view"""
    ticker = request.args.get('ticker')
    market = request.args.get('market')  # Add market parameter support
    
    if ticker:
        # Check if user can make analysis requests
        can_analyze, daily_limit, remaining = usage_tracker.can_make_analysis_request()
        
        if not can_analyze:
            flash(f'Du har brukt opp dine {daily_limit} daglige analyser. Oppgrader for ubegrenset tilgang.', 'warning')
            return redirect(url_for('pricing.pricing'))
        
        # Track the analysis request
        usage_tracker.track_analysis_request(ticker)
        
        try:
            # Get technical analysis data for the specific ticker
            technical_data = AnalysisService.get_technical_analysis(ticker)
            usage_summary = usage_tracker.get_usage_summary()
            return render_template('analysis/technical.html', 
                                 technical_data=technical_data, 
                                 ticker=ticker,
                                 market=market,
                                 analyses={},
                                 usage_summary=usage_summary)
        except Exception as e:
            current_app.logger.error(f"Error getting technical analysis for {ticker}: {str(e)}")
            return render_template('analysis/technical.html', 
                                 error=f"Kunne ikke hente teknisk analyse for {ticker}",
                                 ticker=ticker,
                                 market=market,
                                 analyses={})
    elif market:
        # Handle market-wide technical analysis
        try:
            if market == 'global':
                # Get global market analysis
                market_data = {
                    'market_type': 'global',
                    'indices': ['S&P 500', 'NASDAQ', 'DOW JONES', 'FTSE 100', 'DAX'],
                    'overview': 'Global market technical analysis showing mixed signals',
                    'trend': 'bullish'
                }
            else:
                # Default to Norwegian market
                market_data = {
                    'market_type': 'norwegian',
                    'indices': ['OSEBX', 'OBX'],
                    'overview': 'Norwegian market showing stable growth patterns',
                    'trend': 'neutral'
                }
                
            return render_template('analysis/technical.html', 
                                 market_data=market_data,
                                 market=market,
                                 analyses={})
        except Exception as e:
            current_app.logger.error(f"Error getting market analysis for {market}: {str(e)}")
            return render_template('analysis/technical.html', 
                                 error=f"Kunne ikke hente markedsanalyse for {market}",
                                 market=market,
                                 analyses={})
    
    # If no ticker provided, show the technical analysis landing page with sample data
    try:
        # Get usage summary for template
        usage_summary = usage_tracker.get_usage_summary()
        
        # Get sample analyses for popular tickers including crypto and currency
        sample_tickers = ['EQNR.OL', 'DNB.OL', 'AAPL', 'TSLA', 'MSFT']
        crypto_tickers = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'XRP-USD']
        currency_tickers = ['USDNOK=X', 'EURNOK=X', 'GBPNOK=X']
        
        analyses = {}
        
        # Add stock analyses
        for sample_ticker in sample_tickers:
            try:
                analyses[sample_ticker] = AnalysisService.get_technical_analysis(sample_ticker)
            except:
                pass
        
        # Add crypto analyses with demo data if service fails
        for crypto_ticker in crypto_tickers:
            try:
                analyses[crypto_ticker] = AnalysisService.get_technical_analysis(crypto_ticker)
            except:
                # Add demo crypto data
                analyses[crypto_ticker] = {
                    'last_price': 65000.0 if 'BTC' in crypto_ticker else (3500.0 if 'ETH' in crypto_ticker else 0.5),
                    'signal': 'Buy',
                    'rsi': 45.2,
                    'macd': 1.23,
                    'support': 60000.0 if 'BTC' in crypto_ticker else (3200.0 if 'ETH' in crypto_ticker else 0.45),
                    'resistance': 70000.0 if 'BTC' in crypto_ticker else (3800.0 if 'ETH' in crypto_ticker else 0.55),
                    'last_update': 'I dag',
                    'signal_reason': 'Bullish trend continues'
                }
        
        # Add currency analyses with demo data if service fails
        for currency_ticker in currency_tickers:
            try:
                analyses[currency_ticker] = AnalysisService.get_technical_analysis(currency_ticker)
            except:
                # Add demo currency data
                analyses[currency_ticker] = {
                    'last_price': 10.45 if 'USD' in currency_ticker else (11.20 if 'EUR' in currency_ticker else 13.15),
                    'signal': 'Hold',
                    'rsi': 52.8,
                    'macd': -0.12,
                    'support': 10.20 if 'USD' in currency_ticker else (10.95 if 'EUR' in currency_ticker else 12.90),
                    'resistance': 10.65 if 'USD' in currency_ticker else (11.45 if 'EUR' in currency_ticker else 13.40),
                    'last_update': 'I dag',
                    'signal_reason': 'Sideways movement expected'
                }
        
        return render_template('analysis/technical.html', 
                             analyses=analyses, 
                             usage_summary=usage_summary)
    except Exception as e:
        current_app.logger.error(f"Error loading technical analysis page: {str(e)}")
        return render_template('analysis/technical.html', analyses={})

@analysis.route('/technical/<path:ticker>')
@access_required
def technical_with_ticker(ticker):
    """Technical analysis view for specific ticker"""
    try:
        # Get technical analysis data for the specific ticker
        technical_data = AnalysisService.get_technical_analysis(ticker)
        return render_template('analysis/technical.html', 
                             technical_data=technical_data, 
                             ticker=ticker)
    except Exception as e:
        current_app.logger.error(f"Error getting technical analysis for {ticker}: {str(e)}")
        return render_template('analysis/technical.html', 
                             error=f"Kunne ikke hente teknisk analyse for {ticker}",
                             ticker=ticker)

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
    """AI analysis view"""
    ticker = request.args.get('ticker')
    if not ticker:
        usage_summary = usage_tracker.get_usage_summary()
        return render_template('analysis/ai.html', ticker=None, usage_summary=usage_summary)
    
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
                              usage_summary=usage_summary)
    except Exception as e:
        print(f"Error in AI analysis route: {str(e)}")
        return render_template('analysis/ai.html', 
                              error=f"En feil oppstod: {str(e)}",
                              ticker=ticker)
    

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

@analysis.route('/market-overview')
@access_required
def market_overview():
    """Show market overview with analysis data"""
    try:
        market_data = DataService.get_market_overview()
        return render_template(
            'analysis/market_overview.html',
            oslo_stocks=market_data['oslo_stocks'],
            global_stocks=market_data['global_stocks'],
            crypto=market_data['crypto'],
            currency=market_data['currency']
        )
    except Exception as e:
        print(f"Error in market_overview route: {str(e)}")
        return render_template(
            'error.html', 
            error=f"Det oppstod en feil ved henting av markedsoversikt: {str(e)}"
        )

@analysis.route('/warren-buffett', methods=['GET', 'POST'])
@access_required
def warren_buffett():
    if request.method == 'GET':
        available_stocks = get_all_available_stocks()
        return render_template('analysis/warren-buffett.html', available_stocks=available_stocks)
    # Handle POST request
    ticker = request.form.get('ticker')
    if not ticker:
        flash('Vennligst velg en aksje', 'error')
        return redirect(url_for('analysis.warren_buffett'))
    stock_data = AnalysisService.get_buffett_analysis(ticker)
    if not stock_data:
        flash('Kunne ikke hente data for denne aksjen', 'error')
        return redirect(url_for('analysis.warren_buffett'))
    available_stocks = get_all_available_stocks()
    return render_template('analysis/warren-buffett.html', 
                         stock_data=stock_data, 
                         available_stocks=available_stocks)

@analysis.route('/benjamin-graham', methods=['GET', 'POST'])
@access_required
def benjamin_graham():
    if request.method == 'GET':
        available_stocks = get_all_available_stocks()
        return render_template('analysis/graham.html', available_stocks=available_stocks)
    # Handle POST request
    ticker = request.form.get('ticker')
    if not ticker:
        flash('Vennligst velg en aksje', 'error')
        return redirect(url_for('analysis.benjamin_graham'))
    stock_data = AnalysisService.get_graham_analysis(ticker)
    if not stock_data:
        flash('Kunne ikke hente data for denne aksjen', 'error')
        return redirect(url_for('analysis.benjamin_graham'))
    available_stocks = get_all_available_stocks()
    return render_template('analysis/graham.html', 
                         stock_data=stock_data, 
                         available_stocks=available_stocks)

@analysis.route('/short-analysis', methods=['GET', 'POST'])
@access_required
def short_analysis():
    if request.method == 'GET':
        available_stocks = get_all_available_stocks()
        return render_template('analysis/short-analysis.html', available_stocks=available_stocks)
    # Handle POST request
    ticker = request.form.get('ticker')
    if not ticker:
        flash('Vennligst velg en aksje', 'error')
        return redirect(url_for('analysis.short_analysis'))
    stock_data = AnalysisService.get_short_analysis(ticker)
    if not stock_data:
        flash('Kunne ikke hente data for denne aksjen', 'error')
        return redirect(url_for('analysis.short_analysis'))
    available_stocks = get_all_available_stocks()
    return render_template('analysis/short-analysis.html', 
                         stock_data=stock_data, 
                         available_stocks=available_stocks)

@analysis.route('/fundamental')
@login_required
@access_required
def fundamental():
    """Fundamental analysis page"""
    try:
        ticker = request.args.get('ticker', 'EQNR.OL')
        
        # Get stock info and fundamentals
        stock_info = DataService.get_stock_info(ticker)
        if not stock_info:
            flash(f'Kunne ikke finne data for {ticker}', 'error')
            return redirect(url_for('analysis.index'))
        
        fundamental_data = AnalysisService.get_fundamental_data(ticker)
        
        # Format numbers for Norwegian display
        if fundamental_data:
            for key in ['market_cap', 'enterprise_value', 'revenue', 'ebitda']:
                if key in fundamental_data and fundamental_data[key]:
                    fundamental_data[f'{key}_formatted'] = "{:,.0f}".format(fundamental_data[key]).replace(',', ' ')
        
        return render_template('analysis/fundamental.html',
                             ticker=ticker,
                             stock_info=stock_info,
                             fundamental_data=fundamental_data)
    except Exception as e:
        logger.error(f"Error in fundamental analysis for {ticker}: {str(e)}")
        flash('Feil ved lasting av fundamental analyse. Vennligst prøv igjen senere.', 'error')
        return redirect(url_for('analysis.index'))

@analysis.route('/sentiment')
@login_required
@access_required
def sentiment():
    """Sentiment analysis page"""
    try:
        ticker = request.args.get('ticker', 'EQNR.OL')
        
        # Get sentiment data
        sentiment_data = AnalysisService.get_sentiment_analysis(ticker)
        stock_info = DataService.get_stock_info(ticker)
        
        # Ensure we have Norwegian translations for sentiment
        if sentiment_data and 'overall_sentiment' in sentiment_data:
            sentiment_map = {
                'bullish': 'Positiv',
                'bearish': 'Negativ',
                'neutral': 'Nøytral'
            }
            sentiment_data['overall_sentiment_no'] = sentiment_map.get(
                sentiment_data['overall_sentiment'].lower(), 
                sentiment_data['overall_sentiment']
            )
        
        return render_template('analysis/sentiment.html',
                             ticker=ticker,
                             sentiment_data=sentiment_data,
                             stock_info=stock_info)
    except Exception as e:
        logger.error(f"Error in sentiment analysis for {ticker}: {str(e)}")
        flash('Feil ved lasting av sentimentanalyse. Vennligst prøv igjen senere.', 'error')
        return redirect(url_for('analysis.index'))

@analysis.route('/screener')
@login_required
@access_required
def screener():
    """Stock screener page"""
    try:
        # Get filter parameters
        filters = {
            'market': request.args.get('market', 'all'),
            'min_price': request.args.get('min_price', type=float),
            'max_price': request.args.get('max_price', type=float),
            'min_volume': request.args.get('min_volume', type=int),
            'sector': request.args.get('sector'),
            'signal': request.args.get('signal')
        }
        
        # Run screener
        results = AnalysisService.run_screener(filters)
        
        # Format prices for Norwegian display
        for result in results:
            if 'price' in result:
                result['price_formatted'] = "{:,.2f}".format(result['price']).replace(',', ' ').replace('.', ',')
            if 'volume' in result:
                result['volume_formatted'] = "{:,.0f}".format(result['volume']).replace(',', ' ')
        
        return render_template('analysis/screener.html',
                             filters=filters,
                             results=results)
    except Exception as e:
        logger.error(f"Error running screener: {str(e)}")
        flash('Feil ved kjøring av aksje-screener. Vennligst prøv igjen senere.', 'error')
        return redirect(url_for('analysis.index'))

@analysis.route('/advanced')
@login_required
@access_required
def advanced():
    """Avansert analyse-oversikt"""
    try:
        # Hent avanserte analyse-verktøy og data
        tools = [
            {
                'name': 'Kvantitativ Analyse',
                'description': 'Matematiske modeller og statistisk analyse',
                'url': url_for('analysis.quantitative'),
                'icon': 'bi-calculator'
            },
            {
                'name': 'Monte Carlo Simulering',
                'description': 'Risiko- og avkastningsanalyse',
                'url': url_for('analysis.monte_carlo'),
                'icon': 'bi-dice-5'
            },
            {
                'name': 'Porteføljeoptimalisering',
                'description': 'Modern Portfolio Theory implementering',
                'url': url_for('analysis.portfolio_optimization'),
                'icon': 'bi-pie-chart'
            },
            {
                'name': 'Volatilitet & VaR',
                'description': 'Value at Risk og volatilitetsanalyse',
                'url': url_for('analysis.risk_analysis'),
                'icon': 'bi-exclamation-triangle'
            },
            {
                'name': 'Korrelasjonmatriser',
                'description': 'Asset korrelasjon og diversifikasjon',
                'url': url_for('analysis.correlation'),
                'icon': 'bi-grid-3x3'
            },
            {
                'name': 'Backtesting',
                'description': 'Test handelsstrategier historisk',
                'url': url_for('analysis.backtesting'),
                'icon': 'bi-arrow-clockwise'
            }
        ]
        
        return render_template('analysis/advanced.html', tools=tools)
    except Exception as e:
        logger.error(f"Error loading advanced analysis: {e}")
        flash('Kunne ikke laste avansert analyse.', 'error')
        return redirect(url_for('analysis.index'))

@analysis.route('/quantitative')
@login_required
@access_required
def quantitative():
    """Kvantitativ analyse"""
    try:
        ticker = request.args.get('ticker', 'EQNR.OL')
        
        # Hent kvantitative metriker
        quant_data = {
            'ticker': ticker,
            'beta': 1.15,
            'alpha': 0.03,
            'treynor_ratio': 0.085,
            'information_ratio': 0.45,
            'tracking_error': 0.08,
            'sortino_ratio': 1.32,
            'calmar_ratio': 0.95,
            'maximum_drawdown': 0.18,
            'var_95': 0.12,
            'cvar_95': 0.15,
            'skewness': -0.25,
            'kurtosis': 3.8
        }
        
        return render_template('analysis/quantitative.html', 
                             ticker=ticker,
                             data=quant_data)
    except Exception as e:
        logger.error(f"Error in quantitative analysis: {e}")
        flash('Feil ved kvantitativ analyse.', 'error')
        return redirect(url_for('analysis.advanced'))

@analysis.route('/monte-carlo')
@login_required
@access_required
def monte_carlo():
    """Monte Carlo simulering"""
    try:
        ticker = request.args.get('ticker', 'EQNR.OL')
        simulations = request.args.get('simulations', 1000, type=int)
        
        # Mock Monte Carlo resultater
        mc_results = {
            'ticker': ticker,
            'simulations': simulations,
            'expected_return': 0.08,
            'volatility': 0.22,
            'confidence_intervals': {
                '95%': {'lower': -0.35, 'upper': 0.51},
                '90%': {'lower': -0.28, 'upper': 0.44},
                '80%': {'lower': -0.20, 'upper': 0.36}
            },
            'probabilities': {
                'positive_return': 0.67,
                'loss_gt_10': 0.18,
                'loss_gt_20': 0.08
            }
        }
        
        return render_template('analysis/monte_carlo.html',
                             ticker=ticker,
                             results=mc_results)
    except Exception as e:
        logger.error(f"Error in Monte Carlo analysis: {e}")
        flash('Feil ved Monte Carlo simulering.', 'error')
        return redirect(url_for('analysis.advanced'))

@analysis.route('/portfolio-optimization')
@login_required
@access_required
def portfolio_optimization():
    """Porteføljeoptimalisering"""
    try:
        # Mock optimaliserings-resultater
        optimization = {
            'efficient_frontier': [
                {'risk': 0.10, 'return': 0.06},
                {'risk': 0.15, 'return': 0.08},
                {'risk': 0.20, 'return': 0.10},
                {'risk': 0.25, 'return': 0.11}
            ],
            'optimal_portfolio': {
                'weights': {
                    'EQNR.OL': 0.30,
                    'DNB.OL': 0.25,
                    'AAPL': 0.20,
                    'MSFT': 0.15,
                    'BTC-USD': 0.10
                },
                'expected_return': 0.095,
                'risk': 0.18,
                'sharpe_ratio': 1.4
            }
        }
        
        return render_template('analysis/portfolio_optimization.html',
                             optimization=optimization)
    except Exception as e:
        logger.error(f"Error in portfolio optimization: {e}")
        flash('Feil ved porteføljeoptimalisering.', 'error')
        return redirect(url_for('analysis.advanced'))

@analysis.route('/risk-analysis')
@login_required
@access_required
def risk_analysis():
    """Risiko- og VaR analyse"""
    try:
        ticker = request.args.get('ticker', 'EQNR.OL')
        
        risk_metrics = {
            'ticker': ticker,
            'var_1d_95': 0.035,
            'var_1d_99': 0.052,
            'cvar_1d_95': 0.048,
            'volatility_annual': 0.22,
            'volatility_30d': 0.28,
            'beta': 1.15,
            'correlation_market': 0.78,
            'maximum_drawdown': 0.18,
            'average_drawdown': 0.08,
            'drawdown_duration': 45
        }
        
        return render_template('analysis/risk_analysis.html',
                             ticker=ticker,
                             metrics=risk_metrics)
    except Exception as e:
        logger.error(f"Error in risk analysis: {e}")
        flash('Feil ved risikoanalyse.', 'error')
        return redirect(url_for('analysis.advanced'))

@analysis.route('/correlation')
@login_required
@access_required
def correlation():
    """Korrelasjonanalyse"""
    try:
        # Mock korrelasjonmatriser
        tickers = ['EQNR.OL', 'DNB.OL', 'AAPL', 'MSFT', 'BTC-USD']
        correlation_matrix = {
            'EQNR.OL': {'EQNR.OL': 1.00, 'DNB.OL': 0.65, 'AAPL': 0.25, 'MSFT': 0.30, 'BTC-USD': 0.15},
            'DNB.OL': {'EQNR.OL': 0.65, 'DNB.OL': 1.00, 'AAPL': 0.35, 'MSFT': 0.40, 'BTC-USD': 0.10},
            'AAPL': {'EQNR.OL': 0.25, 'DNB.OL': 0.35, 'AAPL': 1.00, 'MSFT': 0.75, 'BTC-USD': 0.20},
            'MSFT': {'EQNR.OL': 0.30, 'DNB.OL': 0.40, 'AAPL': 0.75, 'MSFT': 1.00, 'BTC-USD': 0.18},
            'BTC-USD': {'EQNR.OL': 0.15, 'DNB.OL': 0.10, 'AAPL': 0.20, 'MSFT': 0.18, 'BTC-USD': 1.00}
        }
        
        return render_template('analysis/correlation.html',
                             tickers=tickers,
                             matrix=correlation_matrix)
    except Exception as e:
        logger.error(f"Error in correlation analysis: {e}")
        flash('Feil ved korrelasjonanalyse.', 'error')
        return redirect(url_for('analysis.advanced'))

@analysis.route('/backtesting')
@login_required
@access_required
def backtesting():
    """Backtesting av handelsstrategier"""
    try:
        strategy = request.args.get('strategy', 'momentum')
        
        backtest_results = {
            'strategy': strategy,
            'period': '2020-2025',
            'total_return': 0.45,
            'annual_return': 0.09,
            'volatility': 0.18,
            'sharpe_ratio': 1.85,
            'max_drawdown': 0.12,
            'win_rate': 0.68,
            'avg_trade_return': 0.015,
            'total_trades': 127,
            'benchmark_outperformance': 0.15
        }
        
        return render_template('analysis/backtesting.html',
                             strategy=strategy,
                             results=backtest_results)
    except Exception as e:
        logger.error(f"Error in backtesting: {e}")
        flash('Feil ved backtesting.', 'error')
        return redirect(url_for('analysis.advanced'))