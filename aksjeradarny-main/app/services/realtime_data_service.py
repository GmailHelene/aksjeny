"""
Real-time data service for live stock prices and market data
"""
import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf
from flask import current_app
import threading
import time
from app.extensions import db

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

class RealTimeDataService:
    """Service for managing real-time stock data updates"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 300  # 5 minutes cache
        self.update_interval = 60  # Update every minute
        self.running = False
        self.thread = None
        
    def start_background_updates(self):
        """Start background thread for continuous data updates"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._background_update_loop, daemon=True)
            self.thread.start()
            logger.info("Real-time data service started")
    
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

# Global instance
real_time_service = RealTimeDataService()
