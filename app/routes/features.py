"""
New features routes for analyst recommendations and AI predictions
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from ..utils.access_control import access_required
from ..models.user import User
from datetime import datetime, timedelta
import random

# Create blueprint for new features
features = Blueprint('features', __name__, url_prefix='/features')

@features.route('/ai-predictions')
@login_required
@access_required
def ai_predictions():
    """AI predictions page"""
    ticker = request.args.get('ticker')
    
    try:
        if ticker:
            # Mock prediction data for single stock
            predictions = {
                'ticker': ticker.upper(),
                'current_price': round(random.uniform(50, 500), 2),
                'predicted_price': round(random.uniform(50, 500), 2),
                'change_percent': round(random.uniform(-10, 10), 2),
                'confidence': round(random.uniform(0.6, 0.95), 2),
                'key_factors': [
                    'Positiv markedstrend',
                    'Sterk kvartalsrapport',
                    'Økt handelsvolum',
                    'Tekniske indikatorer positive'
                ],
                'dates': [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(8)],
                'predicted_values': [round(random.uniform(50, 500), 2) for _ in range(8)],
                'confidence_upper': [round(random.uniform(50, 500), 2) for _ in range(8)],
                'confidence_lower': [round(random.uniform(50, 500), 2) for _ in range(8)]
            }
            predictions['change_percent'] = round(
                ((predictions['predicted_price'] - predictions['current_price']) / predictions['current_price']) * 100, 
                2
            )
            stock_info = {'name': f'{ticker} Company'}
        else:
            # Mock data for overview
            predictions = []
            for t in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']:
                current = round(random.uniform(50, 500), 2)
                predicted = round(random.uniform(50, 500), 2)
                predictions.append({
                    'ticker': t,
                    'current_price': current,
                    'predicted_price': predicted,
                    'change_percent': round(((predicted - current) / current) * 100, 2),
                    'confidence': round(random.uniform(0.6, 0.95), 2)
                })
            stock_info = None
        
        return render_template(
            'features/ai_predictions.html',
            ticker=ticker,
            predictions=predictions,
            stock_info=stock_info,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        current_app.logger.error(f"Error in AI predictions: {str(e)}")
        return render_template(
            'features/ai_predictions.html',
            error="Kunne ikke generere AI-prediksjon. Prøv igjen senere.",
            ticker=ticker
        )

@features.route('/social-sentiment')
@login_required
@access_required
def social_sentiment():
    """Social sentiment analysis page"""
    ticker = request.args.get('ticker')
    
    try:
        # Mock data for now
        if ticker:
            sentiment_data = {
                'ticker': ticker,
                'sentiment': round(random.uniform(-1, 1), 2),
                'reddit': {
                    'mention': random.randint(10, 100),
                    'positiveMention': random.randint(5, 50),
                    'negativeMention': random.randint(5, 30)
                },
                'twitter': {
                    'mention': random.randint(50, 500),
                    'positiveMention': random.randint(20, 200),
                    'negativeMention': random.randint(10, 100)
                }
            }
            stock_info = {'name': f'{ticker} Company'}
        else:
            sentiment_data = None
            stock_info = None
            
        return render_template(
            'features/social_sentiment.html',
            ticker=ticker,
            sentiment_data=sentiment_data,
            stock_info=stock_info,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        current_app.logger.error(f"Error in social sentiment: {str(e)}")
        return render_template(
            'features/social_sentiment.html',
            error="Kunne ikke hente sentiment data. Prøv igjen senere.",
            ticker=ticker
        )

@features.route('/analyst-recommendations')
@login_required
@access_required
def analyst_recommendations():
    """Analyst recommendations page"""
    ticker = request.args.get('ticker')
    
    try:
        # Mock data for now
        if ticker:
            analyst_data = {
                'ticker': ticker,
                'consensus': 'Buy',
                'analyst_count': random.randint(5, 20),
                'target_low': round(random.uniform(50, 100), 2),
                'target_mean': round(random.uniform(100, 150), 2),
                'target_high': round(random.uniform(150, 200), 2),
                'strong_buy': random.randint(1, 5),
                'buy': random.randint(1, 5),
                'hold': random.randint(1, 5),
                'sell': random.randint(0, 2),
                'strong_sell': random.randint(0, 1)
            }
            stock_info = {'name': f'{ticker} Company'}
        else:
            analyst_data = None
            stock_info = None
            
        return render_template(
            'features/analyst_recommendations.html',
            ticker=ticker,
            analyst_data=analyst_data,
            stock_info=stock_info,
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        current_app.logger.error(f"Error in analyst recommendations: {str(e)}")
        return render_template(
            'features/analyst_recommendations.html',
            error="Kunne ikke hente analytiker anbefalinger. Prøv igjen senere.",
            ticker=ticker
        )

@features.route('/api/create-price-alert', methods=['POST'])
@access_required
def api_create_price_alert():
    """API endpoint for creating price alerts"""
    try:
        data = request.get_json()
        ticker = data.get('ticker')
        price_threshold = data.get('price_threshold')
        alert_type = data.get('alert_type', 'above')  # 'above' or 'below'
        
        if not ticker or not price_threshold:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Here you would normally save to database
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Price alert created successfully',
            'alert': {
                'ticker': ticker,
                'price_threshold': price_threshold,
                'alert_type': alert_type
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@features.route('/api/predict/<ticker>')
@login_required
@access_required
def api_predict(ticker):
    """API endpoint for AI predictions"""
    try:
        # Mock prediction
        current = round(random.uniform(50, 500), 2)
        predicted = round(random.uniform(50, 500), 2)
        
        return jsonify({
            'success': True,
            'ticker': ticker.upper(),
            'current_price': current,
            'predicted_price': predicted,
            'change_percent': round(((predicted - current) / current) * 100, 2),
            'confidence': round(random.uniform(0.6, 0.95), 2),
            'prediction_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        })
    except Exception as e:
        current_app.logger.error(f"Error in prediction API: {str(e)}")
        return jsonify({'success': False, 'error': 'Prediction failed'}), 500
