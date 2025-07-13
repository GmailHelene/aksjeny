"""
Benjamin Graham Analysis Service
Implements Benjamin Graham's value investing principles
"""
from datetime import datetime
import random
from flask import current_app

class GrahamAnalysisService:
    """Service for performing Benjamin Graham style analysis on stocks"""
    
    # Graham's key investment criteria
    CRITERIA = {
        'pe_ratio': {
            'name': 'P/E Ratio',
            'description': 'Should be less than 15',
            'threshold': 15,
            'type': 'maximum'
        },
        'pb_ratio': {
            'name': 'P/B Ratio',
            'description': 'P/E × P/B should be less than 22.5',
            'threshold': 22.5,
            'type': 'combined'
        },
        'current_ratio': {
            'name': 'Current Ratio',
            'description': 'Current assets should be at least 2x current liabilities',
            'threshold': 2.0,
            'type': 'minimum'
        },
        'earnings_growth': {
            'name': 'Earnings Growth',
            'description': 'Positive earnings growth over past 5 years',
            'threshold': 0,
            'type': 'minimum'
        },
        'dividend_history': {
            'name': 'Dividend History',
            'description': 'Uninterrupted dividends for past 20 years',
            'threshold': 20,
            'type': 'years'
        },
        'debt_ratio': {
            'name': 'Debt to Equity',
            'description': 'Long-term debt less than net current assets',
            'threshold': 1.0,
            'type': 'maximum'
        },
        'book_value_growth': {
            'name': 'Book Value Growth',
            'description': 'Book value growth over past 10 years',
            'threshold': 5.0,
            'type': 'minimum'
        }
    }
    
    @staticmethod
    def analyze(ticker):
        """
        Perform Benjamin Graham style analysis on a stock
        Returns comprehensive value analysis
        """
        try:
            # Get stock data
            stock_data = GrahamAnalysisService._get_stock_data(ticker)
            
            # Evaluate Graham criteria
            criteria_results = GrahamAnalysisService._evaluate_criteria(ticker, stock_data)
            
            # Calculate Graham score
            graham_score = GrahamAnalysisService._calculate_graham_score(criteria_results)
            
            # Calculate intrinsic value
            intrinsic_value = GrahamAnalysisService._calculate_intrinsic_value(stock_data)
            
            # Generate recommendation
            recommendation = GrahamAnalysisService._generate_recommendation(
                graham_score, stock_data['price'], intrinsic_value
            )
            
            # Generate detailed analysis
            analysis = GrahamAnalysisService._generate_detailed_analysis(
                ticker, stock_data, criteria_results, graham_score, 
                intrinsic_value, recommendation
            )
            
            return analysis
            
        except Exception as e:
            current_app.logger.error(f"Error in Graham analysis for {ticker}: {str(e)}")
            return GrahamAnalysisService._get_fallback_analysis(ticker)
    
    @staticmethod
    def _get_stock_data(ticker):
        """Get stock data for analysis"""
        # Mock data - would integrate with real data service
        base_data = {
            'EQNR.OL': {'price': 342.55, 'pe': 8.5, 'pb': 1.8, 'current_ratio': 1.9, 'debt_equity': 0.4},
            'DNB.OL': {'price': 212.80, 'pe': 11.2, 'pb': 1.2, 'current_ratio': 2.8, 'debt_equity': 0.2},
            'AAPL': {'price': 185.70, 'pe': 28.5, 'pb': 35.2, 'current_ratio': 1.1, 'debt_equity': 1.5},
            'MSFT': {'price': 390.20, 'pe': 32.1, 'pb': 13.8, 'current_ratio': 1.9, 'debt_equity': 0.7}
        }
        
        if ticker in base_data:
            data = base_data[ticker].copy()
        else:
            data = {
                'price': random.uniform(50, 500),
                'pe': random.uniform(10, 30),
                'pb': random.uniform(1, 5),
                'current_ratio': random.uniform(1.5, 3),
                'debt_equity': random.uniform(0.2, 1.5)
            }
        
        # Add additional fields
        data.update({
            'earnings_growth': random.uniform(-5, 15),
            'dividend_years': random.randint(0, 30),
            'book_value_growth': random.uniform(0, 10),
            'earnings_per_share': data['price'] / data['pe'] if data['pe'] > 0 else 0
        })
        
        return data
    
    @staticmethod
    def _evaluate_criteria(ticker, stock_data):
        """Evaluate stock against Graham criteria"""
        results = {}
        
        # P/E Ratio test
        results['pe_ratio'] = {
            'passed': stock_data['pe'] < 15,
            'value': stock_data['pe'],
            'threshold': 15,
            'score': min(100, (15 / stock_data['pe']) * 100) if stock_data['pe'] > 0 else 100
        }
        
        # P/E × P/B test
        pe_pb_product = stock_data['pe'] * stock_data['pb']
        results['pb_ratio'] = {
            'passed': pe_pb_product < 22.5,
            'value': pe_pb_product,
            'threshold': 22.5,
            'score': min(100, (22.5 / pe_pb_product) * 100) if pe_pb_product > 0 else 100
        }
        
        # Current Ratio test
        results['current_ratio'] = {
            'passed': stock_data['current_ratio'] >= 2.0,
            'value': stock_data['current_ratio'],
            'threshold': 2.0,
            'score': min(100, (stock_data['current_ratio'] / 2.0) * 100)
        }
        
        # Earnings Growth test
        results['earnings_growth'] = {
            'passed': stock_data['earnings_growth'] > 0,
            'value': stock_data['earnings_growth'],
            'threshold': 0,
            'score': min(100, max(0, stock_data['earnings_growth'] * 10))
        }
        
        # Dividend History test
        results['dividend_history'] = {
            'passed': stock_data['dividend_years'] >= 20,
            'value': stock_data['dividend_years'],
            'threshold': 20,
            'score': min(100, (stock_data['dividend_years'] / 20) * 100)
        }
        
        # Debt Ratio test
        results['debt_ratio'] = {
            'passed': stock_data['debt_equity'] < 1.0,
            'value': stock_data['debt_equity'],
            'threshold': 1.0,
            'score': min(100, (1.0 / max(0.1, stock_data['debt_equity'])) * 100)
        }
        
        # Book Value Growth test
        results['book_value_growth'] = {
            'passed': stock_data['book_value_growth'] >= 5.0,
            'value': stock_data['book_value_growth'],
            'threshold': 5.0,
            'score': min(100, (stock_data['book_value_growth'] / 5.0) * 100)
        }
        
        return results
    
    @staticmethod
    def _calculate_graham_score(criteria_results):
        """Calculate overall Graham score"""
        total_score = 0
        criteria_count = len(criteria_results)
        
        for result in criteria_results.values():
            total_score += result['score']
        
        return total_score / criteria_count
    
    @staticmethod
    def _calculate_intrinsic_value(stock_data):
        """Calculate intrinsic value using Graham formula"""
        # Graham Formula: V = EPS × (8.5 + 2g)
        # Where g is expected growth rate
        eps = stock_data.get('earnings_per_share', 10)
        growth_rate = min(stock_data.get('earnings_growth', 5), 15)  # Cap at 15%
        
        intrinsic_value = eps * (8.5 + 2 * growth_rate)
        
        # Apply margin of safety
        return intrinsic_value * 0.75
    
    @staticmethod
    def _generate_recommendation(graham_score, current_price, intrinsic_value):
        """Generate recommendation based on Graham analysis"""
        margin_of_safety = ((intrinsic_value - current_price) / current_price) * 100
        
        if graham_score >= 70 and margin_of_safety > 25:
            return {
                'action': 'STRONG BUY',
                'confidence': 'HIGH',
                'summary': 'Excellent value opportunity with significant margin of safety'
            }
        elif graham_score >= 60 and margin_of_safety > 10:
            return {
                'action': 'BUY',
                'confidence': 'MEDIUM',
                'summary': 'Good value investment with adequate margin of safety'
            }
        elif graham_score >= 50 or margin_of_safety > 0:
            return {
                'action': 'HOLD',
                'confidence': 'MEDIUM',
                'summary': 'Fair value - consider accumulating on dips'
            }
        else:
            return {
                'action': 'AVOID',
                'confidence': 'HIGH',
                'summary': 'Overvalued or fails to meet Graham criteria'
            }
    
    @staticmethod
    def _generate_detailed_analysis(ticker, stock_data, criteria_results, 
                                   graham_score, intrinsic_value, recommendation):
        """Generate comprehensive Graham analysis report"""
        margin_of_safety = ((intrinsic_value - stock_data['price']) / stock_data['price']) * 100
        
        return {
            'ticker': ticker,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'current_price': stock_data['price'],
            'intrinsic_value': round(intrinsic_value, 2),
            'margin_of_safety': round(margin_of_safety, 1),
            'graham_score': round(graham_score, 1),
            'criteria_results': GrahamAnalysisService._format_criteria_results(criteria_results),
            'recommendation': recommendation,
            'key_metrics': {
                'pe_ratio': stock_data['pe'],
                'pb_ratio': stock_data['pb'],
                'current_ratio': stock_data['current_ratio'],
                'debt_equity': stock_data['debt_equity'],
                'earnings_growth': f"{stock_data['earnings_growth']:.1f}%",
                'dividend_years': stock_data['dividend_years']
            },
            'investment_thesis': GrahamAnalysisService._generate_investment_thesis(
                ticker, graham_score, margin_of_safety, criteria_results
            ),
            'graham_principles': GrahamAnalysisService._get_applicable_principles(graham_score)
        }
    
    @staticmethod
    def _format_criteria_results(criteria_results):
        """Format criteria results for display"""
        formatted = []
        for key, result in criteria_results.items():
            criterion = GrahamAnalysisService.CRITERIA[key]
            formatted.append({
                'name': criterion['name'],
                'description': criterion['description'],
                'passed': result['passed'],
                'value': f"{result['value']:.2f}",
                'threshold': result['threshold'],
                'score': round(result['score'], 1)
            })
        return formatted
    
    @staticmethod
    def _generate_investment_thesis(ticker, graham_score, margin_of_safety, criteria_results):
        """Generate investment thesis based on Graham principles"""
        passed_criteria = sum(1 for r in criteria_results.values() if r['passed'])
        total_criteria = len(criteria_results)
        
        if graham_score >= 70 and margin_of_safety > 25:
            return (f"{ticker} is a classic Graham value play, passing {passed_criteria}/{total_criteria} criteria "
                   f"with a {margin_of_safety:.1f}% margin of safety. This represents a compelling opportunity "
                   "for patient value investors seeking capital preservation with upside potential.")
        elif graham_score >= 60:
            return (f"{ticker} shows reasonable value characteristics, passing {passed_criteria}/{total_criteria} criteria. "
                   f"With a {margin_of_safety:.1f}% margin of safety, it may be suitable for conservative investors "
                   "but should be monitored for better entry points.")
        else:
            return (f"{ticker} fails to meet Graham's strict value criteria, passing only {passed_criteria}/{total_criteria} tests. "
                   f"The {'negative' if margin_of_safety < 0 else 'insufficient'} margin of safety suggests "
                   "waiting for a significant price correction before considering investment.")
    
    @staticmethod
    def _get_applicable_principles(graham_score):
        """Get relevant Graham principles based on score"""
        if graham_score >= 70:
            return [
                "Buy when others are fearful",
                "Margin of safety is paramount",
                "Focus on intrinsic value, not market price",
                "Patience is the value investor's greatest virtue"
            ]
        else:
            return [
                "Never compromise on margin of safety",
                "Price is what you pay, value is what you get",
                "In the short run, the market is a voting machine",
                "The intelligent investor is a realist who sells to optimists"
            ]
    
    @staticmethod
    def _get_fallback_analysis(ticker):
        """Return fallback analysis if error occurs"""
        return {
            'ticker': ticker,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'graham_score': 50.0,
            'current_price': 100.0,
            'intrinsic_value': 100.0,
            'margin_of_safety': 0.0,
            'recommendation': {
                'action': 'HOLD',
                'confidence': 'LOW',
                'summary': 'Analysis temporarily unavailable - showing default assessment'
            },
            'error': True
        }
