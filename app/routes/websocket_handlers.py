"""
WebSocket Event Handlers for Real-time Market Data
=================================================

WebSocket event handlers providing real-time market data streaming,
portfolio updates, and price alerts.

Author: Aksjeradar Development Team
Date: July 2025
"""

from flask import request, session
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
import logging
from ..services.realtime_data_service import get_real_time_service
from ..extensions import socketio

logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    session_id = request.sid
    user_id = current_user.id if current_user.is_authenticated else None
    
    logger.info(f"WebSocket connected: {session_id} (user: {user_id})")
    
    # Get real-time service and notify of connection
    rt_service = get_real_time_service(socketio)
    rt_service.handle_client_connect(session_id)
    
    # Send welcome message
    emit('connection_status', {
        'status': 'connected',
        'session_id': session_id,
        'user_authenticated': current_user.is_authenticated,
        'timestamp': str(rt_service.stats['start_time'])
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    session_id = request.sid
    user_id = current_user.id if current_user.is_authenticated else None
    
    logger.info(f"WebSocket disconnected: {session_id} (user: {user_id})")
    
    # Notify real-time service
    rt_service = get_real_time_service()
    if rt_service:
        rt_service.handle_client_disconnect(session_id)

@socketio.on('subscribe_symbol')
def handle_subscribe_symbol(data):
    """Handle symbol subscription request"""
    try:
        session_id = request.sid
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            emit('error', {'message': 'Symbol is required'})
            return
        
        rt_service = get_real_time_service()
        if rt_service:
            rt_service.subscribe_to_symbol(session_id, symbol)
            
            # Join room for this symbol
            join_room(f'symbol_{symbol}')
            
            # Send current data if available
            current_data = rt_service.get_live_price(symbol.replace('.OL', ''), 'oslo')
            if current_data:
                emit('market_data_update', current_data)
            
            emit('subscription_response', {
                'symbol': symbol,
                'status': 'subscribed',
                'message': f'Successfully subscribed to {symbol}'
            })
            
            logger.info(f"Session {session_id} subscribed to {symbol}")
        
    except Exception as e:
        logger.error(f"Error in subscribe_symbol: {e}")
        emit('error', {'message': 'Failed to subscribe to symbol'})

@socketio.on('unsubscribe_symbol')
def handle_unsubscribe_symbol(data):
    """Handle symbol unsubscription request"""
    try:
        session_id = request.sid
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            emit('error', {'message': 'Symbol is required'})
            return
        
        rt_service = get_real_time_service()
        if rt_service:
            rt_service.unsubscribe_from_symbol(session_id, symbol)
            
            # Leave room for this symbol
            leave_room(f'symbol_{symbol}')
            
            emit('subscription_response', {
                'symbol': symbol,
                'status': 'unsubscribed',
                'message': f'Successfully unsubscribed from {symbol}'
            })
            
            logger.info(f"Session {session_id} unsubscribed from {symbol}")
        
    except Exception as e:
        logger.error(f"Error in unsubscribe_symbol: {e}")
        emit('error', {'message': 'Failed to unsubscribe from symbol'})

@socketio.on('add_price_alert')
def handle_add_price_alert(data):
    """Handle adding a price alert"""
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required for price alerts'})
            return
        
        symbol = data.get('symbol', '').upper()
        trigger_price = float(data.get('trigger_price', 0))
        alert_type = data.get('alert_type', 'above')
        
        if not symbol or trigger_price <= 0:
            emit('error', {'message': 'Valid symbol and trigger price required'})
            return
        
        rt_service = get_real_time_service()
        if rt_service:
            alert_id = rt_service.add_price_alert(
                current_user.id, symbol, trigger_price, alert_type
            )
            
            emit('alert_response', {
                'alert_id': alert_id,
                'symbol': symbol,
                'trigger_price': trigger_price,
                'alert_type': alert_type,
                'status': 'created',
                'message': f'Price alert created for {symbol} at {trigger_price}'
            })
            
            logger.info(f"Price alert created: {alert_id} for user {current_user.id}")
        
    except Exception as e:
        logger.error(f"Error in add_price_alert: {e}")
        emit('error', {'message': 'Failed to create price alert'})

@socketio.on('remove_price_alert')
def handle_remove_price_alert(data):
    """Handle removing a price alert"""
    try:
        if not current_user.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        alert_id = int(data.get('alert_id', 0))
        
        if not alert_id:
            emit('error', {'message': 'Alert ID required'})
            return
        
        rt_service = get_real_time_service()
        if rt_service:
            success = rt_service.remove_price_alert(current_user.id, alert_id)
            
            if success:
                emit('alert_response', {
                    'alert_id': alert_id,
                    'status': 'removed',
                    'message': f'Price alert {alert_id} removed'
                })
            else:
                emit('error', {'message': 'Alert not found or access denied'})
        
    except Exception as e:
        logger.error(f"Error in remove_price_alert: {e}")
        emit('error', {'message': 'Failed to remove price alert'})

@socketio.on('get_price_history')
def handle_get_price_history(data):
    """Handle request for price history"""
    try:
        symbol = data.get('symbol', '').upper()
        minutes = int(data.get('minutes', 60))
        
        if not symbol:
            emit('error', {'message': 'Symbol is required'})
            return
        
        rt_service = get_real_time_service()
        if rt_service:
            history = rt_service.get_price_history(symbol, minutes)
            
            emit('price_history', {
                'symbol': symbol,
                'minutes': minutes,
                'data': history,
                'count': len(history)
            })
        
    except Exception as e:
        logger.error(f"Error in get_price_history: {e}")
        emit('error', {'message': 'Failed to get price history'})

@socketio.on('get_market_summary')
def handle_get_market_summary():
    """Handle request for market summary"""
    try:
        rt_service = get_real_time_service()
        if rt_service:
            summary = rt_service.get_market_summary()
            
            emit('market_summary', summary)
        
    except Exception as e:
        logger.error(f"Error in get_market_summary: {e}")
        emit('error', {'message': 'Failed to get market summary'})

@socketio.on('get_trending_stocks')
def handle_get_trending_stocks(data):
    """Handle request for trending stocks"""
    try:
        limit = int(data.get('limit', 10))
        
        rt_service = get_real_time_service()
        if rt_service:
            trending = rt_service.get_trending_stocks(limit)
            
            emit('trending_stocks', {
                'stocks': trending,
                'limit': limit,
                'count': len(trending)
            })
        
    except Exception as e:
        logger.error(f"Error in get_trending_stocks: {e}")
        emit('error', {'message': 'Failed to get trending stocks'})

@socketio.on('get_realtime_stats')
def handle_get_realtime_stats():
    """Handle request for real-time streaming statistics"""
    try:
        if not current_user.is_authenticated or not current_user.is_admin:
            emit('error', {'message': 'Admin access required'})
            return
        
        rt_service = get_real_time_service()
        if rt_service:
            stats = rt_service.get_realtime_stats()
            
            emit('realtime_stats', stats)
        
    except Exception as e:
        logger.error(f"Error in get_realtime_stats: {e}")
        emit('error', {'message': 'Failed to get statistics'})

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing"""
    emit('pong', {'timestamp': str(logger.info('now'))})

# Auto-start real-time service when this module is imported
def initialize_realtime_service():
    """Initialize the real-time service with SocketIO"""
    rt_service = get_real_time_service(socketio)
    if not rt_service.running:
        rt_service.start_background_updates()
        logger.info("Real-time service auto-started with WebSocket support")

# Initialize when module loads
initialize_realtime_service()
