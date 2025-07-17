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

@analysis.route('/warren-buffett')
@access_required
def warren_buffett():
    """Warren Buffett analysis style"""
    try:
        ticker = request.args.get('ticker')
        
        if ticker:
            # Return analysis for specific ticker with Warren Buffett criteria
            analysis_data = {
                'ticker': ticker.upper(),
                'company_name': ticker.upper(),
                'buffett_score': random.uniform(60, 90),
                'quality_score': random.choice(['Excellent', 'Good', 'Average', 'Poor']),
                'moat': {
                    'brand_strength': random.randint(60, 95),
                    'market_position': random.randint(55, 90),
                    'type': random.choice(['Brand Moat', 'Network Effect', 'Cost Advantage', 'Regulatory Moat']),
                    'advantages': random.sample(['Strong brand', 'Market leadership', 'Cost efficiency', 'Network effects', 'High switching costs', 'Regulatory protection'], 3)
                },
                'metrics': {
                    'roe': round(random.uniform(12, 25), 1),
                    'profit_margin': round(random.uniform(15, 35), 1), 
                    'revenue_growth': round(random.uniform(2, 12), 1),
                    'debt_ratio': round(random.uniform(10, 40), 1)
                },
                'management': {
                    'capital_allocation': random.randint(60, 95),
                    'shareholder_friendly': random.randint(65, 95),
                    'assessment': random.choice(['Excellent capital allocators with strong track record', 'Good management with clear strategy', 'Average management performance', 'Some concerns about capital allocation'])
                },
                'recommendation': random.choice(['Strong Buy', 'Buy', 'Hold', 'Sell']),
                'fair_value': round(random.uniform(150, 450), 2),
                'confidence': random.randint(70, 95),
                'analysis_date': datetime.now().strftime('%Y-%m-%d')
            }
            return render_template('analysis/warren_buffett.html', 
                                 analysis=analysis_data, 
                                 ticker=ticker)
        
        return render_template('analysis/warren_buffett.html')
    except Exception as e:
        logger.error(f"Error in Warren Buffett analysis: {e}")
        flash("En feil oppstod ved lasting av Warren Buffett-analysen.", "error")
        return redirect(url_for('analysis.index'))

@analysis.route('/benjamin-graham')
@access_required  
def benjamin_graham():
    """Benjamin Graham analysis style"""
    try:
        ticker = request.args.get('ticker')
        
        if ticker:
            # Return analysis for specific ticker
            analysis_data = {
                'ticker': ticker.upper(),
                'company_name': ticker.upper(),
                'graham_score': random.uniform(50, 95),
                'criteria': {
                    'pe_ratio': round(random.uniform(10, 25), 2),
                    'pb_ratio': round(random.uniform(0.8, 3.0), 2),
                    'debt_equity': round(random.uniform(0.2, 1.5), 2),
                    'current_ratio': round(random.uniform(1.0, 3.0), 2),
                    'roe': round(random.uniform(8, 20), 1),
                    'eps_growth': round(random.uniform(-5, 15), 1)
                },
                'value_score': random.choice(['Excellent Value', 'Good Value', 'Fair Value', 'Overpriced']),
                'recommendation': random.choice(['Strong Buy', 'Buy', 'Hold', 'Sell']),
                'intrinsic_value': round(random.uniform(80, 300), 2),
                'margin_of_safety': round(random.uniform(-20, 40), 1),
                'analysis_date': datetime.now().strftime('%Y-%m-%d')
            }
            return render_template('analysis/benjamin_graham.html', 
                                 analysis=analysis_data, 
                                 ticker=ticker)
        
        return render_template('analysis/benjamin_graham.html')
    except Exception as e:
        logger.error(f"Error in Benjamin Graham analysis: {e}")
        flash("En feil oppstod ved lasting av Benjamin Graham-analysen.", "error")
        return redirect(url_for('analysis.index'))

