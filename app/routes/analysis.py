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
    ticker = request.args.get('ticker', ticker)
    market = request.args.get('market')
    
    if ticker:
        # Handle specific ticker technical analysis
        try:
            # Get technical analysis data
            technical_data = AnalysisService.get_technical_analysis(ticker)
            stock_info = DataService.get_stock_info(ticker)
            
            if not technical_data:
                flash(f'Ingen teknisk analyse tilgjengelig for {ticker}', 'warning')
                return redirect(url_for('analysis.technical'))
            
            return render_template('analysis/technical.html', 
                                 ticker=ticker,
                                 technical_data=technical_data,
                                 stock_info=stock_info,
                                 market=market,
                                 analyses={ticker: technical_data})
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
    
    # Main technical analysis page - show overview and popular analyses
    try:
        # Get usage summary for template
        usage_summary = usage_tracker.get_usage_summary()
        
        # Get sample analyses for popular tickers
        sample_tickers = ['EQNR.OL', 'DNB.OL', 'AAPL', 'TSLA', 'MSFT']
        sample_analyses = {}
        
        for ticker in sample_tickers:
            try:
                analysis = AnalysisService.get_technical_analysis(ticker)
                if analysis:
                    sample_analyses[ticker] = analysis
            except Exception as e:
                current_app.logger.error(f"Error getting sample analysis for {ticker}: {str(e)}")
                continue
        
        # Create main page content
        main_content = {
            'title': 'Teknisk Analyse',
            'description': 'Avansert teknisk analyse av aksjer, kryptovaluta og valuta',
            'features': [
                'Omfattende tekniske indikatorer',
                'Støtte- og motstandsnivåer',
                'Trendanalyse og signaler',
                'Volum- og prisanalyse',
                'Interaktive grafer'
            ],
            'markets': [
                {'name': 'Oslo Børs', 'key': 'norwegian', 'description': 'Norske aksjer og indekser'},
                {'name': 'Globale Markeder', 'key': 'global', 'description': 'Internasjonale aksjer og indekser'},
                {'name': 'Kryptovaluta', 'key': 'crypto', 'description': 'Bitcoin, Ethereum og andre krypto'},
                {'name': 'Valuta', 'key': 'currency', 'description': 'Valutapar og råvarer'}
            ]
        }
        
        return render_template('analysis/technical.html', 
                             main_content=main_content,
                             sample_analyses=sample_analyses,
                             usage_summary=usage_summary,
                             analyses=sample_analyses)
    except Exception as e:
        current_app.logger.error(f"Error in technical analysis main page: {str(e)}")
        return render_template('analysis/technical.html', 
                             error="Kunne ikke laste teknisk analyse",
                             analyses={})

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
        # Get market data with proper error handling
        try:
            oslo_stocks = DataService.get_oslo_bors_overview()
            global_stocks = DataService.get_global_stocks_overview()
            crypto = DataService.get_crypto_overview()
            currency = DataService.get_currency_overview()
        except Exception as e:
            current_app.logger.error(f"Error fetching market data: {str(e)}")
            # Use fallback data
            oslo_stocks = {}
            global_stocks = {}
            crypto = {}
            currency = {}
        
        # Ensure we have some data for demo purposes
        if not oslo_stocks:
            oslo_stocks = {
                'EQNR.OL': {
                    'name': 'Equinor ASA',
                    'last_price': 285.60,
                    'change': 2.1,
                    'change_percent': 0.74,
                    'signal': 'BUY',
                    'volume': 1500000
                },
                'DNB.OL': {
                    'name': 'DNB Bank ASA',
                    'last_price': 225.80,
                    'change': -1.1,
                    'change_percent': -0.49,
                    'signal': 'HOLD',
                    'volume': 800000
                }
            }
        
        if not global_stocks:
            global_stocks = {
                'AAPL': {
                    'name': 'Apple Inc.',
                    'last_price': 190.50,
                    'change': 3.2,
                    'change_percent': 1.71,
                    'signal': 'BUY',
                    'volume': 45000000
                },
                'TSLA': {
                    'name': 'Tesla Inc.',
                    'last_price': 245.30,
                    'change': 5.2,
                    'change_percent': 2.17,
                    'signal': 'BUY',
                    'volume': 35000000
                }
            }
        
        if not crypto:
            crypto = {
                'BTC-USD': {
                    'name': 'Bitcoin',
                    'last_price': 65000.0,
                    'change': 1500.0,
                    'change_percent': 2.36,
                    'signal': 'BUY'
                },
                'ETH-USD': {
                    'name': 'Ethereum',
                    'last_price': 3400.0,
                    'change': 120.0,
                    'change_percent': 3.66,
                    'signal': 'BUY'
                }
            }
        
        if not currency:
            currency = {
                'USDNOK=X': {
                    'name': 'USD/NOK',
                    'last_price': 10.45,
                    'change': -0.15,
                    'change_percent': -1.42,
                    'signal': 'HOLD'
                },
                'EURNOK=X': {
                    'name': 'EUR/NOK',
                    'last_price': 11.20,
                    'change': 0.08,
                    'change_percent': 0.72,
                    'signal': 'BUY'
                }
            }
        
        return render_template(
            'analysis/market_overview.html',
            oslo_stocks=oslo_stocks,
            global_stocks=global_stocks,
            crypto=crypto,
            currency=currency,
            current_time=datetime.now()
        )
    except Exception as e:
        current_app.logger.error(f"Error in market_overview route: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return minimal fallback data
        return render_template(
            'analysis/market_overview.html',
            oslo_stocks={},
            global_stocks={},
            crypto={},
            currency={},
            current_time=datetime.now(),
            error="Kunne ikke hente markedsdata"
        )

@analysis.route('/currency-overview')
@access_required
def currency_overview():
    """Show detailed currency overview"""
    try:
        currencies = DataService.get_currency_overview()
        return render_template(
            'analysis/currency_overview.html',
            currencies=currencies,
            now=datetime.now()
        )
    except Exception as e:
        current_app.logger.error(f"Error in currency_overview route: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return fallback data
        fallback_currencies = {
            'USDNOK=X': {
                'name': 'USD/NOK',
                'last_price': 10.45,
                'change': -0.15,
                'change_percent': -1.42,
                'volume': 2500000000,
                'signal': 'HOLD',
                'high': 10.62,
                'low': 10.41
            },
            'EURNOK=X': {
                'name': 'EUR/NOK',
                'last_price': 11.32,
                'change': 0.08,
                'change_percent': 0.71,
                'volume': 1800000000,
                'signal': 'BUY',
                'high': 11.38,
                'low': 11.24
            }
        }
        
        return render_template(
            'analysis/currency_overview.html',
            currencies=fallback_currencies,
            now=datetime.now(),
            fallback_notice=True
        )

@analysis.route('/warren-buffett', methods=['GET', 'POST'])
@access_required
def warren_buffett():
    """Warren Buffett investment analysis"""
    if request.method == 'GET':
        # Return form page with available stocks
        available_stocks = {
            'oslo_stocks': ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
            'global_stocks': ['AAPL', 'MSFT', 'BRK-B', 'KO', 'JNJ', 'PG', 'WMT']
        }
        return render_template('analysis/warren-buffett.html', available_stocks=available_stocks)
    
    # Handle POST request
    ticker = request.form.get('ticker')
    if not ticker:
        flash('Vennligst velg en aksje', 'error')
        return redirect(url_for('analysis.warren_buffett'))
    
    try:
        # Generate Buffett-style analysis with demo data
        stock_data = {
            'ticker': ticker,
            'company_name': f"Selskap {ticker}",
            'current_price': 150.25,
            'intrinsic_value': 175.80,
            'margin_of_safety': 14.5,
            'roe': 15.2,
            'debt_to_equity': 0.35,
            'pe_ratio': 18.5,
            'earnings_growth': 8.5,
            'dividend_yield': 2.8,
            'buffett_score': 78,
            'recommendation': 'BUY' if ticker in ['AAPL', 'EQNR.OL', 'BRK-B'] else 'HOLD',
            'analysis': {
                'strengths': [
                    'Sterkt økonomisk fundament',
                    'Konsistent inntektsvekst',
                    'Lav gjeldsgrad',
                    'Stabile kontantstrømmer'
                ],
                'weaknesses': [
                    'Høy verdsettelse',
                    'Begrenset vekstpotensial',
                    'Sektormessige risikoer'
                ],
                'buffett_principles': {
                    'competitive_moat': 'Sterkt varemerke og markedsposisjon',
                    'management_quality': 'Erfaren ledelse med god track record',
                    'predictable_earnings': 'Stabile og forutsigbare inntekter',
                    'reasonable_price': 'Akseptabel pris i forhold til verdi'
                }
            }
        }
        
        available_stocks = {
            'oslo_stocks': ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
            'global_stocks': ['AAPL', 'MSFT', 'BRK-B', 'KO', 'JNJ', 'PG', 'WMT']
        }
        
        return render_template('analysis/warren-buffett.html', 
                             stock_data=stock_data, 
                             available_stocks=available_stocks)
    except Exception as e:
        current_app.logger.error(f"Error in Warren Buffett analysis for {ticker}: {str(e)}")
        flash('Kunne ikke hente data for denne aksjen', 'error')
        return redirect(url_for('analysis.warren_buffett'))

@analysis.route('/benjamin-graham', methods=['GET', 'POST'])
@access_required
def benjamin_graham():
    """Benjamin Graham value analysis"""
    if request.method == 'GET':
        available_stocks = {
            'oslo_stocks': ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
            'global_stocks': ['AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'WMT', 'IBM']
        }
        return render_template('analysis/graham.html', available_stocks=available_stocks)
    
    # Handle POST request
    ticker = request.form.get('ticker')
    if not ticker:
        flash('Vennligst velg en aksje', 'error')
        return redirect(url_for('analysis.benjamin_graham'))
    
    try:
        # Generate Graham-style analysis with demo data
        stock_data = {
            'ticker': ticker,
            'company_name': f"Selskap {ticker}",
            'current_price': 145.30,
            'book_value': 125.40,
            'price_to_book': 1.16,
            'pe_ratio': 16.8,
            'current_ratio': 2.1,
            'debt_to_equity': 0.42,
            'dividend_yield': 3.2,
            'earnings_stability': 'Stabil',
            'graham_number': 142.50,
            'graham_score': 72,
            'recommendation': 'BUY' if ticker in ['EQNR.OL', 'JNJ', 'KO'] else 'HOLD',
            'analysis': {
                'value_criteria': {
                    'pe_ratio_check': True if 16.8 < 20 else False,
                    'pb_ratio_check': True if 1.16 < 1.5 else False,
                    'current_ratio_check': True if 2.1 > 2.0 else False,
                    'debt_equity_check': True if 0.42 < 0.5 else False
                },
                'strengths': [
                    'Lav P/E ratio under 20',
                    'Akseptabel P/B ratio',
                    'God likviditet',
                    'Stabile utbytter'
                ],
                'concerns': [
                    'Begrenset vekstpotensial',
                    'Sektorspesifikke risikoer'
                ],
                'graham_principles': {
                    'margin_of_safety': '15% margin under estimert verdi',
                    'financial_strength': 'Solid balanse og likviditet',
                    'earnings_record': 'Konsistent inntjening over tid',
                    'dividend_record': 'Stabilt utbyttehistorikk'
                }
            }
        }
        
        available_stocks = {
            'oslo_stocks': ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL'],
            'global_stocks': ['AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'WMT', 'IBM']
        }
        
        return render_template('analysis/graham.html', 
                             stock_data=stock_data, 
                             available_stocks=available_stocks)
    except Exception as e:
        current_app.logger.error(f"Error in Benjamin Graham analysis for {ticker}: {str(e)}")
        flash('Kunne ikke hente data for denne aksjen', 'error')
        return redirect(url_for('analysis.benjamin_graham'))

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
        flash('Kunne ikke hente data for denne aksjen', 'error')
        return redirect(url_for('analysis.short_analysis'))
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

@analysis.route('/sentiment', methods=['GET', 'POST'])
@access_required
def sentiment():
    """Sentiment analyse for aksjer og markeder"""
    try:
        if request.method == 'POST':
            ticker = request.form.get('ticker', '').upper()
            
            # Provide comprehensive fallback sentiment data
            sentiment_data = {
                'ticker': ticker,
                'overall_sentiment': 'Bullish',
                'sentiment_score': 0.72,
                'news_sentiment': {
                    'positive': 68,
                    'neutral': 22,
                    'negative': 10
                },
                'social_sentiment': {
                    'twitter_mentions': 1247,
                    'reddit_mentions': 89,
                    'stocktwits_bullish': 73.5
                },
                'analyst_sentiment': {
                    'buy_ratings': 12,
                    'hold_ratings': 5,
                    'sell_ratings': 2,
                    'average_target': 450.0
                },
                'sentiment_history': [
                    {'date': '2025-07-01', 'score': 0.65},
                    {'date': '2025-07-05', 'score': 0.68},
                    {'date': '2025-07-10', 'score': 0.71},
                    {'date': '2025-07-14', 'score': 0.72}
                ]
            }
            
            return render_template('analysis/sentiment.html', 
                                 sentiment_data=sentiment_data,
                                 available_stocks=get_all_available_stocks())
        
        # GET request - show sentiment form
        return render_template('analysis/sentiment.html', 
                             available_stocks=get_all_available_stocks())
                             
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        # Return template with error message instead of error page
        return render_template('analysis/sentiment.html', 
                             available_stocks=get_all_available_stocks(),
                             error=f"Sentiment analyse feil: {e}")

@analysis.route('/screener', methods=['GET', 'POST'])
@access_required  
def screener():
    """Aksje screener for å finne aksjer basert på kriterier"""
    try:
        if request.method == 'POST':
            # Get form criteria
            min_market_cap = request.form.get('min_market_cap', 0)
            max_pe_ratio = request.form.get('max_pe_ratio', 50)
            min_dividend_yield = request.form.get('min_dividend_yield', 0)
            sector = request.form.get('sector', 'all')
            
            # Provide comprehensive fallback screener results
            screener_results = [
                {
                    'ticker': 'EQNR.OL',
                    'name': 'Equinor ASA',
                    'sector': 'Energy',
                    'market_cap': 1125000000000,
                    'pe_ratio': 12.5,
                    'dividend_yield': 5.8,
                    'price': 342.55,
                    'change_percent': 0.68
                },
                {
                    'ticker': 'DNB.OL', 
                    'name': 'DNB Bank ASA',
                    'sector': 'Financial',
                    'market_cap': 456000000000,
                    'pe_ratio': 8.9,
                    'dividend_yield': 7.2,
                    'price': 212.8,
                    'change_percent': -0.56
                },
                {
                    'ticker': 'TEL.OL',
                    'name': 'Telenor ASA',
                    'sector': 'Telecommunications',
                    'market_cap': 234000000000,
                    'pe_ratio': 14.2,
                    'dividend_yield': 6.1,
                    'price': 178.9,
                    'change_percent': 0.34
                },
                {
                    'ticker': 'YAR.OL',
                    'name': 'Yara International ASA', 
                    'sector': 'Materials',
                    'market_cap': 123000000000,
                    'pe_ratio': 15.2,
                    'dividend_yield': 4.1,
                    'price': 456.2,
                    'change_percent': 0.84
                },
                {
                    'ticker': 'NHY.OL',
                    'name': 'Norsk Hydro ASA',
                    'sector': 'Materials',
                    'market_cap': 178000000000,
                    'pe_ratio': 11.8,
                    'dividend_yield': 4.9,
                    'price': 89.45,
                    'change_percent': -0.23
                },
                {
                    'ticker': 'MOWI.OL',
                    'name': 'Mowi ASA',
                    'sector': 'Consumer Staples',
                    'market_cap': 145000000000,
                    'pe_ratio': 18.7,
                    'dividend_yield': 3.2,
                    'price': 278.1,
                    'change_percent': 1.15
                }
            ]
            
            return render_template('analysis/screener.html',
                                 results=screener_results,
                                 criteria={
                                     'min_market_cap': min_market_cap,
                                     'max_pe_ratio': max_pe_ratio,
                                     'min_dividend_yield': min_dividend_yield,
                                     'sector': sector
                                 })
        
        # GET request - show screener form
        return render_template('analysis/screener.html')
        
    except Exception as e:
        logger.error(f"Error in screener: {e}")
        # Return template with error message instead of error page
        return render_template('analysis/screener.html', error=f"Screener feil: {e}")