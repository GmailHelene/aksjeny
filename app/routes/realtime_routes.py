from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..utils.access_control import access_required
from app.services.realtime_data_service import RealTimeDataService
from app.models import User
import logging

# Create blueprint
realtime_bp = Blueprint('realtime', __name__, url_prefix='/realtime')

# Get or create the realtime data service instance
realtime_service = RealTimeDataService()

@realtime_bp.route('/')
@realtime_bp.route('/dashboard')
def dashboard():
    """Real-time market data dashboard"""
    try:
        # Check if user is authenticated for personalized features
        user_authenticated = current_user.is_authenticated
        
        # Get basic market summary for initial load
        market_summary = realtime_service.get_market_summary()
        
        # Get trending stocks
        trending_stocks = realtime_service.get_trending_stocks(limit=10)
        
        # Render template with initial data
        return render_template('realtime/dashboard.html',
                             page_title='Real-time Markedsdata',
                             market_summary=market_summary,
                             trending_stocks=trending_stocks,
                             user_authenticated=user_authenticated)
    
    except Exception as e:
        logging.error(f"Error loading realtime dashboard: {str(e)}")
        return render_template('error.html', 
                             error_message="Kunne ikke laste real-time dashboard"), 500

@realtime_bp.route('/api/market-summary')
@access_required
def api_market_summary():
    """API endpoint for market summary data"""
    try:
        summary = realtime_service.get_market_summary()
        return jsonify({
            'status': 'success',
            'data': summary
        })
    except Exception as e:
        logging.error(f"Error getting market summary: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke hente markedsoversikt'
        }), 500

@realtime_bp.route('/api/trending-stocks')
@access_required
def api_trending_stocks():
    """API endpoint for trending stocks"""
    try:
        limit = request.args.get('limit', 10, type=int)
        stocks = realtime_service.get_trending_stocks(limit=limit)
        
        return jsonify({
            'status': 'success',
            'data': {'stocks': stocks}
        })
    except Exception as e:
        logging.error(f"Error getting trending stocks: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke hente trending aksjer'
        }), 500

@realtime_bp.route('/api/price-history/<symbol>')
@access_required
def api_price_history(symbol):
    """API endpoint for stock price history"""
    try:
        days = request.args.get('days', 7, type=int)
        history = realtime_service.get_price_history(symbol, days=days)
        
        return jsonify({
            'status': 'success',
            'data': {
                'symbol': symbol,
                'history': history
            }
        })
    except Exception as e:
        logging.error(f"Error getting price history for {symbol}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Kunne ikke hente prishistorikk for {symbol}'
        }), 500

@realtime_bp.route('/api/alerts', methods=['GET'])
@login_required
def api_get_alerts():
    """Get user's price alerts"""
    try:
        alerts = realtime_service.get_user_alerts(current_user.id)
        
        # Convert alerts to serializable format
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'id': alert.id,
                'symbol': alert.symbol,
                'trigger_price': alert.trigger_price,
                'alert_type': alert.alert_type,
                'is_active': alert.is_active,
                'created_at': alert.created_at.isoformat() if alert.created_at else None
            })
        
        return jsonify({
            'status': 'success',
            'data': {'alerts': alert_data}
        })
    except Exception as e:
        logging.error(f"Error getting user alerts: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke hente prisalarmer'
        }), 500

@realtime_bp.route('/api/alerts', methods=['POST'])
@login_required
def api_create_alert():
    """Create a new price alert"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['symbol', 'trigger_price', 'alert_type']):
            return jsonify({
                'status': 'error',
                'message': 'Manglende påkrevde felt'
            }), 400
        
        # Create alert through realtime service
        alert = realtime_service.create_price_alert(
            user_id=current_user.id,
            symbol=data['symbol'].upper(),
            trigger_price=float(data['trigger_price']),
            alert_type=data['alert_type']
        )
        
        if alert:
            return jsonify({
                'status': 'success',
                'data': {
                    'id': alert.id,
                    'symbol': alert.symbol,
                    'trigger_price': alert.trigger_price,
                    'alert_type': alert.alert_type
                },
                'message': 'Prisalarm opprettet'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Kunne ikke opprette prisalarm'
            }), 500
            
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': 'Ugyldig prisverdi'
        }), 400
    except Exception as e:
        logging.error(f"Error creating price alert: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke opprette prisalarm'
        }), 500

@realtime_bp.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
@login_required
def api_delete_alert(alert_id):
    """Delete a price alert"""
    try:
        success = realtime_service.remove_price_alert(alert_id, current_user.id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Prisalarm fjernet'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Kunne ikke fjerne prisalarm'
            }), 404
            
    except Exception as e:
        logging.error(f"Error deleting alert {alert_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke fjerne prisalarm'
        }), 500

@realtime_bp.route('/api/statistics')
@access_required
def api_statistics():
    """Get real-time service statistics"""
    try:
        stats = realtime_service.get_statistics()
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        logging.error(f"Error getting statistics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke hente statistikk'
        }), 500

@realtime_bp.route('/api/health')
def api_health():
    """Health check endpoint for real-time service"""
    try:
        stats = realtime_service.get_statistics()
        
        # Check if service is healthy
        is_healthy = (
            stats.get('active_connections', 0) >= 0 and
            stats.get('is_running', False)
        )
        
        status_code = 200 if is_healthy else 503
        
        return jsonify({
            'status': 'healthy' if is_healthy else 'unhealthy',
            'service': 'realtime_data_service',
            'statistics': stats,
            'timestamp': realtime_service._get_current_time().isoformat()
        }), status_code
        
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'service': 'realtime_data_service',
            'message': str(e)
        }), 503

@realtime_bp.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard for real-time service monitoring"""
    try:
        # Check if user has admin rights (you might want to add this to your User model)
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # For now, allow all authenticated users - adjust based on your admin logic
        # if not current_user.is_admin:
        #     return redirect(url_for('main.dashboard'))
        
        # Get comprehensive statistics
        stats = realtime_service.get_statistics()
        
        return render_template('realtime/admin.html',
                             page_title='Real-time Admin Dashboard',
                             statistics=stats)
        
    except Exception as e:
        logging.error(f"Error loading admin dashboard: {str(e)}")
        return render_template('error.html',
                             error_message="Kunne ikke laste admin dashboard"), 500

@realtime_bp.route('/admin/restart', methods=['POST'])
@login_required
def admin_restart_service():
    """Restart the real-time data service"""
    try:
        # Check admin permissions here
        # if not current_user.is_admin:
        #     return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        # Stop and restart service
        realtime_service.stop()
        realtime_service.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Real-time service restarted'
        })
        
    except Exception as e:
        logging.error(f"Error restarting service: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Kunne ikke restarte tjenesten'
        }), 500

# Error handlers for the blueprint
@realtime_bp.errorhandler(404)
def not_found(error):
    return render_template('error.html',
                         error_message="Siden ble ikke funnet"), 404

@realtime_bp.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_message="Intern serverfeil"), 500
