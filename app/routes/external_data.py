from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..utils.access_control import access_required
try:
    from app.services.external_data import (
        get_stock_comprehensive_data, 
        get_insider_trading_data, 
        get_analyst_ratings,
        get_market_sentiment,
        external_data_service
    )
except ImportError:
    # Fallback dummy functions if service not available
    def get_stock_comprehensive_data(symbol):
        return {}
    def get_insider_trading_data(symbol):
        return []
    def get_analyst_ratings(symbol):
        return {}
    def get_market_sentiment(symbol):
        return {}
    external_data_service = None

from app.services.portfolio_service import get_ai_analysis
import logging

logger = logging.getLogger(__name__)

external_data_bp = Blueprint('external_data', __name__)

@external_data_bp.route('/external-analysis/<symbol>')
@login_required
def external_analysis(symbol):
    """Show comprehensive external analysis for a stock"""
    try:
        # Get comprehensive data from all external sources
        comprehensive_data = get_stock_comprehensive_data(symbol)
        
        # Get insider trading data
        insider_trades = get_insider_trading_data(symbol)
        
        # Get analyst ratings
        analyst_ratings = get_analyst_ratings(symbol)
        
        # Get market sentiment
        market_sentiment = get_market_sentiment(symbol)
        
        # Get our internal AI analysis for comparison
        ai_analysis = get_ai_analysis(symbol)
        
        return render_template('external_data/comprehensive_analysis.html',
                             symbol=symbol,
                             comprehensive_data=comprehensive_data,
                             insider_trades=insider_trades,
                             analyst_ratings=analyst_ratings,
                             market_sentiment=market_sentiment,
                             ai_analysis=ai_analysis)
                             
    except Exception as e:
        logger.error(f"Error in external analysis for {symbol}: {e}")
        return render_template('error.html', error="Kunne ikke hente eksterne data"), 500

@external_data_bp.route('/api/external-data/<symbol>')
@login_required
def api_external_data(symbol):
    """API endpoint for external data"""
    try:
        data_type = request.args.get('type', 'comprehensive')
        
        if data_type == 'insider':
            insider_trades = get_insider_trading_data(symbol)
            return jsonify({
                'symbol': symbol,
                'insider_trades': [
                    {
                        'insider_name': trade.insider_name,
                        'position': trade.position,
                        'transaction_type': trade.transaction_type,
                        'shares': trade.shares,
                        'price': trade.price,
                        'value': trade.value,
                        'date': trade.date.isoformat(),
                        'source': trade.source
                    } for trade in insider_trades
                ]
            })
        
        elif data_type == 'analysts':
            analyst_ratings = get_analyst_ratings(symbol)
            return jsonify({
                'symbol': symbol,
                'analyst_ratings': [
                    {
                        'analyst_firm': rating.analyst_firm,
                        'rating': rating.rating,
                        'price_target': rating.price_target,
                        'date': rating.date.isoformat(),
                        'source': rating.source
                    } for rating in analyst_ratings
                ]
            })
        
        elif data_type == 'sentiment':
            sentiment = get_market_sentiment(symbol)
            return jsonify({
                'symbol': symbol,
                'sentiment': {
                    'sentiment_score': sentiment.sentiment_score,
                    'bullish_percent': sentiment.bullish_percent,
                    'bearish_percent': sentiment.bearish_percent,
                    'neutral_percent': sentiment.neutral_percent,
                    'source': sentiment.source,
                    'date': sentiment.date.isoformat()
                }
            })
        
        else:  # comprehensive
            comprehensive_data = get_stock_comprehensive_data(symbol)
            return jsonify(comprehensive_data)
            
    except Exception as e:
        logger.error(f"Error in API external data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@external_data_bp.route('/api/market-overview')
@access_required
def api_market_overview():
    """API endpoint for market overview"""
    try:
        market_data = external_data_service.get_market_overview()
        return jsonify(market_data)
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return jsonify({'error': str(e)}), 500

@external_data_bp.route('/insider-trading')
@login_required
def insider_trading_overview():
    """Show insider trading overview page"""
    try:
        # Get insider activity for top Norwegian stocks
        top_stocks = ['EQNR', 'DNB', 'TEL', 'AKER', 'MOWI', 'NOR', 'YAR', 'STL']
        
        insider_activity = {}
        for stock in top_stocks:
            try:
                trades = get_insider_trading_data(stock)
                if trades:
                    insider_activity[stock] = trades[:5]  # Latest 5 trades
            except Exception as e:
                logger.error(f"Error getting insider data for {stock}: {e}")
                continue
        
        return render_template('external_data/insider_trading.html',
                             insider_activity=insider_activity)
                             
    except Exception as e:
        logger.error(f"Error in insider trading overview: {e}")
        return render_template('error.html', error="Kunne ikke hente innsidehandel data"), 500

@external_data_bp.route('/analyst-coverage')
@login_required
def analyst_coverage():
    """Show analyst coverage overview"""
    try:
        # Get analyst coverage for top stocks
        top_stocks = ['EQNR', 'DNB', 'TEL', 'AKER', 'MOWI']
        
        analyst_coverage = {}
        for stock in top_stocks:
            try:
                ratings = get_analyst_ratings(stock)
                comprehensive = get_stock_comprehensive_data(stock)
                
                analyst_coverage[stock] = {
                    'ratings': ratings,
                    'consensus': comprehensive.get('analyst_consensus', {}),
                    'technical': comprehensive.get('technical_analysis', {})
                }
            except Exception as e:
                logger.error(f"Error getting analyst data for {stock}: {e}")
                continue
        
        return render_template('external_data/analyst_coverage.html',
                             analyst_coverage=analyst_coverage)
                             
    except Exception as e:
        logger.error(f"Error in analyst coverage: {e}")
        return render_template('error.html', error="Kunne ikke hente analytiker data"), 500

@external_data_bp.route('/market-intelligence')
@login_required
def market_intelligence():
    """Comprehensive market intelligence dashboard"""
    try:
        # Get market overview
        market_overview = external_data_service.get_market_overview()
        
        # Get data for featured stocks
        featured_stocks = ['EQNR', 'DNB', 'TEL']
        featured_analysis = {}
        
        for stock in featured_stocks:
            try:
                comprehensive = get_stock_comprehensive_data(stock)
                ai_analysis = get_ai_analysis(stock)
                
                featured_analysis[stock] = {
                    'external': comprehensive,
                    'ai': ai_analysis
                }
            except Exception as e:
                logger.error(f"Error getting featured analysis for {stock}: {e}")
                continue
        
        return render_template('external_data/market_intelligence.html',
                             market_overview=market_overview,
                             featured_analysis=featured_analysis)
                             
    except Exception as e:
        logger.error(f"Error in market intelligence: {e}")
        return render_template('error.html', error="Kunne ikke hente markedsintelligens"), 500
