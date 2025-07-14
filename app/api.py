"""
API routes for Aksjeradar
"""
from flask import Blueprint, jsonify, request
from flask_login import current_user
from .services.ml_prediction_service import MLPredictionService
from .services.portfolio_optimizer import PortfolioOptimizer  
from .services.risk_manager import RiskManager
from .services.insider_trading_service import InsiderTradingService
from .services.financial_data_aggregator import FinancialDataAggregator
import logging

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

# Initialize services
ml_service = MLPredictionService()
portfolio_optimizer = PortfolioOptimizer()
risk_manager = RiskManager()
insider_service = InsiderTradingService()
data_aggregator = FinancialDataAggregator()

@api.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'aksjeradar',
        'version': '1.0.0'
    })

@api.route('/version')  
def version():
    """Version info endpoint"""
    return jsonify({
        'version': '1.0.0',
        'service': 'aksjeradar'
    })

# ML Prediction endpoints
@api.route('/ml/predict/<symbol>', methods=['GET'])
def predict_stock(symbol):
    """Get ML prediction for a stock"""
    try:
        days_ahead = request.args.get('days', 30, type=int)
        prediction = ml_service.predict_stock_price(symbol, days_ahead)
        
        if prediction:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'prediction': prediction
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to generate prediction'
            }), 404
            
    except Exception as e:
        logger.error(f"Error predicting stock {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Prediction service unavailable'
        }), 500

@api.route('/ml/batch-predict', methods=['POST'])
def batch_predict():
    """Get predictions for multiple stocks"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        days_ahead = data.get('days', 30)
        
        predictions = ml_service.batch_predict(symbols, days_ahead)
        
        return jsonify({
            'success': True,
            'predictions': predictions
        })
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {e}")
        return jsonify({
            'success': False,
            'message': 'Batch prediction failed'
        }), 500

@api.route('/ml/market-analysis', methods=['GET'])
def market_analysis():
    """Get comprehensive market analysis"""
    try:
        analysis = ml_service.get_market_analysis()
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        return jsonify({
            'success': False,
            'message': 'Market analysis unavailable'
        }), 500

# Portfolio Optimization endpoints
@api.route('/portfolio/optimize', methods=['POST'])
def optimize_portfolio():
    """Optimize portfolio allocation"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        weights = data.get('weights')
        method = data.get('method', 'sharpe')
        
        result = portfolio_optimizer.optimize_portfolio(symbols, weights, method)
        
        return jsonify({
            'success': True,
            'optimization': result
        })
        
    except Exception as e:
        logger.error(f"Error optimizing portfolio: {e}")
        return jsonify({
            'success': False,
            'message': 'Portfolio optimization failed'
        }), 500

