from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from ..models.user import User
from ..extensions import db
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import json
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

backtest_bp = Blueprint('backtest', __name__)

class BacktestEngine:
    """Avansert backtest-system for trading-strategier"""
    
    def __init__(self):
        self.commission = 0.001  # 0.1% commission per trade
        self.slippage = 0.0005   # 0.05% slippage
        
    def get_data(self, symbols, start_date, end_date):
        """Hent historiske data for backtesting"""
        try:
            data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=start_date, end=end_date)
                if not hist.empty:
                    data[symbol] = hist
            
            return data
        except Exception as e:
            current_app.logger.error(f"Feil ved henting av backtest-data: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Beregn tekniske indikatorer"""
        # Simple Moving Averages
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # Bollinger Bands
        df['BB_middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Price momentum
        df['Momentum_10'] = df['Close'] / df['Close'].shift(10) - 1
        df['Momentum_20'] = df['Close'] / df['Close'].shift(20) - 1
        
        return df
    
    def strategy_sma_crossover(self, df, short_window=10, long_window=50):
        """Simple Moving Average Crossover Strategy"""
        df = self.calculate_technical_indicators(df)
        
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['short_sma'] = df[f'SMA_{short_window}']
        signals['long_sma'] = df[f'SMA_{long_window}']
        
        # Generate signals
        signals['signal'] = 0
        signals['signal'][short_window:] = np.where(
            signals['short_sma'][short_window:] > signals['long_sma'][short_window:], 1, 0
        )
        signals['positions'] = signals['signal'].diff()
        
        return signals
    
    def strategy_rsi_mean_reversion(self, df, rsi_low=30, rsi_high=70):
        """RSI Mean Reversion Strategy"""
        df = self.calculate_technical_indicators(df)
        
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['rsi'] = df['RSI']
        
        # Generate signals
        signals['signal'] = 0
        signals['buy_signal'] = (df['RSI'] < rsi_low)
        signals['sell_signal'] = (df['RSI'] > rsi_high)
        
        # Track position
        position = 0
        positions = []
        for i in range(len(signals)):
            if signals['buy_signal'].iloc[i] and position == 0:
                position = 1
            elif signals['sell_signal'].iloc[i] and position == 1:
                position = 0
            positions.append(position)
        
        signals['signal'] = positions
        signals['positions'] = signals['signal'].diff()
        
        return signals
    
    def strategy_macd_momentum(self, df):
        """MACD Momentum Strategy"""
        df = self.calculate_technical_indicators(df)
        
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['macd'] = df['MACD']
        signals['macd_signal'] = df['MACD_signal']
        
        # Generate signals
        signals['signal'] = 0
        signals['signal'] = np.where(df['MACD'] > df['MACD_signal'], 1, 0)
        signals['positions'] = signals['signal'].diff()
        
        return signals
    
    def strategy_bollinger_bands(self, df):
        """Bollinger Bands Mean Reversion Strategy"""
        df = self.calculate_technical_indicators(df)
        
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        signals['bb_upper'] = df['BB_upper']
        signals['bb_lower'] = df['BB_lower']
        signals['bb_middle'] = df['BB_middle']
        
        # Generate signals
        signals['signal'] = 0
        buy_condition = df['Close'] < df['BB_lower']
        sell_condition = df['Close'] > df['BB_upper']
        
        position = 0
        positions = []
        for i in range(len(signals)):
            if buy_condition.iloc[i] and position == 0:
                position = 1
            elif sell_condition.iloc[i] and position == 1:
                position = 0
            positions.append(position)
        
        signals['signal'] = positions
        signals['positions'] = signals['signal'].diff()
        
        return signals
    
    def strategy_multi_factor(self, df):
        """Multi-factor AI-inspired Strategy"""
        df = self.calculate_technical_indicators(df)
        
        signals = pd.DataFrame(index=df.index)
        signals['price'] = df['Close']
        
        # Combine multiple factors
        # Trend following
        trend_score = np.where(df['SMA_10'] > df['SMA_50'], 1, -1)
        
        # Momentum
        momentum_score = np.where(df['Momentum_10'] > 0.02, 1, 
                                np.where(df['Momentum_10'] < -0.02, -1, 0))
        
        # Mean reversion
        mean_reversion_score = np.where(df['RSI'] < 30, 1,
                                      np.where(df['RSI'] > 70, -1, 0))
        
        # Volume confirmation
        volume_score = np.where(df['Volume_ratio'] > 1.5, 1, 0)
        
        # Combine scores
        combined_score = trend_score + momentum_score + mean_reversion_score + volume_score
        
        # Generate signals
        signals['signal'] = np.where(combined_score >= 2, 1, 0)
        signals['positions'] = signals['signal'].diff()
        signals['combined_score'] = combined_score
        
        return signals
    
    def backtest_strategy(self, df, signals, initial_capital=100000):
        """Kjør backtest av strategi"""
        # Initialize the portfolio
        portfolio = pd.DataFrame(index=signals.index)
        portfolio['holdings'] = signals['signal'] * initial_capital / signals['price']
        portfolio['cash'] = initial_capital - (portfolio['holdings'] * signals['price'])
        portfolio['total'] = portfolio['cash'] + (portfolio['holdings'] * signals['price'])
        
        # Calculate returns
        portfolio['returns'] = portfolio['total'].pct_change()
        portfolio['cumulative_returns'] = (1 + portfolio['returns']).cumprod()
        
        # Account for transaction costs
        trades = signals['positions'].abs().sum()
        total_commission = trades * initial_capital * self.commission
        portfolio['total_after_costs'] = portfolio['total'] - (total_commission / len(portfolio))
        
        return portfolio
    
    def calculate_metrics(self, portfolio, benchmark_returns=None):
        """Beregn performance-målinger"""
        returns = portfolio['returns'].dropna()
        
        # Basic metrics
        total_return = (portfolio['total'].iloc[-1] / portfolio['total'].iloc[0]) - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - 0.02) / volatility  # Assuming 2% risk-free rate
        
        # Drawdown analysis
        running_max = portfolio['total'].cummax()
        drawdown = (portfolio['total'] - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Win rate
        positive_returns = returns[returns > 0]
        win_rate = len(positive_returns) / len(returns) if len(returns) > 0 else 0
        
        # Calmar ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Sortino ratio
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 0
        sortino_ratio = (annual_return - 0.02) / downside_deviation if downside_deviation != 0 else 0
        
        metrics = {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'total_trades': len(returns),
            'avg_return_per_trade': returns.mean() if len(returns) > 0 else 0
        }
        
        # Benchmark comparison
        if benchmark_returns is not None:
            benchmark_annual = (1 + benchmark_returns.mean()) ** 252 - 1
            alpha = annual_return - benchmark_annual
            beta = np.cov(returns, benchmark_returns)[0, 1] / np.var(benchmark_returns)
            metrics['alpha'] = alpha
            metrics['beta'] = beta
        
        return metrics

@backtest_bp.route('/')
@login_required
def index():
    """Backtest hovedside"""
    return render_template('backtest/index.html')

@backtest_bp.route('/strategy_builder')
@login_required
def strategy_builder():
    """Strategibygger"""
    return render_template('backtest/strategy_builder.html')

@backtest_bp.route('/api/run_backtest', methods=['POST'])
@login_required
def run_backtest():
    """API-endpoint for å kjøre backtest"""
    try:
        data = request.get_json()
        
        symbol = data.get('symbol')
        strategy = data.get('strategy')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        initial_capital = data.get('initial_capital', 100000)
        
        if not all([symbol, strategy, start_date, end_date]):
            return jsonify({'error': 'Manglende påkrevde felter'}), 400
        
        engine = BacktestEngine()
        
        # Hent data
        stock_data = engine.get_data([symbol], start_date, end_date)
        if not stock_data or symbol not in stock_data:
            return jsonify({'error': f'Kunne ikke hente data for {symbol}'}), 400
        
        df = stock_data[symbol]
        
        # Kjør strategi
        if strategy == 'sma_crossover':
            short_window = data.get('short_window', 10)
            long_window = data.get('long_window', 50)
            signals = engine.strategy_sma_crossover(df, short_window, long_window)
        elif strategy == 'rsi_mean_reversion':
            rsi_low = data.get('rsi_low', 30)
            rsi_high = data.get('rsi_high', 70)
            signals = engine.strategy_rsi_mean_reversion(df, rsi_low, rsi_high)
        elif strategy == 'macd_momentum':
            signals = engine.strategy_macd_momentum(df)
        elif strategy == 'bollinger_bands':
            signals = engine.strategy_bollinger_bands(df)
        elif strategy == 'multi_factor':
            signals = engine.strategy_multi_factor(df)
        else:
            return jsonify({'error': 'Ukjent strategi'}), 400
        
        # Kjør backtest
        portfolio = engine.backtest_strategy(df, signals, initial_capital)
        
        # Beregn benchmark (buy and hold)
        benchmark_return = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
        benchmark_returns = df['Close'].pct_change().dropna()
        
        # Beregn målinger
        metrics = engine.calculate_metrics(portfolio, benchmark_returns)
        
        # Forbered data for retur
        result = {
            'symbol': symbol,
            'strategy': strategy,
            'period': f"{start_date} til {end_date}",
            'initial_capital': initial_capital,
            'metrics': metrics,
            'benchmark_return': benchmark_return,
            'portfolio_data': {
                'dates': [d.strftime('%Y-%m-%d') for d in portfolio.index],
                'total_value': portfolio['total'].tolist(),
                'returns': portfolio['returns'].fillna(0).tolist(),
                'cumulative_returns': portfolio['cumulative_returns'].tolist()
            },
            'signals_data': {
                'dates': [d.strftime('%Y-%m-%d') for d in signals.index],
                'prices': signals['price'].tolist(),
                'signals': signals['signal'].tolist(),
                'positions': signals['positions'].fillna(0).tolist()
            }
        }
        
        # Legg til strategi-spesifikk data
        if 'short_sma' in signals.columns:
            result['signals_data']['short_sma'] = signals['short_sma'].tolist()
            result['signals_data']['long_sma'] = signals['long_sma'].tolist()
        elif 'rsi' in signals.columns:
            result['signals_data']['rsi'] = signals['rsi'].tolist()
        elif 'macd' in signals.columns:
            result['signals_data']['macd'] = signals['macd'].tolist()
            result['signals_data']['macd_signal'] = signals['macd_signal'].tolist()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Feil ved backtest: {e}")
        return jsonify({'error': 'Intern serverfeil'}), 500

@backtest_bp.route('/api/optimize_strategy', methods=['POST'])
@login_required
def optimize_strategy():
    """Optimaliser strategi-parametere"""
    try:
        data = request.get_json()
        
        symbol = data.get('symbol')
        strategy = data.get('strategy')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        optimization_metric = data.get('metric', 'sharpe_ratio')
        
        engine = BacktestEngine()
        
        # Hent data
        stock_data = engine.get_data([symbol], start_date, end_date)
        if not stock_data or symbol not in stock_data:
            return jsonify({'error': f'Kunne ikke hente data for {symbol}'}), 400
        
        df = stock_data[symbol]
        
        best_params = None
        best_score = -np.inf
        results = []
        
        if strategy == 'sma_crossover':
            # Test ulike SMA-kombinasjoner
            short_windows = range(5, 21, 2)
            long_windows = range(20, 101, 10)
            
            for short in short_windows:
                for long in long_windows:
                    if short >= long:
                        continue
                    
                    try:
                        signals = engine.strategy_sma_crossover(df, short, long)
                        portfolio = engine.backtest_strategy(df, signals)
                        metrics = engine.calculate_metrics(portfolio)
                        
                        score = metrics[optimization_metric]
                        
                        results.append({
                            'short_window': short,
                            'long_window': long,
                            'score': score,
                            'total_return': metrics['total_return'],
                            'sharpe_ratio': metrics['sharpe_ratio'],
                            'max_drawdown': metrics['max_drawdown']
                        })
                        
                        if score > best_score:
                            best_score = score
                            best_params = {'short_window': short, 'long_window': long}
                    
                    except Exception as e:
                        continue
        
        elif strategy == 'rsi_mean_reversion':
            # Test ulike RSI-terskler
            low_thresholds = range(20, 36, 2)
            high_thresholds = range(65, 81, 2)
            
            for low in low_thresholds:
                for high in high_thresholds:
                    if high <= low + 20:
                        continue
                    
                    try:
                        signals = engine.strategy_rsi_mean_reversion(df, low, high)
                        portfolio = engine.backtest_strategy(df, signals)
                        metrics = engine.calculate_metrics(portfolio)
                        
                        score = metrics[optimization_metric]
                        
                        results.append({
                            'rsi_low': low,
                            'rsi_high': high,
                            'score': score,
                            'total_return': metrics['total_return'],
                            'sharpe_ratio': metrics['sharpe_ratio'],
                            'max_drawdown': metrics['max_drawdown']
                        })
                        
                        if score > best_score:
                            best_score = score
                            best_params = {'rsi_low': low, 'rsi_high': high}
                    
                    except Exception as e:
                        continue
        
        # Sorter resultater
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'best_params': best_params,
            'best_score': best_score,
            'optimization_metric': optimization_metric,
            'results': results[:20]  # Returner top 20 resultater
        })
        
    except Exception as e:
        current_app.logger.error(f"Feil ved optimalisering: {e}")
        return jsonify({'error': 'Intern serverfeil'}), 500

