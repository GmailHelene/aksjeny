"""
Social sentiment analysis routes
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import current_user
from ..utils.access_control import access_required, premium_required
from ..services.external_apis import ExternalAPIService
from ..services.data_service import DataService
from datetime import datetime

# Create blueprint
social_sentiment = Blueprint('social_sentiment', __name__, url_prefix='/features')

@social_sentiment.route('/social-sentiment')
@access_required
def social_sentiment_page():
    """Show social sentiment analysis page"""
    ticker = request.args.get('ticker')
    
    if ticker:
        # Get sentiment data for specific ticker
        try:
            sentiment_data = ExternalAPIService.get_social_sentiment(ticker)
            stock_info = DataService.get_stock_info(ticker)
            
            return render_template('features/social_sentiment.html', 
                                 ticker=ticker,
                                 sentiment_data=sentiment_data,
                                 stock_info=stock_info,
                                 last_updated=datetime.now().strftime('%d.%m.%Y %H:%M'))
        except Exception as e:
            current_app.logger.error(f"Error getting social sentiment for {ticker}: {str(e)}")
            return render_template('features/social_sentiment.html', 
                                 ticker=ticker,
                                 error="Could not load sentiment data")
    
    # Show overview of trending stocks
    try:
        trending = DataService.get_trending_stocks()
        return render_template('features/social_sentiment.html', 
                             trending=trending,
                             last_updated=datetime.now().strftime('%d.%m.%Y %H:%M'))
    except Exception as e:
        current_app.logger.error(f"Error getting trending stocks: {str(e)}")
        return render_template('features/social_sentiment.html', 
                             trending=[],
                             error="Could not load trending data")

@social_sentiment.route('/api/social-sentiment/<ticker>')
@access_required
def api_social_sentiment(ticker):
    """API endpoint for social sentiment data"""
    try:
        sentiment = ExternalAPIService.get_social_sentiment(ticker)
        return jsonify({
            'success': True,
            'data': sentiment,
            'ticker': ticker,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