@api.route('/portfolio/efficient-frontier', methods=['POST'])
def efficient_frontier():
    """Generate efficient frontier for portfolio"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        num_portfolios = data.get('num_portfolios', 10000)
        
        frontier = portfolio_optimizer.generate_efficient_frontier(symbols, num_portfolios)
        
        return jsonify({
            'success': True,
            'frontier': frontier
        })
        
    except Exception as e:
        logger.error(f"Error generating efficient frontier: {e}")
        return jsonify({
            'success': False,
            'message': 'Efficient frontier generation failed'
        }), 500

@api.route('/portfolio/rebalance', methods=['POST'])
def rebalance_portfolio():
    """Get portfolio rebalancing recommendations"""
    try:
        data = request.get_json()
        current_portfolio = data.get('current_portfolio', {})
        target_allocation = data.get('target_allocation', {})
        
        recommendations = portfolio_optimizer.rebalance_portfolio(
            current_portfolio, target_allocation
        )
        
        return jsonify({
            'success': True,
            'rebalancing': recommendations
        })
        
    except Exception as e:
        logger.error(f"Error rebalancing portfolio: {e}")
        return jsonify({
            'success': False,
            'message': 'Portfolio rebalancing failed'
        }), 500

# Risk Management endpoints
@api.route('/risk/portfolio-risk', methods=['POST'])
def portfolio_risk():
    """Calculate portfolio risk metrics"""
    try:
        data = request.get_json()
        portfolio = data.get('portfolio', {})
        timeframe = data.get('timeframe', 252)
        
        risk_metrics = risk_manager.calculate_portfolio_risk(portfolio, timeframe)
        
        return jsonify({
            'success': True,
            'risk_metrics': risk_metrics
        })
        
    except Exception as e:
        logger.error(f"Error calculating portfolio risk: {e}")
        return jsonify({
            'success': False,
            'message': 'Risk calculation failed'
        }), 500

@api.route('/risk/var-analysis', methods=['POST'])
def var_analysis():
    """Perform Value at Risk analysis"""
    try:
        data = request.get_json()
        portfolio = data.get('portfolio', {})
        confidence_level = data.get('confidence_level', 0.95)
        time_horizon = data.get('time_horizon', 1)
        
        var_result = risk_manager.calculate_var(portfolio, confidence_level, time_horizon)
        
        return jsonify({
            'success': True,
            'var_analysis': var_result
        })
        
    except Exception as e:
        logger.error(f"Error in VaR analysis: {e}")
        return jsonify({
            'success': False,
            'message': 'VaR analysis failed'
        }), 500

@api.route('/risk/stress-test', methods=['POST'])
def stress_test():
    """Perform portfolio stress testing"""
    try:
        data = request.get_json()
        portfolio = data.get('portfolio', {})
        scenario = data.get('scenario', 'market_crash')
        
        stress_result = risk_manager.stress_test_portfolio(portfolio, scenario)
        
        return jsonify({
            'success': True,
            'stress_test': stress_result
        })
        
    except Exception as e:
        logger.error(f"Error in stress testing: {e}")
        return jsonify({
            'success': False,
            'message': 'Stress testing failed'
        }), 500

@api.route('/risk/monte-carlo', methods=['POST'])
def monte_carlo_simulation():
    """Run Monte Carlo risk simulation"""
    try:
        data = request.get_json()
        portfolio = data.get('portfolio', {})
        simulations = data.get('simulations', 10000)
        time_horizon = data.get('time_horizon', 252)
        
        mc_result = risk_manager.monte_carlo_simulation(portfolio, simulations, time_horizon)
        
        return jsonify({
            'success': True,
            'monte_carlo': mc_result
        })
        
    except Exception as e:
        logger.error(f"Error in Monte Carlo simulation: {e}")
        return jsonify({
            'success': False,
            'message': 'Monte Carlo simulation failed'
        }), 500

# Insider Trading endpoints
@api.route('/insider-trading/<symbol>', methods=['GET'])
def get_insider_trading_data(symbol):
    """Get insider trading data for a specific stock"""
    try:
        data = insider_service.get_insider_trading_data(symbol)
        
        if data:
            return jsonify({
                'success': True,
                'symbol': symbol,
                'insider_trading_data': data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No insider trading data found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching insider trading data for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Insider trading data service unavailable'
        }), 500

@api.route('/insider-trading/batch', methods=['POST'])
def batch_insider_trading():
    """Get insider trading data for multiple stocks"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        result = {}
        for symbol in symbols:
            result[symbol] = insider_service.get_insider_trading_data(symbol)
        
        return jsonify({
            'success': True,
            'insider_trading_data': result
        })
        
    except Exception as e:
        logger.error(f"Error in batch insider trading data request: {e}")
        return jsonify({
            'success': False,
            'message': 'Batch insider trading data request failed'
        }), 500

# Insider Trading and Market Intelligence endpoints
@api.route('/insider/transactions/<symbol>', methods=['GET'])
def get_insider_transactions(symbol):
    """Get insider trading transactions for a symbol"""
    try:
        days_back = request.args.get('days', 90, type=int)
        transactions = insider_service.get_insider_transactions(symbol, days_back)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'transactions': [insider_service._transaction_to_dict(t) for t in transactions]
        })
        
    except Exception as e:
        logger.error(f"Error getting insider transactions for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get insider transactions'
        }), 500

@api.route('/insider/sentiment/<symbol>', methods=['GET'])
def get_market_sentiment(symbol):
    """Get market sentiment analysis for a symbol"""
    try:
        sentiment = insider_service.get_market_sentiment(symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'sentiment': insider_service._sentiment_to_dict(sentiment)
        })
        
    except Exception as e:
        logger.error(f"Error getting market sentiment for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get market sentiment'
        }), 500

@api.route('/insider/short-interest/<symbol>', methods=['GET'])
def get_short_interest(symbol):
    """Get short interest data for a symbol"""
    try:
        short_data = insider_service.get_short_interest_data(symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'short_interest': insider_service._short_data_to_dict(short_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting short interest for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get short interest data'
        }), 500