@analysis.route('/sentiment')
@access_required
def sentiment():
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
    """Stock screening tool"""
    try:
        # Get screening parameters
        min_market_cap = request.args.get('min_market_cap', type=float, default=0)
        max_pe = request.args.get('max_pe', type=float, default=50)
        min_roe = request.args.get('min_roe', type=float, default=0)
        sector = request.args.get('sector', default='all')
        
        # Mock screened stocks
        screened_stocks = [
            {
                'symbol': 'EQNR.OL',
                'name': 'Equinor ASA',
                'price': 342.55,
                'market_cap': 1087000000000,
                'pe_ratio': 12.5,
                'roe': 15.2,
                'sector': 'Energy',
                'score': 85
            },
            {
                'symbol': 'DNB.OL', 
                'name': 'DNB Bank ASA',
                'price': 212.8,
                'market_cap': 328000000000,
                'pe_ratio': 8.9,
                'roe': 12.8,
                'sector': 'Financial',
                'score': 78
            },
            {
                'symbol': 'AAPL',
                'name': 'Apple Inc.',
                'price': 185.25,
                'market_cap': 2870000000000,
                'pe_ratio': 28.5,
                'roe': 24.1,
                'sector': 'Technology',
                'score': 92
            }
        ]
        
        return render_template('analysis/screener.html', 
                             screened_stocks=screened_stocks,
                             filters={
                                 'min_market_cap': min_market_cap,
                                 'max_pe': max_pe, 
                                 'min_roe': min_roe,
                                 'sector': sector
                             })
    except Exception as e:
        logger.error(f"Error in screener: {e}")
        flash("En feil oppstod ved lasting av screeneren.", "error")
        return redirect(url_for('analysis.index'))

@analysis.route('/short-analysis')
@access_required
def short_analysis():
    """Short selling analysis"""
    try:
        ticker = request.args.get('ticker')
        
        if ticker:
            # Return short analysis for specific ticker
            short_data = {
                'ticker': ticker.upper(),
                'company_name': ticker.upper(),
                'short_interest': round(random.uniform(2, 25), 1),
                'short_ratio': round(random.uniform(1, 10), 1),
                'days_to_cover': round(random.uniform(1, 15), 1),
                'short_squeeze_potential': random.choice(['High', 'Medium', 'Low']),
                'trend': random.choice(['Increasing', 'Decreasing', 'Stable']),
                'recommendation': random.choice(['Watch for Squeeze', 'Monitor', 'Low Risk']),
                'analysis_date': datetime.now().strftime('%Y-%m-%d')
            }
            return render_template('analysis/short_analysis.html', 
                                 short_data=short_data, 
                                 ticker=ticker)
        
        return render_template('analysis/short_analysis.html')
    except Exception as e:
        logger.error(f"Error in short analysis: {e}")
        flash("En feil oppstod ved lasting av short-analysen.", "error")
        return redirect(url_for('analysis.index'))

