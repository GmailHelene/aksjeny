"""
Real-time WebSocket Handler
==========================

WebSocket endpoints for streaming real-time market data,
live quotes, and trading updates to connected clients.
"""

from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_login import login_required, current_user
from ..services.market_data_service import get_market_data_service
from ..decorators import access_required
import json
import logging
from datetime import datetime
from typing import Dict, Set

logger = logging.getLogger(__name__)

# WebSocket namespace for market data
MARKET_DATA_NAMESPACE = '/market-data'

# Track connected clients and their subscriptions
connected_clients: Dict[str, Set[str]] = {}  # session_id -> set of symbols
symbol_subscribers: Dict[str, Set[str]] = {}  # symbol -> set of session_ids

class MarketDataWebSocket:
    """WebSocket handler for real-time market data"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.market_service = get_market_data_service()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect', namespace=MARKET_DATA_NAMESPACE)
        @login_required
        def handle_connect():
            """Handle client connection"""
            session_id = request.sid
            connected_clients[session_id] = set()
            
            logger.info(f"Market data client connected: {session_id}")
            
            # Send initial market status
            market_status = self.market_service.get_market_status()
            emit('market_status', market_status)
            
            # Send market indices
            indices = self.market_service.get_market_indices()
            indices_data = {symbol: index.to_dict() for symbol, index in indices.items()}
            emit('market_indices', indices_data)
        
        @self.socketio.on('disconnect', namespace=MARKET_DATA_NAMESPACE)
        def handle_disconnect():
            """Handle client disconnection"""
            session_id = request.sid
            
            if session_id in connected_clients:
                # Unsubscribe from all symbols
                subscribed_symbols = connected_clients[session_id]
                for symbol in subscribed_symbols:
                    self._unsubscribe_symbol(session_id, symbol)
                
                del connected_clients[session_id]
            
            logger.info(f"Market data client disconnected: {session_id}")
        
        @self.socketio.on('subscribe_quote', namespace=MARKET_DATA_NAMESPACE)
        @login_required
        def handle_subscribe_quote(data):
            """Subscribe to real-time quotes for symbols"""
            session_id = request.sid
            symbols = data.get('symbols', [])
            
            if not isinstance(symbols, list):
                symbols = [symbols]
            
            for symbol in symbols:
                symbol = symbol.upper()
                self._subscribe_symbol(session_id, symbol)
                
                # Send current quote immediately
                quote = self.market_service.get_quote(symbol)
                if quote:
                    emit('quote_update', {
                        'symbol': symbol,
                        'data': quote.to_dict()
                    })
            
            logger.info(f"Client {session_id} subscribed to quotes: {symbols}")
        
        @self.socketio.on('unsubscribe_quote', namespace=MARKET_DATA_NAMESPACE)
        @login_required
        def handle_unsubscribe_quote(data):
            """Unsubscribe from real-time quotes"""
            session_id = request.sid
            symbols = data.get('symbols', [])
            
            if not isinstance(symbols, list):
                symbols = [symbols]
            
            for symbol in symbols:
                symbol = symbol.upper()
                self._unsubscribe_symbol(session_id, symbol)
            
            logger.info(f"Client {session_id} unsubscribed from quotes: {symbols}")
        
        @self.socketio.on('get_historical_data', namespace=MARKET_DATA_NAMESPACE)
        @login_required
        def handle_get_historical_data(data):
            """Get historical price data"""
            symbol = data.get('symbol', '').upper()
            period = data.get('period', '1y')
            
            if not symbol:
                emit('error', {'message': 'Symbol is required'})
                return
            
            try:
                historical_data = self.market_service.get_historical_data(symbol, period)
                emit('historical_data', {
                    'symbol': symbol,
                    'period': period,
                    'data': historical_data
                })
            except Exception as e:
                logger.error(f"Error getting historical data: {e}")
                emit('error', {'message': f'Error getting historical data: {str(e)}'})
        
        @self.socketio.on('get_top_movers', namespace=MARKET_DATA_NAMESPACE)
        @login_required
        def handle_get_top_movers(data):
            """Get top market movers"""
            limit = data.get('limit', 10)
            
            try:
                movers = self.market_service.get_top_movers(limit)
                movers_data = {
                    'gainers': [quote.to_dict() for quote in movers['gainers']],
                    'losers': [quote.to_dict() for quote in movers['losers']]
                }
                emit('top_movers', movers_data)
            except Exception as e:
                logger.error(f"Error getting top movers: {e}")
                emit('error', {'message': f'Error getting top movers: {str(e)}'})
        
        @self.socketio.on('get_sector_performance', namespace=MARKET_DATA_NAMESPACE)
        @login_required
        def handle_get_sector_performance():
            """Get sector performance data"""
            try:
                sector_data = self.market_service.get_sector_performance()
                emit('sector_performance', sector_data)
            except Exception as e:
                logger.error(f"Error getting sector performance: {e}")
                emit('error', {'message': f'Error getting sector performance: {str(e)}'})
    
    def _subscribe_symbol(self, session_id: str, symbol: str):
        """Subscribe a session to a symbol"""
        if session_id not in connected_clients:
            connected_clients[session_id] = set()
        
        connected_clients[session_id].add(symbol)
        
        if symbol not in symbol_subscribers:
            symbol_subscribers[symbol] = set()
        
        symbol_subscribers[symbol].add(session_id)
    
    def _unsubscribe_symbol(self, session_id: str, symbol: str):
        """Unsubscribe a session from a symbol"""
        if session_id in connected_clients:
            connected_clients[session_id].discard(symbol)
        
        if symbol in symbol_subscribers:
            symbol_subscribers[symbol].discard(session_id)
            
            # Clean up empty symbol subscriptions
            if not symbol_subscribers[symbol]:
                del symbol_subscribers[symbol]
    
    def broadcast_quote_update(self, symbol: str, quote_data: dict):
        """Broadcast quote update to all subscribers"""
        if symbol in symbol_subscribers:
            for session_id in symbol_subscribers[symbol]:
                self.socketio.emit('quote_update', {
                    'symbol': symbol,
                    'data': quote_data
                }, room=session_id, namespace=MARKET_DATA_NAMESPACE)
    
    def broadcast_market_indices(self, indices_data: dict):
        """Broadcast market indices update to all connected clients"""
        self.socketio.emit('market_indices', indices_data, namespace=MARKET_DATA_NAMESPACE)
    
    def broadcast_market_status(self, status_data: dict):
        """Broadcast market status update"""
        self.socketio.emit('market_status', status_data, namespace=MARKET_DATA_NAMESPACE)
    
    def get_subscriber_count(self, symbol: str) -> int:
        """Get number of subscribers for a symbol"""
        return len(symbol_subscribers.get(symbol, set()))
    
    def get_active_symbols(self) -> Set[str]:
        """Get all actively subscribed symbols"""
        return set(symbol_subscribers.keys())

# WebSocket instance will be initialized with SocketIO
market_websocket: MarketDataWebSocket = None

def init_market_websocket(socketio: SocketIO):
    """Initialize market data WebSocket handler"""
    global market_websocket
    market_websocket = MarketDataWebSocket(socketio)
    return market_websocket

def get_market_websocket() -> MarketDataWebSocket:
    """Get the market data WebSocket handler"""
    return market_websocket

# Real-time market data API routes
realtime_data = Blueprint('realtime_data', __name__, url_prefix='/api/realtime')

@realtime_data.route('/quote/<symbol>')
@access_required
def get_quote(symbol):
    """Get real-time quote for a symbol"""
    try:
        market_service = get_market_data_service()
        quote = market_service.get_quote(symbol.upper())
        
        if quote:
            return jsonify({
                'success': True,
                'data': quote.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Quote not found for {symbol}'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@realtime_data.route('/quotes')
@access_required
def get_multiple_quotes():
    """Get quotes for multiple symbols"""
    symbols = request.args.getlist('symbols')
    
    if not symbols:
        return jsonify({
            'success': False,
            'message': 'No symbols provided'
        }), 400
    
    try:
        market_service = get_market_data_service()
        quotes = market_service.get_multiple_quotes(symbols)
        
        quotes_data = {symbol: quote.to_dict() for symbol, quote in quotes.items()}
        
        return jsonify({
            'success': True,
            'data': quotes_data
        })
        
    except Exception as e:
        logger.error(f"Error getting multiple quotes: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@realtime_data.route('/market-indices')
@access_required
def get_market_indices():
    """Get current market indices"""
    try:
        market_service = get_market_data_service()
        indices = market_service.get_market_indices()
        
        indices_data = {symbol: index.to_dict() for symbol, index in indices.items()}
        
        return jsonify({
            'success': True,
            'data': indices_data
        })
        
    except Exception as e:
        logger.error(f"Error getting market indices: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@realtime_data.route('/market-status')
@access_required
def get_market_status():
    """Get current market status"""
    try:
        market_service = get_market_data_service()
        status = market_service.get_market_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@realtime_data.route('/top-movers')
@access_required
def get_top_movers():
    """Get top market movers"""
    limit = request.args.get('limit', 10, type=int)
    
    try:
        market_service = get_market_data_service()
        movers = market_service.get_top_movers(limit)
        
        movers_data = {
            'gainers': [quote.to_dict() for quote in movers['gainers']],
            'losers': [quote.to_dict() for quote in movers['losers']]
        }
        
        return jsonify({
            'success': True,
            'data': movers_data
        })
        
    except Exception as e:
        logger.error(f"Error getting top movers: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@realtime_data.route('/sector-performance')
@access_required
def get_sector_performance():
    """Get sector performance data"""
    try:
        market_service = get_market_data_service()
        sector_data = market_service.get_sector_performance()
        
        return jsonify({
            'success': True,
            'data': sector_data
        })
        
    except Exception as e:
        logger.error(f"Error getting sector performance: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@realtime_data.route('/historical/<symbol>')
@access_required
def get_historical_data(symbol):
    """Get historical price data"""
    period = request.args.get('period', '1y')
    
    try:
        market_service = get_market_data_service()
        historical_data = market_service.get_historical_data(symbol.upper(), period)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol.upper(),
                'period': period,
                'data': historical_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting historical data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@realtime_data.route('/stats')
@access_required
def get_realtime_stats():
    """Get real-time service statistics"""
    try:
        websocket = get_market_websocket()
        if not websocket:
            return jsonify({
                'success': False,
                'message': 'WebSocket service not available'
            }), 503
        
        active_symbols = websocket.get_active_symbols()
        subscriber_counts = {symbol: websocket.get_subscriber_count(symbol) 
                           for symbol in active_symbols}
        
        return jsonify({
            'success': True,
            'data': {
                'connected_clients': len(connected_clients),
                'active_symbols': len(active_symbols),
                'symbols': list(active_symbols),
                'subscriber_counts': subscriber_counts,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting realtime stats: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