@api.route('/insider/analysis/<symbol>', methods=['GET'])
def get_comprehensive_analysis(symbol):
    """Get comprehensive insider trading and market intelligence analysis"""
    try:
        analysis = insider_service.get_comprehensive_analysis(symbol)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error getting comprehensive analysis for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get comprehensive analysis'
        }), 500

@api.route('/insider/batch-analysis', methods=['POST'])
def batch_insider_analysis():
    """Get insider trading analysis for multiple symbols"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({
                'success': False,
                'message': 'No symbols provided'
            }), 400
        
        results = {}
        for symbol in symbols[:10]:  # Limit to 10 symbols
            try:
                results[symbol] = insider_service.get_comprehensive_analysis(symbol)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                results[symbol] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'analyses': results
        })
        
    except Exception as e:
        logger.error(f"Error in batch insider analysis: {e}")
        return jsonify({
            'success': False,
            'message': 'Batch analysis failed'
        }), 500

# Financial News and Market Data endpoints
@api.route('/news/<symbol>', methods=['GET'])
def get_financial_news(symbol):
    """Get financial news for a symbol"""
    try:
        # This would integrate with news APIs
        # For now, return demo data structure
        news_data = {
            'symbol': symbol,
            'articles': [
                {
                    'title': f'Latest analysis on {symbol}',
                    'summary': f'Market experts analyze recent performance of {symbol}',
                    'sentiment': 'positive',
                    'source': 'Financial News',
                    'timestamp': '2025-07-14T10:00:00Z',
                    'url': f'https://example.com/news/{symbol}'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'news': news_data
        })
        
    except Exception as e:
        logger.error(f"Error getting news for {symbol}: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get financial news'
        }), 500

@api.route('/market/overview', methods=['GET'])
def get_market_overview():
    """Get general market overview and sentiment"""
    try:
        overview = {
            'market_status': 'open',
            'overall_sentiment': 'bullish',
            'volatility_index': 18.5,
            'top_movers': [
                {'symbol': 'TSLA', 'change': '+5.2%'},
                {'symbol': 'AAPL', 'change': '+2.1%'},
                {'symbol': 'GOOGL', 'change': '-1.8%'}
            ],
            'insider_activity_summary': {
                'total_transactions_today': 156,
                'buy_sell_ratio': 1.4,
                'top_insider_sectors': ['Technology', 'Healthcare', 'Finance']
            }
        }
        
        return jsonify({
            'success': True,
            'market_overview': overview
        })
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get market overview'
        }), 500

# Comprehensive Financial Data Aggregation endpoints
@api.route('/crypto/data', methods=['GET'])
def get_crypto_data():
    """Get cryptocurrency market data"""
    try:
        symbols = request.args.getlist('symbols')
        limit = request.args.get('limit', 100, type=int)
        
        crypto_data = data_aggregator.get_crypto_data(symbols if symbols else None, limit)
        
        return jsonify({
            'success': True,
            'crypto_data': [data_aggregator._crypto_to_dict(c) for c in crypto_data]
        })
        
    except Exception as e:
        logger.error(f"Error getting crypto data: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get crypto data'
        }), 500

@api.route('/crypto/trending', methods=['GET'])
def get_trending_crypto():
    """Get trending cryptocurrencies"""
    try:
        trending = data_aggregator.get_trending_crypto()
        
        return jsonify({
            'success': True,
            'trending_crypto': trending
        })
        
    except Exception as e:
        logger.error(f"Error getting trending crypto: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get trending crypto'
        }), 500

@api.route('/currency/rates', methods=['GET'])
def get_currency_rates():
    """Get currency exchange rates"""
    try:
        base = request.args.get('base', 'USD')
        targets = request.args.getlist('targets')
        
        if not targets:
            targets = ['EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'SEK', 'NOK', 'DKK']
        
        rates = data_aggregator.get_currency_rates(base, targets)
        
        return jsonify({
            'success': True,
            'currency_rates': [data_aggregator._currency_to_dict(r) for r in rates]
        })
        
    except Exception as e:
        logger.error(f"Error getting currency rates: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get currency rates'
        }), 500

@api.route('/news/financial', methods=['GET'])
def get_financial_news_api():
    """Get financial news from multiple sources"""
    try:
        symbols = request.args.getlist('symbols')
        sources = request.args.getlist('sources')
        limit = request.args.get('limit', 50, type=int)
        
        news = data_aggregator.get_financial_news(symbols if symbols else None, sources if sources else None, limit)
        
        return jsonify({
            'success': True,
            'news': [data_aggregator._news_to_dict(n) for n in news]
        })
        
    except Exception as e:
        logger.error(f"Error getting financial news: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get financial news'
        }), 500

@api.route('/economic/indicators', methods=['GET'])
def get_economic_indicators():
    """Get key economic indicators"""
    try:
        indicators = data_aggregator.get_economic_indicators()
        
        return jsonify({
            'success': True,
            'economic_indicators': [data_aggregator._indicator_to_dict(i) for i in indicators]
        })
        
    except Exception as e:
        logger.error(f"Error getting economic indicators: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get economic indicators'
        }), 500

@api.route('/market/comprehensive', methods=['POST'])
def get_comprehensive_market_data():
    """Get comprehensive market data for multiple symbols"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'])
        
        market_data = data_aggregator.get_comprehensive_market_data(symbols)
        
        return jsonify({
            'success': True,
            'market_data': market_data
        })
        
    except Exception as e:
        logger.error(f"Error getting comprehensive market data: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get comprehensive market data'
        }), 500