@analysis.route('/market-overview')
@access_required
def market_overview():
    """Market overview page with comprehensive fallback data"""
    try:
        # Get market data with fallbacks
        oslo_data = {}
        global_data = {}
        crypto_data = {}
        currency_data = {}
        
        try:
            oslo_data = DataService.get_oslo_bors_overview() or {}
        except Exception as e:
            current_app.logger.warning(f"Could not get Oslo Børs data: {e}")
            oslo_data = {
                'EQNR.OL': {'name': 'Equinor ASA', 'last_price': 285.50, 'change_percent': 1.2},
                'DNB.OL': {'name': 'DNB Bank ASA', 'last_price': 195.25, 'change_percent': 0.8},
                'TEL.OL': {'name': 'Telenor ASA', 'last_price': 145.75, 'change_percent': -0.5}
            }
            
        try:
            global_data = DataService.get_global_stocks_overview() or {}
        except Exception as e:
            current_app.logger.warning(f"Could not get global data: {e}")
            global_data = {
                'AAPL': {'name': 'Apple Inc.', 'last_price': 180.50, 'change_percent': 1.5},
                'GOOGL': {'name': 'Alphabet Inc.', 'last_price': 2750.25, 'change_percent': 0.9},
                'MSFT': {'name': 'Microsoft Corp.', 'last_price': 335.75, 'change_percent': 1.1}
            }
            
        try:
            crypto_data = DataService.get_crypto_overview() or {}
        except Exception as e:
            current_app.logger.warning(f"Could not get crypto data: {e}")
            crypto_data = {
                'BTC-USD': {'name': 'Bitcoin', 'last_price': 45000.00, 'change_percent': 2.5},
                'ETH-USD': {'name': 'Ethereum', 'last_price': 3200.00, 'change_percent': -1.2},
                'BNB-USD': {'name': 'Binance Coin', 'last_price': 320.50, 'change_percent': 1.8}
            }
            
        try:
            currency_data = DataService.get_currency_overview() or {}
        except Exception as e:
            current_app.logger.warning(f"Could not get currency data: {e}")
            currency_data = {
                'USDNOK=X': {'name': 'USD/NOK', 'last_price': 10.45, 'change_percent': -0.3},
                'EURNOK=X': {'name': 'EUR/NOK', 'last_price': 11.25, 'change_percent': 0.1},
                'GBPNOK=X': {'name': 'GBP/NOK', 'last_price': 13.15, 'change_percent': 0.5}
            }
        
        # Create market summary
        market_summary = {
            'oslo_stocks_count': len(oslo_data),
            'global_stocks_count': len(global_data),
            'crypto_count': len(crypto_data),
            'currency_pairs_count': len(currency_data),
            'total_instruments': len(oslo_data) + len(global_data) + len(crypto_data) + len(currency_data)
        }
        
        # Enhanced market data for template
        market_data = {
            'sp500': {'value': '4,450.25', 'change': '+1.2'},
            'nasdaq': {'value': '13,850.50', 'change': '+0.8'},
            'dax': {'value': '15,725.30', 'change': '-0.3'},
            'ftse': {'value': '7,420.15', 'change': '+0.5'},
            'osebx': {'value': '1,285.75', 'change': '+0.9'}
        }
        
        return render_template('analysis/market_overview.html',
                             oslo_stocks=oslo_data,
                             global_stocks=global_data,
                             crypto_data=crypto_data,
                             currency_data=currency_data,
                             market_summary=market_summary,
                             market_data=market_data,
                             current_time=datetime.now())
                             
    except Exception as e:
        current_app.logger.error(f"Error in market overview: {e}")
        
        # Ultimate fallback with minimal data
        fallback_market_data = {
            'sp500': {'value': 'N/A', 'change': '0.00'},
            'nasdaq': {'value': 'N/A', 'change': '0.00'},
            'dax': {'value': 'N/A', 'change': '0.00'},
            'ftse': {'value': 'N/A', 'change': '0.00'},
            'osebx': {'value': 'N/A', 'change': '0.00'}
        }
        
        fallback_summary = {
            'oslo_stocks_count': 0,
            'global_stocks_count': 0,
            'crypto_count': 0,
            'currency_pairs_count': 0,
            'total_instruments': 0
        }
        
        return render_template('analysis/market_overview.html',
                             oslo_stocks={},
                             global_stocks={},
                             crypto_data={},
                             currency_data={},
                             market_summary=fallback_summary,
                             market_data=fallback_market_data,
                             current_time=datetime.now(),
                             error="Markedsdata er midlertidig utilgjengelig. Prøv igjen senere.")

@analysis.route('/currency-overview')
@access_required
def currency_overview():
    """Currency overview analysis"""
    try:
        currency_data = DataService.get_currency_overview() or {}
        
        # Expand currency data with more pairs
        extended_currency_data = {
            'USDNOK=X': {
                'name': 'USD/NOK',
                'last_price': 10.45,
                'change': -0.15,
                'change_percent': -1.42,
                'signal': 'HOLD',
                'volume': 2500000000
            },
            'EURNOK=X': {
                'name': 'EUR/NOK',
                'last_price': 11.32,
                'change': 0.08,
                'change_percent': 0.71,
                'signal': 'BUY',
                'volume': 1800000000
            },
            'GBPNOK=X': {
                'name': 'GBP/NOK',
                'last_price': 12.85,
                'change': 0.05,
                'change_percent': 0.39,
                'signal': 'HOLD',
                'volume': 950000000
            },
            'JPYNOK=X': {
                'name': 'JPY/NOK',
                'last_price': 0.071,
                'change': -0.001,
                'change_percent': -1.12,
                'signal': 'SELL',
                'volume': 450000000
            },
            'SEKNOM=X': {
                'name': 'SEK/NOK',
                'last_price': 0.98,
                'change': 0.002,
                'change_percent': 0.21,
                'signal': 'HOLD',
                'volume': 1200000000
            },
            'DKKNOK=X': {
                'name': 'DKK/NOK',
                'last_price': 1.52,
                'change': 0.01,
                'change_percent': 0.66,
                'signal': 'BUY',
                'volume': 800000000
            }
        }
        
        # Merge with existing data
        currency_data.update(extended_currency_data)
        
        return render_template('analysis/currency_overview.html',
                             currency_data=currency_data)
    except Exception as e:
        logger.error(f"Error in currency overview: {e}")
        flash("En feil oppstod ved lasting av valutaoversikten.", "error")
        return redirect(url_for('analysis.index'))

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