"""
Portfolio Service - AI-powered portfolio analysis and optimization
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StockAnalysis:
    """Data class for stock analysis results"""
    symbol: str
    current_price: float
    ai_score: float
    signals: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    week_change: float
    technical_indicators: Dict[str, float]
    recommendation: str

class PortfolioService:
    """Service for portfolio analysis and optimization"""
    
    @staticmethod
    def calculate_ai_score(symbol: str, data: pd.DataFrame) -> float:
        """Calculate AI score based on multiple factors"""
        try:
            if data.empty:
                return 5.0  # Neutral score
            
            # Calculate various indicators
            sma_20 = data['Close'].rolling(window=20).mean()
            sma_50 = data['Close'].rolling(window=50).mean()
            rsi = PortfolioService._calculate_rsi(data['Close'])
            macd_line, macd_signal = PortfolioService._calculate_macd(data['Close'])
            
            current_price = data['Close'].iloc[-1]
            volume_trend = data['Volume'].rolling(window=10).mean().iloc[-1] / data['Volume'].rolling(window=30).mean().iloc[-1]
            
            # AI Score components (0-10 scale)
            trend_score = 0
            if current_price > sma_20.iloc[-1]:
                trend_score += 2
            if sma_20.iloc[-1] > sma_50.iloc[-1]:
                trend_score += 2
            
            momentum_score = 0
            if rsi.iloc[-1] > 30 and rsi.iloc[-1] < 70:
                momentum_score += 2
            if macd_line.iloc[-1] > macd_signal.iloc[-1]:
                momentum_score += 1
            
            volume_score = min(2, volume_trend) if volume_trend > 1 else 0
            
            # Price action score
            price_change_5d = (current_price - data['Close'].iloc[-6]) / data['Close'].iloc[-6] * 100
            price_action_score = min(2, max(-2, price_change_5d / 5)) + 2
            
            # Combine scores
            ai_score = (trend_score + momentum_score + volume_score + price_action_score) / 8 * 10
            
            return min(10, max(0, ai_score))
            
        except Exception as e:
            logger.error(f"Error calculating AI score for {symbol}: {e}")
            return 5.0
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal).mean()
        return macd_line, macd_signal
    
    @staticmethod
    def generate_signals(symbol: str, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate trading signals"""
        signals = []
        
        try:
            if data.empty:
                return signals
            
            # Calculate indicators
            sma_20 = data['Close'].rolling(window=20).mean()
            sma_50 = data['Close'].rolling(window=50).mean()
            rsi = PortfolioService._calculate_rsi(data['Close'])
            macd_line, macd_signal = PortfolioService._calculate_macd(data['Close'])
            
            current_price = data['Close'].iloc[-1]
            
            # Golden Cross signal
            if (sma_20.iloc[-1] > sma_50.iloc[-1] and 
                sma_20.iloc[-2] <= sma_50.iloc[-2]):
                signals.append({
                    "type": "GOLDEN_CROSS",
                    "description": "SMA 20 krysser over SMA 50 - bullish signal",
                    "strength": "Strong",
                    "timeframe": "Medium term"
                })
            
            # RSI signals
            if rsi.iloc[-1] < 30:
                signals.append({
                    "type": "RSI_OVERSOLD",
                    "description": "RSI under 30 - potensielt oversold",
                    "strength": "Medium",
                    "timeframe": "Short term"
                })
            elif rsi.iloc[-1] > 70:
                signals.append({
                    "type": "RSI_OVERBOUGHT", 
                    "description": "RSI over 70 - potensielt overkjøpt",
                    "strength": "Medium",
                    "timeframe": "Short term"
                })
            
            # MACD signals
            if (macd_line.iloc[-1] > macd_signal.iloc[-1] and 
                macd_line.iloc[-2] <= macd_signal.iloc[-2]):
                signals.append({
                    "type": "MACD_BULLISH",
                    "description": "MACD linje krysser over signal linje",
                    "strength": "Medium",
                    "timeframe": "Medium term"
                })
            
            # Volume analysis
            avg_volume = data['Volume'].rolling(window=20).mean().iloc[-1]
            if data['Volume'].iloc[-1] > avg_volume * 1.5:
                signals.append({
                    "type": "HIGH_VOLUME",
                    "description": "Høyt handelsvolum - økt interesse",
                    "strength": "Medium",
                    "timeframe": "Short term"
                })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {e}")
            return signals

def get_ai_analysis(symbol: str) -> Dict[str, Any]:
    """Get comprehensive AI analysis for a stock"""
    try:
        # Add .OL suffix for Norwegian stocks if not present
        ticker_symbol = symbol if '.OL' in symbol else f"{symbol}.OL"
        
        # Get stock data
        ticker = yf.Ticker(ticker_symbol)
        data = ticker.history(period="3mo")  # 3 months of data
        
        if data.empty:
            return {
                "symbol": symbol,
                "current_price": 0,
                "ai_score": 5.0,
                "signals": [],
                "risk_assessment": {"level": "Unknown", "volatility": "Unknown", "beta": "Unknown"},
                "week_change": 0,
                "error": "No data available"
            }
        
        current_price = float(data['Close'].iloc[-1])
        week_ago_price = float(data['Close'].iloc[-6]) if len(data) > 5 else current_price
        week_change = ((current_price - week_ago_price) / week_ago_price * 100) if week_ago_price > 0 else 0
        
        # Calculate AI score
        ai_score = PortfolioService.calculate_ai_score(symbol, data)
        
        # Generate signals
        signals = PortfolioService.generate_signals(symbol, data)
        
        # Risk assessment
        volatility = data['Close'].pct_change().std() * np.sqrt(252) * 100  # Annualized volatility
        risk_level = "Low" if volatility < 20 else "Medium" if volatility < 40 else "High"
        
        # Get basic company info
        info = ticker.info
        beta = info.get('beta', 1.0) if info else 1.0
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "ai_score": ai_score,
            "signals": signals,
            "risk_assessment": {
                "level": risk_level,
                "volatility": f"{volatility:.1f}%",
                "beta": beta
            },
            "week_change": week_change,
            "technical_indicators": {
                "rsi": float(PortfolioService._calculate_rsi(data['Close']).iloc[-1]),
                "sma_20": float(data['Close'].rolling(window=20).mean().iloc[-1]),
                "sma_50": float(data['Close'].rolling(window=50).mean().iloc[-1]),
                "volume_trend": float(data['Volume'].rolling(window=10).mean().iloc[-1] / data['Volume'].rolling(window=30).mean().iloc[-1])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting AI analysis for {symbol}: {e}")
        return {
            "symbol": symbol,
            "current_price": 0,
            "ai_score": 5.0,
            "signals": [],
            "risk_assessment": {"level": "Unknown", "volatility": "Unknown", "beta": "Unknown"},
            "week_change": 0,
            "error": str(e)
        }

def optimize_portfolio(stocks: List[str], target_return: float = 0.10) -> Dict[str, Any]:
    """Optimize portfolio allocation using Modern Portfolio Theory"""
    try:
        # This is a simplified implementation
        # In production, you'd use more sophisticated optimization
        
        equal_weight = 1.0 / len(stocks)
        optimization_result = {
            "weights": {stock: equal_weight for stock in stocks},
            "expected_return": target_return,
            "volatility": 0.15,
            "sharpe_ratio": (target_return - 0.02) / 0.15,  # Assuming 2% risk-free rate
            "method": "Equal Weight (Simplified)"
        }
        
        return optimization_result
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        return {
            "weights": {},
            "expected_return": 0,
            "volatility": 0,
            "sharpe_ratio": 0,
            "error": str(e)
        }