@api.route('/dashboard/data', methods=['GET'])
def get_dashboard_data():
    """Get aggregated data for dashboard display"""
    try:
        user_symbols = request.args.getlist('symbols')
        
        if not user_symbols:
            # Default Norwegian and international stocks
            user_symbols = ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'AAPL', 'GOOGL', 'MSFT', 'TSLA']
        
        dashboard_data = data_aggregator.get_aggregated_dashboard_data(user_symbols)
        
        return jsonify({
            'success': True,
            'dashboard_data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get dashboard data'
        }), 500

# Norwegian Market Specific endpoints
@api.route('/norwegian/stocks', methods=['GET'])
def get_norwegian_stocks():
    """Get Norwegian stock market data"""
    try:
        norwegian_symbols = [
            'EQNR.OL', 'DNB.OL', 'TEL.OL', 'YAR.OL', 'NHY.OL', 'AKSO.OL',
            'MOWI.OL', 'ORK.OL', 'SALM.OL', 'AKERBP.OL', 'SUBC.OL', 'KAHOT.OL'
        ]
        
        norwegian_data = data_aggregator.get_comprehensive_market_data(norwegian_symbols)
        
        return jsonify({
            'success': True,
            'norwegian_stocks': norwegian_data
        })
        
    except Exception as e:
        logger.error(f"Error getting Norwegian stocks: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get Norwegian stock data'
        }), 500

@api.route('/market/sectors', methods=['GET'])
def get_sector_analysis():
    """Get sector-wise market analysis"""
    try:
        # Sector data would be calculated from individual stocks
        sector_data = {
            'technology': {
                'symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
                'performance': '+2.3%',
                'trend': 'bullish'
            },
            'energy': {
                'symbols': ['EQNR.OL', 'AKERBP.OL'],
                'performance': '+1.8%',
                'trend': 'bullish'
            },
            'finance': {
                'symbols': ['DNB.OL'],
                'performance': '+0.9%',
                'trend': 'neutral'
            },
            'telecommunications': {
                'symbols': ['TEL.OL'],
                'performance': '-0.5%',
                'trend': 'bearish'
            }
        }
        
        return jsonify({
            'success': True,
            'sector_analysis': sector_data
        })
        
    except Exception as e:
        logger.error(f"Error getting sector analysis: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get sector analysis'
        }), 500

# Real-time data endpoints  
@api.route('/realtime/quotes', methods=['POST'])
def get_realtime_quotes():
    """Get real-time quotes for multiple symbols"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({
                'success': False,
                'message': 'No symbols provided'
            }), 400
        
        # Get real-time data using yfinance or other sources
        quotes = {}
        for symbol in symbols[:20]:  # Limit to 20 symbols
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                quotes[symbol] = {
                    'price': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                    'change': info.get('regularMarketChange', 0),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'volume': info.get('regularMarketVolume', 0),
                    'market_status': 'open'  # Would be determined by market hours
                }
            except:
                # Fallback to demo data
                quotes[symbol] = {
                    'price': np.random.uniform(50, 300),
                    'change': np.random.uniform(-5, 5),
                    'change_percent': np.random.uniform(-3, 3),
                    'volume': np.random.randint(100000, 10000000),
                    'market_status': 'open'
                }
        
        return jsonify({
            'success': True,
            'quotes': quotes
        })
        
    except Exception as e:
        logger.error(f"Error getting real-time quotes: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to get real-time quotes'
        }), 500