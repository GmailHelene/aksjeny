"""
Real-time data API endpoints
"""
from flask import Blueprint, jsonify, request
from ..services.realtime_data_service import real_time_service
from ..utils.access_control import access_required
from ..models.user import User
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

realtime_api = Blueprint('realtime_api', __name__, url_prefix='/api/realtime')

@realtime_api.route('/price/<ticker>')
@access_required
def get_live_price(ticker):
    """Get live price for a specific ticker"""
    try:
        category = request.args.get('category', 'oslo')
        data = real_time_service.get_live_price(ticker, category)
        
        if data:
            return jsonify({
                'success': True,
                'data': {
                    'ticker': data['ticker'],
                    'current_price': round(data['current_price'], 2),
                    'change': round(data['change'], 2),
                    'change_percent': round(data['change_percent'], 2),
                    'volume': data['volume'],
                    'last_updated': data['last_updated'].isoformat(),
                    'category': data['category']
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Data not available'
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_live_price: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@realtime_api.route('/market-summary')
@access_required
def get_market_summary():
    """Get real-time market summary"""
    try:
        summary = real_time_service.get_market_summary()
        
        # Format the response
        formatted_summary = {}
        for market, data in summary.items():
            if market == 'last_updated':
                formatted_summary[market] = data.isoformat() if hasattr(data, 'isoformat') else str(data)
            elif isinstance(data, dict) and 'last_updated' in data:
                formatted_data = data.copy()
                if hasattr(data['last_updated'], 'isoformat'):
                    formatted_data['last_updated'] = data['last_updated'].isoformat()
                formatted_summary[market] = formatted_data
            else:
                formatted_summary[market] = data
        
        return jsonify({
            'success': True,
            'data': formatted_summary
        })
        
    except Exception as e:
        logger.error(f"Error in get_market_summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@realtime_api.route('/trending')
@access_required  
def get_trending_stocks():
    """Get trending stocks"""
    try:
        limit = request.args.get('limit', 10, type=int)
        trending = real_time_service.get_trending_stocks(limit)
        
        # Format the response
        formatted_trending = []
        for stock in trending:
            formatted_trending.append({
                'ticker': stock['ticker'],
                'current_price': round(stock['current_price'], 2),
                'change': round(stock['change'], 2),
                'change_percent': round(stock['change_percent'], 2),
                'volume': stock['volume'],
                'category': stock['category'],
                'last_updated': stock['last_updated'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': formatted_trending
        })
        
    except Exception as e:
        logger.error(f"Error in get_trending_stocks: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@realtime_api.route('/batch-prices')
@access_required
def get_batch_prices():
    """Get prices for multiple tickers"""
    try:
        tickers = request.args.get('tickers', '').split(',')
        category = request.args.get('category', 'oslo')
        
        if not tickers or tickers == ['']:
            return jsonify({
                'success': False,
                'error': 'No tickers provided'
            }), 400
        
        results = {}
        for ticker in tickers:
            ticker = ticker.strip()
            if ticker:
                data = real_time_service.get_live_price(ticker, category)
                if data:
                    results[ticker] = {
                        'current_price': round(data['current_price'], 2),
                        'change': round(data['change'], 2),
                        'change_percent': round(data['change_percent'], 2),
                        'volume': data['volume'],
                        'last_updated': data['last_updated'].isoformat()
                    }
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Error in get_batch_prices: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@realtime_api.route('/start-updates')
def start_real_time_updates():
    """Start real-time background updates (admin only)"""
    try:
        if current_user.is_authenticated and (current_user.is_admin or 
            current_user.email in ['helene@luxushair.com', 'helene@luxushair.com', 'helene721@gmail.com']):
            
            real_time_service.start_background_updates()
            return jsonify({
                'success': True,
                'message': 'Real-time updates started'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 401
            
    except Exception as e:
        logger.error(f"Error starting real-time updates: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@realtime_api.route('/stop-updates')
def stop_real_time_updates():
    """Stop real-time background updates (admin only)"""
    try:
        if current_user.is_authenticated and (current_user.is_admin or 
            current_user.email in ['helene@luxushair.com', 'helene@luxushair.com', 'helene721@gmail.com']):
            
            real_time_service.stop_background_updates()
            return jsonify({
                'success': True,
                'message': 'Real-time updates stopped'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 401
            
    except Exception as e:
        logger.error(f"Error stopping real-time updates: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@realtime_api.route('/status')
def get_service_status():
    """Get real-time service status"""
    try:
        return jsonify({
            'success': True,
            'data': {
                'service_running': real_time_service.running,
                'cache_size': len(real_time_service.cache),
                'update_interval': real_time_service.update_interval,
                'cache_duration': real_time_service.cache_duration
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