@backtest_bp.route('/api/compare_strategies', methods=['POST'])
@login_required
def compare_strategies():
    """Sammenlign flere strategier"""
    try:
        data = request.get_json()
        
        symbol = data.get('symbol')
        strategies = data.get('strategies', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        initial_capital = data.get('initial_capital', 100000)
        
        engine = BacktestEngine()
        
        # Hent data
        stock_data = engine.get_data([symbol], start_date, end_date)
        if not stock_data or symbol not in stock_data:
            return jsonify({'error': f'Kunne ikke hente data for {symbol}'}), 400
        
        df = stock_data[symbol]
        
        comparison_results = []
        
        for strategy_config in strategies:
            strategy_name = strategy_config['name']
            
            try:
                if strategy_name == 'sma_crossover':
                    signals = engine.strategy_sma_crossover(
                        df, 
                        strategy_config.get('short_window', 10),
                        strategy_config.get('long_window', 50)
                    )
                elif strategy_name == 'rsi_mean_reversion':
                    signals = engine.strategy_rsi_mean_reversion(
                        df, 
                        strategy_config.get('rsi_low', 30),
                        strategy_config.get('rsi_high', 70)
                    )
                elif strategy_name == 'macd_momentum':
                    signals = engine.strategy_macd_momentum(df)
                elif strategy_name == 'bollinger_bands':
                    signals = engine.strategy_bollinger_bands(df)
                elif strategy_name == 'multi_factor':
                    signals = engine.strategy_multi_factor(df)
                else:
                    continue
                
                portfolio = engine.backtest_strategy(df, signals, initial_capital)
                metrics = engine.calculate_metrics(portfolio)
                
                comparison_results.append({
                    'strategy': strategy_name,
                    'config': strategy_config,
                    'metrics': metrics,
                    'final_value': portfolio['total'].iloc[-1],
                    'portfolio_data': {
                        'dates': [d.strftime('%Y-%m-%d') for d in portfolio.index],
                        'total_value': portfolio['total'].tolist(),
                        'cumulative_returns': portfolio['cumulative_returns'].tolist()
                    }
                })
                
            except Exception as e:
                current_app.logger.error(f"Feil ved testing av {strategy_name}: {e}")
                continue
        
        # Legg til benchmark
        benchmark_value = df['Close'] / df['Close'].iloc[0] * initial_capital
        comparison_results.append({
            'strategy': 'Buy & Hold',
            'config': {},
            'metrics': {
                'total_return': (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1,
                'annual_return': ((df['Close'].iloc[-1] / df['Close'].iloc[0]) ** (252 / len(df))) - 1,
                'volatility': df['Close'].pct_change().std() * np.sqrt(252),
                'max_drawdown': ((df['Close'] / df['Close'].cummax()) - 1).min()
            },
            'final_value': benchmark_value.iloc[-1],
            'portfolio_data': {
                'dates': [d.strftime('%Y-%m-%d') for d in df.index],
                'total_value': benchmark_value.tolist(),
                'cumulative_returns': (df['Close'] / df['Close'].iloc[0]).tolist()
            }
        })
        
        return jsonify({
            'symbol': symbol,
            'period': f"{start_date} til {end_date}",
            'results': comparison_results
        })
        
    except Exception as e:
        current_app.logger.error(f"Feil ved sammenligning av strategier: {e}")
        return jsonify({'error': 'Intern serverfeil'}), 500
