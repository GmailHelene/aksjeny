"""
Real-time data service for live stock prices and market data with WebSocket streaming
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import yfinance as yf
from flask import current_app
import threading
import time
from ..extensions import db
from dataclasses import dataclass, asdict
import numpy as np
from collections import defaultdict, deque
import queue

# Import rate limiter
try:
    from .rate_limiter import rate_limiter
except ImportError:
    # Fallback if rate limiter is not available
    class DummyRateLimiter:
        def wait_if_needed(self, api_name='default'):
            time.sleep(2.0)  # Simple fallback delay
    rate_limiter = DummyRateLimiter()

logger = logging.getLogger(__name__)

@dataclass
class MarketDataPoint:
    """Real-time market data point"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class PriceAlert:
    """Price alert notification"""
    alert_id: int
    user_id: int
    symbol: str
    trigger_price: float
    current_price: float
    alert_type: str  # 'above', 'below', 'change_percent'
    message: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RealTimeDataService:
    """Service for managing real-time stock data updates with WebSocket streaming"""
    
    def __init__(self, socketio=None):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 300  # 5 minutes cache
        self.update_interval = 60  # Update every minute
        self.running = False
        self.thread = None
        
        # WebSocket functionality
        self.socketio = socketio
        self.user_subscriptions: Dict[str, Set[str]] = defaultdict(set)  # session_id -> symbols
        self.price_alerts: Dict[int, List[PriceAlert]] = defaultdict(list)  # user_id -> alerts
        self.price_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1440))  # 24h history
        
        # Data queues for WebSocket streaming
        self.market_data_queue = queue.Queue(maxsize=1000)
        self.alert_queue = queue.Queue(maxsize=200)
        
        # Performance tracking
        self.stats = {
            'messages_sent': 0,
            'data_points_processed': 0,
            'active_connections': 0,
            'alerts_triggered': 0,
            'start_time': datetime.now()
        }
        
    def start_background_updates(self):
        """Start background thread for continuous data updates"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._background_update_loop, daemon=True)
            self.thread.start()
            
            # Start WebSocket streaming if available
            if self.socketio:
                self._start_websocket_threads()
            
            logger.info("Real-time data service started with WebSocket streaming")
    
    def _start_websocket_threads(self):
        """Start WebSocket-specific background threads"""
        # Start alert processing thread
        alert_thread = threading.Thread(target=self._alert_processor, daemon=True)
        alert_thread.start()
        
        # Start data broadcaster thread
        broadcast_thread = threading.Thread(target=self._data_broadcaster, daemon=True)
        broadcast_thread.start()
        
        logger.info("WebSocket streaming threads started")
    
    def subscribe_to_symbol(self, session_id: str, symbol: str):
        """Subscribe a user session to real-time data for a symbol"""
        self.user_subscriptions[session_id].add(symbol.upper())
        
        if self.socketio:
            # Join socket room for this symbol
            self.socketio.emit('subscription_confirmed', 
                             {'symbol': symbol, 'status': 'subscribed'}, 
                             room=session_id)
        
        logger.debug(f"Session {session_id} subscribed to {symbol}")
    
    def unsubscribe_from_symbol(self, session_id: str, symbol: str):
        """Unsubscribe a user session from a symbol"""
        self.user_subscriptions[session_id].discard(symbol.upper())
        logger.debug(f"Session {session_id} unsubscribed from {symbol}")
    
    def add_price_alert(self, user_id: int, symbol: str, trigger_price: float, 
                       alert_type: str = 'above') -> int:
        """Add a price alert for a user"""
        alert_id = int(time.time() * 1000)  # Unique ID based on timestamp
        
        alert = PriceAlert(
            alert_id=alert_id,
            user_id=user_id,
            symbol=symbol.upper(),
            trigger_price=trigger_price,
            current_price=0.0,  # Will be updated
            alert_type=alert_type,
            message=f"Price alert for {symbol} at {trigger_price}",
            timestamp=datetime.now()
        )
        
        self.price_alerts[user_id].append(alert)
        
        logger.info(f"Added price alert {alert_id} for user {user_id}: {symbol} {alert_type} {trigger_price}")
        return alert_id
    
    def remove_price_alert(self, user_id: int, alert_id: int) -> bool:
        """Remove a price alert"""
        alerts = self.price_alerts[user_id]
        for i, alert in enumerate(alerts):
            if alert.alert_id == alert_id:
                del alerts[i]
                logger.info(f"Removed price alert {alert_id} for user {user_id}")
                return True
        return False
    
    def get_price_history(self, symbol: str, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get price history for a symbol"""
        history = list(self.price_history.get(symbol.upper(), []))
        return history[-minutes:] if history else []
    
    def stop_background_updates(self):
        """Stop background updates"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Real-time data service stopped")
    
    def _background_update_loop(self):
        """Background loop for updating data"""
        while self.running:
            try:
                self._update_all_data()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in background update loop: {e}")
                time.sleep(30)  # Wait 30 seconds on error
    
    def _update_all_data(self):
        """Update all tracked stocks and market data"""
        try:
            # Update Oslo Børs
            oslo_tickers = [
                'EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL', 
                'MOWI.OL', 'NEL.OL', 'REC.OL', 'ORK.OL', 'SSO.OL'
            ]
            self._update_ticker_batch(oslo_tickers, 'oslo')
            
            # Update Global stocks
            global_tickers = [
                'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 
                'NVDA', 'META', 'NFLX', 'ADBE', 'CRM'
            ]
            self._update_ticker_batch(global_tickers, 'global')
            
            # Update Crypto
            crypto_tickers = [
                'BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'SOL-USD'
            ]
            self._update_ticker_batch(crypto_tickers, 'crypto')
            
            logger.info(f"Updated real-time data at {datetime.now()}")
            
        except Exception as e:
            logger.error(f"Error updating all data: {e}")
    
    def _update_ticker_batch(self, tickers: List[str], category: str):
        """Update a batch of tickers efficiently with rate limiting"""
        try:
            # Use rate limiter instead of simple sleep
            rate_limiter.wait_if_needed('yahoo_finance')
            
            # Process tickers in smaller batches to avoid overwhelming Yahoo
            batch_size = 3  # Reduced from 5 to 3 for gentler API usage
            for i in range(0, len(tickers), batch_size):
                batch = tickers[i:i + batch_size]
                
                try:
                    # Use yfinance to get multiple tickers at once
                    ticker_string = ' '.join(batch)
                    data = yf.download(ticker_string, period='1d', interval='1m', 
                                     group_by='ticker', auto_adjust=True, 
                                     prepost=True, threads=False, progress=False)  # Disable threading to be gentler
                    
                    if data.empty:
                        logger.warning(f"No data received for batch: {batch}")
                        continue
                    
                    current_time = datetime.now()
                    
                    for ticker in batch:
                        try:
                            if len(batch) == 1:
                                ticker_data = data
                            else:
                                ticker_data = data[ticker] if ticker in data.columns.levels[0] else None
                        
                            if ticker_data is None or ticker_data.empty:
                                continue
                            
                            # Get latest values
                            latest = ticker_data.iloc[-1]
                            previous = ticker_data.iloc[-2] if len(ticker_data) > 1 else latest
                            
                            # Calculate changes
                            current_price = float(latest['Close'])
                            previous_price = float(previous['Close'])
                            change = current_price - previous_price
                            change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
                            volume = int(latest['Volume']) if 'Volume' in latest else 0
                            
                            # Store in cache
                            cache_key = f"{category}_{ticker}"
                            self.cache[cache_key] = {
                                'ticker': ticker,
                                'current_price': current_price,
                                'change': change,
                                'change_percent': change_percent,
                                'volume': volume,
                                'last_updated': current_time,
                                'category': category
                            }
                            self.cache_timestamps[cache_key] = current_time
                            
                            # Create market data point for WebSocket streaming
                            if self.socketio:
                                market_data_point = MarketDataPoint(
                                    symbol=ticker.replace('.OL', ''),  # Clean symbol for display
                                    price=current_price,
                                    change=change,
                                    change_percent=change_percent,
                                    volume=volume,
                                    timestamp=current_time,
                                    high=float(latest['High']) if 'High' in latest else current_price,
                                    low=float(latest['Low']) if 'Low' in latest else current_price
                                )
                                
                                # Queue for WebSocket broadcasting
                                if not self.market_data_queue.full():
                                    self.market_data_queue.put(market_data_point)
                                
                                # Store in price history
                                clean_symbol = ticker.replace('.OL', '')
                                self.price_history[clean_symbol].append({
                                    'timestamp': current_time.isoformat(),
                                    'price': current_price,
                                    'volume': volume
                                })
                            
                            self.stats['data_points_processed'] += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing ticker {ticker}: {e}")
                            continue
                    
                    # Add delay between small batches
                    if i + batch_size < len(tickers):
                        time.sleep(3)  # Increased pause between batches from 1 to 3 seconds
                        
                except Exception as e:
                    logger.error(f"Error processing batch {batch}: {e}")
                    time.sleep(10)  # Much longer delay on error (increased from 3 to 10 seconds)
                    
        except Exception as e:
            logger.error(f"Error updating ticker batch {category}: {e}")
    
    def get_live_price(self, ticker: str, category: str = 'oslo') -> Optional[Dict[str, Any]]:
        """Get live price for a specific ticker"""
        cache_key = f"{category}_{ticker}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_time = self.cache_timestamps.get(cache_key)
            if cached_time and (datetime.now() - cached_time).seconds < self.cache_duration:
                return self.cache[cache_key]
        
        # Fetch fresh data if not cached or expired
        try:
            if not ticker.endswith('.OL') and category == 'oslo':
                ticker = f"{ticker}.OL"
            
            stock = yf.Ticker(ticker)
            info = stock.history(period='2d', interval='1m')
            
            if info.empty:
                return None
            
            latest = info.iloc[-1]
            previous = info.iloc[-2] if len(info) > 1 else latest
            
            current_price = float(latest['Close'])
            previous_price = float(previous['Close'])
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
            volume = int(latest['Volume']) if 'Volume' in latest else 0
            
            result = {
                'ticker': ticker,
                'current_price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': volume,
                'last_updated': datetime.now(),
                'category': category
            }
            
            # Cache the result
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching live price for {ticker}: {e}")
            return None
    
    def get_market_summary(self) -> Dict[str, Any]:
        """Get real-time market summary"""
        try:
            summary = {
                'oslo_bors': self._get_category_summary('oslo'),
                'global': self._get_category_summary('global'),
                'crypto': self._get_category_summary('crypto'),
                'last_updated': datetime.now()
            }
            return summary
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {}
    
    def _get_category_summary(self, category: str) -> Dict[str, Any]:
        """Get summary for a specific category"""
        try:
            category_data = {k: v for k, v in self.cache.items() if k.startswith(f"{category}_")}
            
            if not category_data:
                return {'status': 'no_data'}
            
            prices = [data['current_price'] for data in category_data.values()]
            changes = [data['change_percent'] for data in category_data.values()]
            
            return {
                'total_stocks': len(category_data),
                'avg_change': sum(changes) / len(changes) if changes else 0,
                'positive_count': len([c for c in changes if c > 0]),
                'negative_count': len([c for c in changes if c < 0]),
                'neutral_count': len([c for c in changes if c == 0]),
                'last_updated': max([data['last_updated'] for data in category_data.values()]),
                'status': 'active'
            }
        except Exception as e:
            logger.error(f"Error fetching category summary for {category}: {e}")
            return {'error': f"Failed to fetch data for {category}"}
    
    def get_trending_stocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending stocks based on volume and price movements"""
        try:
            all_stocks = list(self.cache.values())
            
            # Sort by combination of volume and absolute change percent
            trending = sorted(all_stocks, 
                            key=lambda x: (x['volume'] * abs(x['change_percent'])), 
                            reverse=True)
            
            return trending[:limit]
        except Exception as e:
            logger.error(f"Error getting trending stocks: {e}")
            return []
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("Cache cleared")
    
    def _alert_processor(self):
        """Process price alerts and trigger notifications"""
        while self.running:
            try:
                for user_id, alerts in list(self.price_alerts.items()):
                    for alert in alerts[:]:  # Copy list to avoid modification issues
                        # Find symbol data in cache
                        symbol_data = None
                        for cache_key, data in self.cache.items():
                            if data['ticker'].replace('.OL', '').upper() == alert.symbol:
                                symbol_data = data
                                break
                        
                        if symbol_data:
                            alert.current_price = symbol_data['current_price']
                            triggered = False
                            
                            if alert.alert_type == 'above' and symbol_data['current_price'] >= alert.trigger_price:
                                triggered = True
                            elif alert.alert_type == 'below' and symbol_data['current_price'] <= alert.trigger_price:
                                triggered = True
                            elif alert.alert_type == 'change_percent':
                                if abs(symbol_data['change_percent']) >= alert.trigger_price:
                                    triggered = True
                            
                            if triggered:
                                alert.message = f"🔔 {alert.symbol} alert triggered! Price: {symbol_data['current_price']:.2f}"
                                
                                if not self.alert_queue.full():
                                    self.alert_queue.put(alert)
                                
                                # Remove triggered alert
                                self.price_alerts[user_id].remove(alert)
                                self.stats['alerts_triggered'] += 1
                                
                                logger.info(f"Price alert triggered: {alert.message}")
                
                time.sleep(5)  # Check alerts every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in alert processing: {e}")
                time.sleep(10)
    
    def _data_broadcaster(self):
        """Broadcast real-time data to connected WebSocket clients"""
        while self.running and self.socketio:
            try:
                # Broadcast market data updates
                while not self.market_data_queue.empty():
                    try:
                        data_point = self.market_data_queue.get_nowait()
                        
                        # Send to all sessions subscribed to this symbol
                        for session_id, symbols in self.user_subscriptions.items():
                            if data_point.symbol in symbols:
                                self.socketio.emit('market_data_update', 
                                                 data_point.to_dict(),
                                                 room=session_id)
                        
                        self.stats['messages_sent'] += 1
                        
                    except queue.Empty:
                        break
                
                # Broadcast price alerts
                while not self.alert_queue.empty():
                    try:
                        alert = self.alert_queue.get_nowait()
                        
                        # Send alert to specific user (need to find their session)
                        # In a real app, you'd maintain user_id -> session_id mapping
                        self.socketio.emit('price_alert',
                                         alert.to_dict(),
                                         broadcast=True)  # Broadcast to all for simplicity
                        
                        self.stats['messages_sent'] += 1
                        
                    except queue.Empty:
                        break
                
                time.sleep(0.5)  # Small delay to prevent overwhelming
                
            except Exception as e:
                logger.error(f"Error in data broadcasting: {e}")
                time.sleep(2)
    
    def handle_client_connect(self, session_id: str):
        """Handle new WebSocket client connection"""
        self.stats['active_connections'] += 1
        
        if self.socketio:
            # Send initial market summary
            market_summary = self.get_market_summary()
            self.socketio.emit('market_summary', market_summary, room=session_id)
        
        logger.info(f"WebSocket client connected: {session_id}")
    
    def handle_client_disconnect(self, session_id: str):
        """Handle WebSocket client disconnection"""
        # Clean up subscriptions
        if session_id in self.user_subscriptions:
            del self.user_subscriptions[session_id]
        
        self.stats['active_connections'] = max(0, self.stats['active_connections'] - 1)
        logger.info(f"WebSocket client disconnected: {session_id}")
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time streaming statistics"""
        uptime = datetime.now() - self.stats['start_time']
        
        return {
            'uptime_seconds': int(uptime.total_seconds()),
            'messages_sent': self.stats['messages_sent'],
            'data_points_processed': self.stats['data_points_processed'],
            'active_connections': self.stats['active_connections'],
            'alerts_triggered': self.stats['alerts_triggered'],
            'subscribed_symbols': sum(len(symbols) for symbols in self.user_subscriptions.values()),
            'total_alerts': sum(len(alerts) for alerts in self.price_alerts.values()),
            'cache_size': len(self.cache)
        }

# Global instance
real_time_service = None

def get_real_time_service(socketio=None):
    """Get or create the global real-time service instance"""
    global real_time_service
    
    if real_time_service is None:
        real_time_service = RealTimeDataService(socketio)
        logger.info("Global real-time service created")
    elif socketio and not real_time_service.socketio:
        real_time_service.socketio = socketio
        logger.info("SocketIO added to existing real-time service")
    
    return real_time_service
