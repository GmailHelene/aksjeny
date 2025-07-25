"""
Real-time Market Data Service
============================

Comprehensive market data integration with WebSocket support,
real-time quotes, market indices, and live trading data.
"""

import asyncio
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    websockets = None
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from flask import current_app
from ..models import db
import logging
import requests
from collections import defaultdict
import yfinance as yf

logger = logging.getLogger(__name__)

@dataclass
class Quote:
    """Real-time stock quote data structure"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    previous_close: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return data

@dataclass
class MarketIndex:
    """Market index data structure"""
    name: str
    symbol: str
    value: float
    change: float
    change_percent: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return data

@dataclass
class TradingVolume:
    """Trading volume data"""
    symbol: str
    volume: int
    avg_volume: int
    volume_ratio: float
    timestamp: datetime = None
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat() if self.timestamp else None
        return data

class MarketDataService:
    """Real-time market data service with WebSocket support"""
    
    def __init__(self):
        self.quotes_cache = {}
        self.indices_cache = {}
        self.subscribers = defaultdict(list)  # WebSocket subscribers
        self.running = False
        self.update_thread = None
        self.websocket_server = None
        
        # Market indices to track
        self.indices = {
            '^GSPC': 'S&P 500',
            '^IXIC': 'NASDAQ',
            '^DJI': 'Dow Jones',
            '^VIX': 'VIX',
            '^TNX': '10-Year Treasury'
        }
        
        # Popular stocks to track
        self.default_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
            'META', 'NVDA', 'NFLX', 'UBER', 'SPOT'
        ]
        
        self.data_sources = {
            'yahoo': self._fetch_yahoo_data,
            'alpha_vantage': self._fetch_alpha_vantage_data,
            'polygon': self._fetch_polygon_data
        }
        
    def start(self):
        """Start the real-time market data service"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting real-time market data service")
        
        # Start background update thread
        self.update_thread = threading.Thread(target=self._background_update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Initialize with default data
        self._initial_data_load()
        
        logger.info("Market data service started successfully")
    
    def stop(self):
        """Stop the market data service"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        logger.info("Market data service stopped")
    
    def _initial_data_load(self):
        """Load initial market data"""
        try:
            # Load market indices
            self._update_market_indices()
            
            # Load default stock quotes
            self._update_stock_quotes(self.default_symbols)
            
            logger.info(f"Initial data loaded: {len(self.quotes_cache)} quotes, {len(self.indices_cache)} indices")
        except Exception as e:
            logger.error(f"Error in initial data load: {e}")
    
    def _background_update_loop(self):
        """Background loop for updating market data"""
        update_interval = 30  # seconds
        last_update = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                if current_time - last_update >= update_interval:
                    if self._is_market_hours():
                        # Update during market hours
                        self._update_market_indices()
                        
                        # Update quotes for subscribed symbols
                        symbols_to_update = list(self.quotes_cache.keys())
                        if symbols_to_update:
                            self._update_stock_quotes(symbols_to_update)
                        
                        # Notify WebSocket subscribers
                        self._notify_subscribers()
                    
                    last_update = current_time
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in background update loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def _is_market_hours(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now()
        
        # Simple check for US market hours (9:30 AM - 4:00 PM ET, Mon-Fri)
        if now.weekday() >= 5:  # Weekend
            return False
        
        # For demo purposes, consider market always open
        # In production, implement proper market hours logic
        return True
    
    def get_quote(self, symbol: str, force_refresh: bool = False) -> Optional[Quote]:
        """Get real-time quote for a symbol"""
        symbol = symbol.upper()
        
        # Check cache first
        if not force_refresh and symbol in self.quotes_cache:
            quote = self.quotes_cache[symbol]
            # Return cached data if less than 1 minute old
            if (datetime.utcnow() - quote.timestamp).seconds < 60:
                return quote
        
        # Fetch fresh data
        try:
            quote_data = self._fetch_quote_data(symbol)
            if quote_data:
                self.quotes_cache[symbol] = quote_data
                return quote_data
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
        
        return self.quotes_cache.get(symbol)
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        """Get quotes for multiple symbols"""
        results = {}
        
        # Group symbols for batch requests
        symbols_to_fetch = [s.upper() for s in symbols]
        quotes_data = self._update_stock_quotes(symbols_to_fetch)
        
        for symbol in symbols_to_fetch:
            if symbol in self.quotes_cache:
                results[symbol] = self.quotes_cache[symbol]
        
        return results
    
    def get_market_indices(self) -> Dict[str, MarketIndex]:
        """Get current market indices"""
        if not self.indices_cache:
            self._update_market_indices()
        
        return self.indices_cache.copy()
    
    def get_top_movers(self, limit: int = 10) -> Dict[str, List[Quote]]:
        """Get top gainers and losers"""
        try:
            # Fetch data for S&P 500 stocks (simplified)
            sp500_symbols = [
                'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V',
                'PG', 'UNH', 'HD', 'MA', 'PYPL', 'DIS', 'ADBE', 'NFLX', 'CRM', 'CMCSA',
                'VZ', 'KO', 'NKE', 'MRK', 'PEP', 'T', 'ABT', 'AVGO', 'TMO', 'COST'
            ]
            
            quotes = self.get_multiple_quotes(sp500_symbols)
            
            # Sort by change percentage
            sorted_quotes = sorted(quotes.values(), key=lambda q: q.change_percent, reverse=True)
            
            return {
                'gainers': sorted_quotes[:limit],
                'losers': sorted_quotes[-limit:][::-1]  # Reverse to show biggest losers first
            }
            
        except Exception as e:
            logger.error(f"Error getting top movers: {e}")
            return {'gainers': [], 'losers': []}
    
    def get_sector_performance(self) -> Dict[str, float]:
        """Get sector performance data"""
        try:
            # Sector ETFs as proxies
            sector_etfs = {
                'Technology': 'XLK',
                'Healthcare': 'XLV', 
                'Financials': 'XLF',
                'Energy': 'XLE',
                'Consumer Discretionary': 'XLY',
                'Industrials': 'XLI',
                'Communication Services': 'XLC',
                'Consumer Staples': 'XLP',
                'Real Estate': 'XLRE',
                'Materials': 'XLB',
                'Utilities': 'XLU'
            }
            
            sector_quotes = self.get_multiple_quotes(list(sector_etfs.values()))
            
            performance = {}
            for sector, etf_symbol in sector_etfs.items():
                if etf_symbol in sector_quotes:
                    performance[sector] = sector_quotes[etf_symbol].change_percent
                else:
                    performance[sector] = 0.0
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting sector performance: {e}")
            return {}
    
    def _fetch_quote_data(self, symbol: str) -> Optional[Quote]:
        """Fetch quote data for a single symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='2d')
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
            
            return Quote(
                symbol=symbol,
                price=float(current_price),
                change=float(change),
                change_percent=float(change_percent),
                volume=int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                high=float(hist['High'].iloc[-1]),
                low=float(hist['Low'].iloc[-1]),
                open=float(hist['Open'].iloc[-1]),
                previous_close=float(previous_close),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE')
            )
            
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def _update_stock_quotes(self, symbols: List[str]) -> bool:
        """Update quotes for multiple symbols"""
        try:
            for symbol in symbols:
                quote = self._fetch_quote_data(symbol)
                if quote:
                    self.quotes_cache[symbol] = quote
            
            logger.debug(f"Updated quotes for {len(symbols)} symbols")
            return True
            
        except Exception as e:
            logger.error(f"Error updating stock quotes: {e}")
            return False
    
    def _update_market_indices(self) -> bool:
        """Update market indices data"""
        try:
            for symbol, name in self.indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2d')
                    
                    if not hist.empty:
                        current_value = hist['Close'].iloc[-1]
                        previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_value
                        
                        change = current_value - previous_close
                        change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                        
                        self.indices_cache[symbol] = MarketIndex(
                            name=name,
                            symbol=symbol,
                            value=float(current_value),
                            change=float(change),
                            change_percent=float(change_percent)
                        )
                        
                except Exception as e:
                    logger.error(f"Error updating index {symbol}: {e}")
                    continue
            
            logger.debug(f"Updated {len(self.indices_cache)} market indices")
            return True
            
        except Exception as e:
            logger.error(f"Error updating market indices: {e}")
            return False
    
    def _fetch_yahoo_data(self, symbols: List[str]) -> Dict[str, dict]:
        """Fetch data from Yahoo Finance"""
        # Implementation for Yahoo Finance API
        return {}
    
    def _fetch_alpha_vantage_data(self, symbols: List[str]) -> Dict[str, dict]:
        """Fetch data from Alpha Vantage API"""
        # Implementation for Alpha Vantage API
        return {}
    
    def _fetch_polygon_data(self, symbols: List[str]) -> Dict[str, dict]:
        """Fetch data from Polygon API"""
        # Implementation for Polygon API
        return {}
    
    def subscribe_to_symbol(self, symbol: str, callback: Callable):
        """Subscribe to real-time updates for a symbol"""
        symbol = symbol.upper()
        self.subscribers[symbol].append(callback)
        
        # Ensure we have the quote in cache
        if symbol not in self.quotes_cache:
            self.get_quote(symbol)
    
    def unsubscribe_from_symbol(self, symbol: str, callback: Callable):
        """Unsubscribe from symbol updates"""
        symbol = symbol.upper()
        if symbol in self.subscribers and callback in self.subscribers[symbol]:
            self.subscribers[symbol].remove(callback)
    
    def _notify_subscribers(self):
        """Notify all subscribers of data updates"""
        for symbol, callbacks in self.subscribers.items():
            if symbol in self.quotes_cache:
                quote = self.quotes_cache[symbol]
                for callback in callbacks:
                    try:
                        callback(quote)
                    except Exception as e:
                        logger.error(f"Error notifying subscriber for {symbol}: {e}")
    
    def get_historical_data(self, symbol: str, period: str = '1y') -> List[Dict]:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    'date': date.isoformat(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return []
    
    def get_market_status(self) -> Dict[str, any]:
        """Get current market status"""
        is_open = self._is_market_hours()
        
        # Calculate next market open/close
        now = datetime.now()
        if is_open:
            # Market is open, calculate next close (4:00 PM ET)
            next_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            if next_close <= now:
                next_close += timedelta(days=1)
            next_event = next_close
            next_event_type = 'close'
        else:
            # Market is closed, calculate next open (9:30 AM ET next trading day)
            next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            if next_open <= now or now.weekday() >= 5:
                # Move to next trading day
                days_ahead = 1
                if now.weekday() == 4:  # Friday
                    days_ahead = 3  # Skip to Monday
                elif now.weekday() == 5:  # Saturday
                    days_ahead = 2  # Skip to Monday
                
                next_open += timedelta(days=days_ahead)
            
            next_event = next_open
            next_event_type = 'open'
        
        return {
            'is_open': is_open,
            'next_event': next_event.isoformat(),
            'next_event_type': next_event_type,
            'timezone': 'US/Eastern'
        }

# Global market data service instance
market_data_service = MarketDataService()

def init_market_data_service(app):
    """Initialize market data service with Flask app"""
    with app.app_context():
        market_data_service.start()

def get_market_data_service() -> MarketDataService:
    """Get the global market data service instance"""
    return market_data_service
