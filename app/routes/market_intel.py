"""
Market Intelligence Routes - for insider trading, institutional ownership, and market data
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from ..utils.access_control import access_required, demo_access

# Import service here to avoid issues
try:
    from ..services.external_apis import ExternalAPIService
except ImportError as e:
    print(f"Warning: Could not import ExternalAPIService: {e}")
    ExternalAPIService = None

market_intel = Blueprint('market_intel', __name__, url_prefix='/market-intel')

@market_intel.route('/')
@access_required
def index():
    """Market intelligence dashboard"""
    try:
        # Check if service is available
        if not ExternalAPIService:
            return render_template('market_intel/index.html',
                                 insider_data={},
                                 sector_performance={},
                                 earnings_calendar=[],
                                 crypto_fear_greed={},
                                 economic_indicators={},
                                 market_news=[],
                                 error="Ekstern data-service er ikke tilgjengelig.")
        
        # Get recent insider trading for popular stocks
        popular_tickers = ['EQNR.OL', 'DNB.OL', 'AAPL', 'MSFT', 'TSLA']
        insider_data = {}
        
        for ticker in popular_tickers[:3]:  # Limit to avoid API rate limits
            try:
                insider_data[ticker] = ExternalAPIService.get_insider_trading(ticker, limit=5) or []
            except:
                insider_data[ticker] = []
        
        # Get sector performance with fallback
        try:
            sector_performance = ExternalAPIService.get_sector_performance() or {}
        except:
            sector_performance = {}
        
        # Get earnings calendar with fallback
        try:
            earnings_calendar = ExternalAPIService.get_earnings_calendar(days_ahead=14) or []
        except:
            earnings_calendar = []
        
        # Get crypto fear & greed index with fallback
        try:
            crypto_fear_greed = ExternalAPIService.get_crypto_fear_greed_index() or {}
        except:
            crypto_fear_greed = {}
        
        # Get economic indicators with fallback
        try:
            economic_indicators = ExternalAPIService.get_economic_indicators() or {}
        except:
            economic_indicators = {}
        
        # Get market news with fallback
        try:
            market_news = ExternalAPIService.get_market_news(limit=10) or []
        except:
            market_news = []
        
        return render_template('market_intel/index.html',
                             insider_data=insider_data,
                             sector_performance=sector_performance,
                             earnings_calendar=earnings_calendar,
                             crypto_fear_greed=crypto_fear_greed,
                             economic_indicators=economic_indicators,
                             market_news=market_news)
    except Exception as e:
        print(f"Error in market_intel index: {e}")
        # Return basic template with empty data instead of error page
        return render_template('market_intel/index.html',
                             insider_data={},
                             sector_performance={},
                             earnings_calendar=[],
                             crypto_fear_greed={},
                             economic_indicators={},
                             market_news=[],
                             error="Kunne ikke hente alle markedsdata. Viser tilgjengelig informasjon.")

@market_intel.route('/insider-trading')
@demo_access
def insider_trading():
    """Dedicated insider trading page"""
    ticker = request.args.get('ticker', 'EQNR.OL')
    
    try:
        # Check if user has access to real data
        has_access = current_user.is_authenticated and (
            current_user.email in {'helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com', 'tonjekit91@gmail.com'} or
            (hasattr(current_user, 'has_active_subscription') and current_user.has_active_subscription())
        )
        
        # Validate ticker format
        if not ticker or len(ticker) < 2:
            ticker = 'EQNR.OL'
        
        # Clean ticker (remove extra spaces, convert to uppercase)
        ticker = ticker.strip().upper()
        
        # For demo users or users without access, show demo template
        if not has_access:
            return render_template('insider_trading/demo_insider_trading.html',
                                 ticker=ticker,
                                 demo_data=[
                                     {
                                         'date': '2024-07-20',
                                         'insider_name': 'John Doe',
                                         'title': 'CEO',
                                         'transaction_type': 'Purchase',
                                         'shares': 10000,
                                         'price': 245.50,
                                         'value': 2455000
                                     },
                                     {
                                         'date': '2024-07-18',
                                         'insider_name': 'Jane Smith',
                                         'title': 'CFO',
                                         'transaction_type': 'Sale',
                                         'shares': 5000,
                                         'price': 244.00,
                                         'value': 1220000
                                     }
                                 ],
                                 restricted=True)
        
        # Check if service is available
        if not ExternalAPIService:
            return render_template('market_intel/insider_trading.html',
                                 ticker=ticker,
                                 insider_data=[],
                                 institutional_data={},
                                 error="Ekstern data-service er ikke tilgjengelig.")
        
        # Get insider trading data with fallback
        try:
            insider_data = ExternalAPIService.get_insider_trading(ticker, limit=25) or []
        except Exception as e:
            print(f"Error getting insider data for {ticker}: {e}")
            insider_data = []
        
        # Get institutional ownership data with fallback
        try:
            institutional_data = ExternalAPIService.get_institutional_ownership(ticker) or {}
        except Exception as e:
            print(f"Error getting institutional data for {ticker}: {e}")
            institutional_data = {}
        
        return render_template('market_intel/insider_trading.html',
                             ticker=ticker,
                             insider_data=insider_data,
                             institutional_data=institutional_data)
                             
    except Exception as e:
        print(f"Error in insider_trading route: {e}")
        # Return the template with empty data instead of error page
        return render_template('market_intel/insider_trading.html',
                             ticker=ticker,
                             insider_data=[],
                             institutional_data={},
                             error="Kunne ikke hente all innsidehandel data. Viser tilgjengelig informasjon.")

@market_intel.route('/earnings-calendar')
@access_required
def earnings_calendar():
    """Earnings calendar page"""
    days_ahead = request.args.get('days', 30, type=int)
    
    try:
        earnings_data = ExternalAPIService.get_earnings_calendar(days_ahead=days_ahead)
        
        return render_template('market_intel/earnings_calendar.html',
                             earnings_data=earnings_data,
                             days_ahead=days_ahead)
    except Exception as e:
        return render_template('error.html', error="Kunne ikke hente resultatkalender.")

@market_intel.route('/sector-analysis')
@access_required
def sector_analysis():
    """Sector performance analysis"""
    try:
        sector_data = ExternalAPIService.get_sector_performance()
        screener_data = ExternalAPIService.get_stock_screener(
            market_cap_min=1000000000,  # 1B+ market cap
            volume_min=1000000          # 1M+ volume
        )
        
        return render_template('market_intel/sector_analysis.html',
                             sector_data=sector_data,
                             screener_data=screener_data[:20])  # Top 20
    except Exception as e:
        return render_template('error.html', error="Kunne ikke hente sektoranalyse.")

@market_intel.route('/economic-indicators')
@access_required
def economic_indicators():
    """Economic indicators and market overview"""
    try:
        economic_data = ExternalAPIService.get_economic_indicators()
        crypto_fear_greed = ExternalAPIService.get_crypto_fear_greed_index()
        
        return render_template('market_intel/economic_indicators.html',
                             economic_data=economic_data,
                             crypto_fear_greed=crypto_fear_greed)
    except Exception as e:
        return render_template('error.html', error="Kunne ikke hente økonomiske indikatorer.")

# API endpoints for AJAX requests
@market_intel.route('/api/insider-trading/<ticker>')
@access_required
def api_insider_trading(ticker):
    """API endpoint for insider trading data"""
    try:
        limit = request.args.get('limit', 10, type=int)
        data = ExternalAPIService.get_insider_trading(ticker, limit=limit)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_intel.route('/api/institutional-ownership/<ticker>')
@access_required
def api_institutional_ownership(ticker):
    """API endpoint for institutional ownership data"""
    try:
        data = ExternalAPIService.get_institutional_ownership(ticker)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_intel.route('/api/sector-performance')
@access_required
def api_sector_performance():
    """API endpoint for sector performance"""
    try:
        data = ExternalAPIService.get_sector_performance()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_intel.route('/api/earnings-calendar')
@access_required
def api_earnings_calendar():
    """API endpoint for earnings calendar"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        data = ExternalAPIService.get_earnings_calendar(days_ahead=days_ahead)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@market_intel.route('/api/crypto-fear-greed')
@access_required
def api_crypto_fear_greed():
    """API endpoint for crypto fear & greed index"""
    try:
        data = ExternalAPIService.get_crypto_fear_greed_index()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
