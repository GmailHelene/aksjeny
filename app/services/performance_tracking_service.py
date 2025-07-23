"""
Advanced Performance Tracking Service
===================================

Comprehensive portfolio performance analysis with attribution,
benchmarking, and advanced analytics.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
import json

logger = logging.getLogger(__name__)

class PerformanceTrackingService:
    """Advanced portfolio performance analytics and attribution"""
    
    @staticmethod
    def calculate_performance_attribution(holdings: List[Dict], 
                                        benchmark: str = 'OSEBX',
                                        periods: List[str] = None) -> Dict:
        """
        Calculate detailed performance attribution analysis
        
        Args:
            holdings: Portfolio holdings with performance data
            benchmark: Benchmark index for comparison
            periods: Time periods for analysis ['1M', '3M', '6M', '1Y', 'YTD']
            
        Returns:
            Comprehensive performance attribution breakdown
        """
        try:
            if periods is None:
                periods = ['1M', '3M', '6M', '1Y', 'YTD']
            
            # Generate performance data
            performance_data = PerformanceTrackingService._generate_performance_data(
                holdings, benchmark
            )
            
            attribution_results = {}
            
            for period in periods:
                period_data = PerformanceTrackingService._get_period_data(
                    performance_data, period
                )
                
                # Calculate attribution components
                attribution = PerformanceTrackingService._calculate_attribution_components(
                    period_data, holdings
                )
                
                attribution_results[period] = attribution
            
            # Overall portfolio metrics
            portfolio_metrics = PerformanceTrackingService._calculate_portfolio_metrics(
                performance_data, holdings
            )
            
            # Risk-adjusted returns
            risk_adjusted = PerformanceTrackingService._calculate_risk_adjusted_returns(
                performance_data
            )
            
            return {
                'success': True,
                'attribution_analysis': attribution_results,
                'portfolio_metrics': portfolio_metrics,
                'risk_adjusted_returns': risk_adjusted,
                'top_contributors': PerformanceTrackingService._identify_top_contributors(
                    attribution_results, holdings
                ),
                'performance_summary': PerformanceTrackingService._generate_performance_summary(
                    attribution_results, portfolio_metrics
                ),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance attribution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def generate_benchmark_comparison(holdings: List[Dict], 
                                    benchmarks: List[str] = None) -> Dict:
        """Generate comprehensive benchmark comparison analysis"""
        try:
            if benchmarks is None:
                benchmarks = ['OSEBX', 'S&P500', 'MSCI_WORLD', 'FTSE_100']
            
            # Calculate portfolio returns
            portfolio_data = PerformanceTrackingService._generate_portfolio_returns(holdings)
            
            comparison_results = {}
            
            for benchmark in benchmarks:
                # Generate benchmark data
                benchmark_data = PerformanceTrackingService._generate_benchmark_data(benchmark)
                
                # Calculate comparison metrics
                comparison = PerformanceTrackingService._calculate_benchmark_metrics(
                    portfolio_data, benchmark_data, benchmark
                )
                
                comparison_results[benchmark] = comparison
            
            # Best/worst performing periods
            performance_periods = PerformanceTrackingService._analyze_performance_periods(
                portfolio_data, comparison_results
            )
            
            return {
                'success': True,
                'benchmark_comparisons': comparison_results,
                'performance_periods': performance_periods,
                'overall_ranking': PerformanceTrackingService._rank_against_benchmarks(
                    comparison_results
                ),
                'outperformance_analysis': PerformanceTrackingService._analyze_outperformance(
                    comparison_results
                ),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Benchmark comparison error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def calculate_factor_exposure(holdings: List[Dict]) -> Dict:
        """Calculate portfolio exposure to various risk factors"""
        try:
            # Define factor exposures for each sector/style
            factor_definitions = {
                'growth': {'tech': 0.8, 'healthcare': 0.6, 'consumer_disc': 0.5},
                'value': {'financials': 0.7, 'energy': 0.8, 'materials': 0.6},
                'momentum': {'tech': 0.6, 'healthcare': 0.4, 'industrials': 0.3},
                'quality': {'healthcare': 0.8, 'consumer_staples': 0.7, 'tech': 0.6},
                'low_volatility': {'utilities': 0.9, 'consumer_staples': 0.8, 'telecoms': 0.7},
                'size': {'small_cap': 1.0, 'mid_cap': 0.5, 'large_cap': -0.5}
            }
            
            # Calculate sector allocations
            sector_allocation = PerformanceTrackingService._calculate_sector_allocation(holdings)
            
            # Calculate factor exposures
            factor_exposures = {}
            for factor, sector_weights in factor_definitions.items():
                exposure = 0
                for sector, allocation in sector_allocation.items():
                    sector_factor_weight = sector_weights.get(sector, 0)
                    exposure += allocation * sector_factor_weight
                
                factor_exposures[factor] = round(exposure, 4)
            
            # Style analysis
            style_analysis = PerformanceTrackingService._calculate_style_analysis(
                factor_exposures
            )
            
            # Risk factor contribution
            risk_contributions = PerformanceTrackingService._calculate_risk_factor_contributions(
                factor_exposures, holdings
            )
            
            return {
                'success': True,
                'factor_exposures': factor_exposures,
                'sector_allocation': sector_allocation,
                'style_analysis': style_analysis,
                'risk_contributions': risk_contributions,
                'factor_recommendations': PerformanceTrackingService._generate_factor_recommendations(
                    factor_exposures, style_analysis
                ),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Factor exposure calculation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def _generate_performance_data(holdings: List[Dict], benchmark: str) -> Dict:
        """Generate synthetic performance data for analysis"""
        # Create date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 2)  # 2 years of data
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        performance_data = {
            'dates': dates,
            'portfolio_returns': [],
            'benchmark_returns': [],
            'individual_returns': {}
        }
        
        # Generate portfolio and benchmark returns
        np.random.seed(42)  # For reproducible results
        
        # Portfolio returns (slightly better than benchmark)
        portfolio_returns = np.random.normal(0.0008, 0.015, len(dates))
        performance_data['portfolio_returns'] = portfolio_returns
        
        # Benchmark returns
        benchmark_returns = np.random.normal(0.0006, 0.014, len(dates))
        performance_data['benchmark_returns'] = benchmark_returns
        
        # Individual stock returns
        for holding in holdings:
            symbol = holding['symbol']
            # Correlate with portfolio but add individual variance
            individual_returns = (
                0.7 * portfolio_returns + 
                0.3 * np.random.normal(0.0005, 0.018, len(dates))
            )
            performance_data['individual_returns'][symbol] = individual_returns
        
        return performance_data
    
    @staticmethod
    def _get_period_data(performance_data: Dict, period: str) -> Dict:
        """Extract data for specific time period"""
        end_date = performance_data['dates'][-1]
        
        if period == '1M':
            start_date = end_date - timedelta(days=30)
        elif period == '3M':
            start_date = end_date - timedelta(days=90)
        elif period == '6M':
            start_date = end_date - timedelta(days=180)
        elif period == '1Y':
            start_date = end_date - timedelta(days=365)
        elif period == 'YTD':
            start_date = datetime(end_date.year, 1, 1)
        else:
            start_date = performance_data['dates'][0]
        
        # Filter data for period
        mask = (performance_data['dates'] >= start_date) & (performance_data['dates'] <= end_date)
        indices = np.where(mask)[0]
        
        return {
            'portfolio_returns': np.array(performance_data['portfolio_returns'])[indices],
            'benchmark_returns': np.array(performance_data['benchmark_returns'])[indices],
            'individual_returns': {
                symbol: np.array(returns)[indices] 
                for symbol, returns in performance_data['individual_returns'].items()
            }
        }
    
    @staticmethod
    def _calculate_attribution_components(period_data: Dict, holdings: List[Dict]) -> Dict:
        """Calculate performance attribution components"""
        portfolio_return = np.sum(period_data['portfolio_returns'])
        benchmark_return = np.sum(period_data['benchmark_returns'])
        
        # Asset allocation effect
        allocation_effect = 0
        selection_effect = 0
        interaction_effect = 0
        
        # Calculate individual contributions
        individual_contributions = {}
        
        for holding in holdings:
            symbol = holding['symbol']
            weight = holding.get('weight', 0)
            
            if symbol in period_data['individual_returns']:
                asset_return = np.sum(period_data['individual_returns'][symbol])
                
                # Simplified attribution calculation
                contribution = weight * asset_return
                individual_contributions[symbol] = {
                    'return': round(asset_return, 6),
                    'weight': weight,
                    'contribution': round(contribution, 6),
                    'excess_return': round(asset_return - benchmark_return, 6)
                }
                
                # Aggregate effects (simplified)
                allocation_effect += weight * (asset_return - benchmark_return) * 0.3
                selection_effect += weight * (asset_return - benchmark_return) * 0.7
        
        return {
            'portfolio_return': round(portfolio_return, 6),
            'benchmark_return': round(benchmark_return, 6),
            'excess_return': round(portfolio_return - benchmark_return, 6),
            'allocation_effect': round(allocation_effect, 6),
            'selection_effect': round(selection_effect, 6),
            'interaction_effect': round(interaction_effect, 6),
            'individual_contributions': individual_contributions
        }
    
    @staticmethod
    def _calculate_portfolio_metrics(performance_data: Dict, holdings: List[Dict]) -> Dict:
        """Calculate comprehensive portfolio performance metrics"""
        portfolio_returns = np.array(performance_data['portfolio_returns'])
        benchmark_returns = np.array(performance_data['benchmark_returns'])
        
        # Cumulative returns
        portfolio_cumulative = np.prod(1 + portfolio_returns) - 1
        benchmark_cumulative = np.prod(1 + benchmark_returns) - 1
        
        # Annualized metrics
        years = len(portfolio_returns) / 252
        annualized_return = (1 + portfolio_cumulative) ** (1/years) - 1
        annualized_volatility = portfolio_returns.std() * np.sqrt(252)
        
        # Risk metrics
        excess_returns = portfolio_returns - benchmark_returns
        tracking_error = excess_returns.std() * np.sqrt(252)
        information_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
        
        # Sharpe ratio
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
        
        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        rolling_max = pd.Series(cumulative_returns).expanding().max()
        drawdown = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        return {
            'total_return': round(portfolio_cumulative, 4),
            'annualized_return': round(annualized_return, 4),
            'volatility': round(annualized_volatility, 4),
            'sharpe_ratio': round(sharpe_ratio, 4),
            'information_ratio': round(information_ratio, 4),
            'tracking_error': round(tracking_error, 4),
            'max_drawdown': round(max_drawdown, 4),
            'calmar_ratio': round(annualized_return / abs(max_drawdown), 4) if max_drawdown != 0 else 0,
            'benchmark_total_return': round(benchmark_cumulative, 4),
            'excess_return': round(portfolio_cumulative - benchmark_cumulative, 4)
        }
    
    @staticmethod
    def _calculate_risk_adjusted_returns(performance_data: Dict) -> Dict:
        """Calculate various risk-adjusted return metrics"""
        portfolio_returns = np.array(performance_data['portfolio_returns'])
        
        # Sortino ratio (downside deviation)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0.001
        
        annualized_return = portfolio_returns.mean() * 252
        risk_free_rate = 0.02
        
        sortino_ratio = (annualized_return - risk_free_rate) / downside_std if downside_std > 0 else 0
        
        # Omega ratio
        threshold = 0.0
        gains = portfolio_returns[portfolio_returns > threshold].sum()
        losses = abs(portfolio_returns[portfolio_returns <= threshold].sum())
        omega_ratio = gains / losses if losses > 0 else float('inf')
        
        # Treynor ratio (assuming beta = 1 for simplification)
        beta = 1.0
        treynor_ratio = (annualized_return - risk_free_rate) / beta
        
        return {
            'sortino_ratio': round(sortino_ratio, 4),
            'omega_ratio': round(min(omega_ratio, 10), 4),  # Cap at 10 for display
            'treynor_ratio': round(treynor_ratio, 4),
            'downside_deviation': round(downside_std, 4),
            'upside_capture': round(np.mean(portfolio_returns[portfolio_returns > 0]) * 252, 4),
            'downside_capture': round(abs(np.mean(portfolio_returns[portfolio_returns < 0])) * 252, 4)
        }
    
    @staticmethod
    def _identify_top_contributors(attribution_results: Dict, holdings: List[Dict]) -> Dict:
        """Identify top and bottom contributors to performance"""
        # Use 1-year data for contributor analysis
        one_year_data = attribution_results.get('1Y', {})
        contributions = one_year_data.get('individual_contributions', {})
        
        if not contributions:
            return {'top_contributors': [], 'top_detractors': []}
        
        # Sort by contribution
        sorted_contributions = sorted(
            contributions.items(),
            key=lambda x: x[1]['contribution'],
            reverse=True
        )
        
        top_contributors = []
        top_detractors = []
        
        for symbol, data in sorted_contributions[:3]:  # Top 3
            top_contributors.append({
                'symbol': symbol,
                'contribution': data['contribution'],
                'return': data['return'],
                'weight': data['weight']
            })
        
        for symbol, data in sorted_contributions[-3:]:  # Bottom 3
            top_detractors.append({
                'symbol': symbol,
                'contribution': data['contribution'],
                'return': data['return'],
                'weight': data['weight']
            })
        
        return {
            'top_contributors': top_contributors,
            'top_detractors': list(reversed(top_detractors))  # Worst first
        }
    
    @staticmethod
    def _generate_performance_summary(attribution_results: Dict, portfolio_metrics: Dict) -> Dict:
        """Generate summary of key performance insights"""
        # Get recent performance (1M, 3M)
        recent_1m = attribution_results.get('1M', {}).get('excess_return', 0)
        recent_3m = attribution_results.get('3M', {}).get('excess_return', 0)
        ytd_excess = attribution_results.get('YTD', {}).get('excess_return', 0)
        
        # Performance classification
        performance_grade = 'A'
        if portfolio_metrics.get('sharpe_ratio', 0) < 0.5:
            performance_grade = 'C'
        elif portfolio_metrics.get('sharpe_ratio', 0) < 1.0:
            performance_grade = 'B'
        
        # Consistency score (based on tracking error)
        tracking_error = portfolio_metrics.get('tracking_error', 0)
        consistency_score = 'High' if tracking_error < 0.05 else 'Medium' if tracking_error < 0.10 else 'Low'
        
        return {
            'performance_grade': performance_grade,
            'consistency_score': consistency_score,
            'recent_momentum': 'Positive' if recent_1m > 0 and recent_3m > 0 else 'Negative',
            'ytd_performance': 'Outperforming' if ytd_excess > 0 else 'Underperforming',
            'risk_efficiency': 'Good' if portfolio_metrics.get('sharpe_ratio', 0) > 1.0 else 'Fair',
            'key_metrics': {
                'best_period': '3M' if recent_3m > recent_1m else '1M',
                'worst_drawdown': portfolio_metrics.get('max_drawdown', 0),
                'current_risk_level': PerformanceTrackingService._assess_current_risk(portfolio_metrics)
            }
        }
    
    @staticmethod
    def _generate_portfolio_returns(holdings: List[Dict]) -> np.ndarray:
        """Generate portfolio return series"""
        # Simple simulation for demonstration
        np.random.seed(hash(str(holdings)) % 2**32)
        returns = np.random.normal(0.0008, 0.015, 500)  # ~2 years daily
        return returns
    
    @staticmethod
    def _generate_benchmark_data(benchmark: str) -> np.ndarray:
        """Generate benchmark return series"""
        benchmark_params = {
            'OSEBX': {'mean': 0.0006, 'std': 0.014},
            'S&P500': {'mean': 0.0008, 'std': 0.016},
            'MSCI_WORLD': {'mean': 0.0007, 'std': 0.015},
            'FTSE_100': {'mean': 0.0005, 'std': 0.013}
        }
        
        params = benchmark_params.get(benchmark, benchmark_params['OSEBX'])
        np.random.seed(hash(benchmark) % 2**32)
        returns = np.random.normal(params['mean'], params['std'], 500)
        return returns
    
    @staticmethod
    def _calculate_benchmark_metrics(portfolio_data: np.ndarray, 
                                   benchmark_data: np.ndarray, 
                                   benchmark_name: str) -> Dict:
        """Calculate metrics vs specific benchmark"""
        portfolio_total = np.prod(1 + portfolio_data) - 1
        benchmark_total = np.prod(1 + benchmark_data) - 1
        
        # Correlation
        correlation = np.corrcoef(portfolio_data, benchmark_data)[0, 1]
        
        # Beta
        beta = np.cov(portfolio_data, benchmark_data)[0, 1] / np.var(benchmark_data)
        
        # Alpha (Jensen's alpha)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        alpha = portfolio_data.mean() - (risk_free_rate + beta * (benchmark_data.mean() - risk_free_rate))
        
        # Tracking error
        tracking_error = (portfolio_data - benchmark_data).std() * np.sqrt(252)
        
        return {
            'total_return_diff': round(portfolio_total - benchmark_total, 4),
            'correlation': round(correlation, 4),
            'beta': round(beta, 4),
            'alpha': round(alpha * 252, 4),  # Annualized
            'tracking_error': round(tracking_error, 4),
            'up_capture': round(PerformanceTrackingService._calculate_capture_ratio(
                portfolio_data, benchmark_data, 'up'
            ), 4),
            'down_capture': round(PerformanceTrackingService._calculate_capture_ratio(
                portfolio_data, benchmark_data, 'down'
            ), 4)
        }
    
    @staticmethod
    def _calculate_capture_ratio(portfolio_returns: np.ndarray, 
                               benchmark_returns: np.ndarray, 
                               direction: str) -> float:
        """Calculate up/down capture ratios"""
        if direction == 'up':
            mask = benchmark_returns > 0
        else:
            mask = benchmark_returns < 0
        
        if np.sum(mask) == 0:
            return 1.0
        
        portfolio_avg = portfolio_returns[mask].mean()
        benchmark_avg = benchmark_returns[mask].mean()
        
        return portfolio_avg / benchmark_avg if benchmark_avg != 0 else 1.0
    
    @staticmethod
    def _analyze_performance_periods(portfolio_data: np.ndarray, 
                                   comparison_results: Dict) -> Dict:
        """Analyze best and worst performing periods"""
        # Find rolling 30-day periods
        rolling_returns = []
        for i in range(len(portfolio_data) - 30):
            period_return = np.prod(1 + portfolio_data[i:i+30]) - 1
            rolling_returns.append(period_return)
        
        rolling_returns = np.array(rolling_returns)
        
        best_period_idx = np.argmax(rolling_returns)
        worst_period_idx = np.argmin(rolling_returns)
        
        return {
            'best_30day_return': round(rolling_returns[best_period_idx], 4),
            'worst_30day_return': round(rolling_returns[worst_period_idx], 4),
            'positive_periods_pct': round(np.mean(rolling_returns > 0) * 100, 1),
            'volatility_trends': {
                'increasing': np.std(rolling_returns[-60:]) > np.std(rolling_returns[:-60]),
                'current_volatility': round(np.std(rolling_returns[-30:]), 4)
            }
        }
    
    @staticmethod
    def _rank_against_benchmarks(comparison_results: Dict) -> Dict:
        """Rank portfolio performance against all benchmarks"""
        benchmark_rankings = []
        
        for benchmark, metrics in comparison_results.items():
            benchmark_rankings.append({
                'benchmark': benchmark,
                'total_return_diff': metrics['total_return_diff'],
                'alpha': metrics['alpha'],
                'tracking_error': metrics['tracking_error']
            })
        
        # Sort by total return difference
        benchmark_rankings.sort(key=lambda x: x['total_return_diff'], reverse=True)
        
        outperformed = sum(1 for b in benchmark_rankings if b['total_return_diff'] > 0)
        
        return {
            'rankings': benchmark_rankings,
            'outperformed_count': outperformed,
            'total_benchmarks': len(benchmark_rankings),
            'percentile_rank': round(outperformed / len(benchmark_rankings) * 100, 1)
        }
    
    @staticmethod
    def _analyze_outperformance(comparison_results: Dict) -> Dict:
        """Analyze consistency of outperformance"""
        alpha_values = [metrics['alpha'] for metrics in comparison_results.values()]
        return_diffs = [metrics['total_return_diff'] for metrics in comparison_results.values()]
        
        return {
            'average_alpha': round(np.mean(alpha_values), 4),
            'alpha_consistency': round(np.std(alpha_values), 4),
            'average_outperformance': round(np.mean(return_diffs), 4),
            'outperformance_consistency': 'High' if np.std(return_diffs) < 0.02 else 'Low'
        }
    
    @staticmethod
    def _calculate_sector_allocation(holdings: List[Dict]) -> Dict:
        """Calculate sector allocation from holdings"""
        # Mock sector mapping for demonstration
        sector_mapping = {
            'AAPL': 'tech', 'MSFT': 'tech', 'GOOGL': 'tech',
            'JPM': 'financials', 'BAC': 'financials',
            'JNJ': 'healthcare', 'PFE': 'healthcare',
            'XOM': 'energy', 'CVX': 'energy'
        }
        
        sector_allocation = {}
        for holding in holdings:
            sector = sector_mapping.get(holding['symbol'], 'other')
            weight = holding.get('weight', 0)
            sector_allocation[sector] = sector_allocation.get(sector, 0) + weight
        
        return sector_allocation
    
    @staticmethod
    def _calculate_style_analysis(factor_exposures: Dict) -> Dict:
        """Analyze portfolio style characteristics"""
        growth_score = factor_exposures.get('growth', 0)
        value_score = factor_exposures.get('value', 0)
        quality_score = factor_exposures.get('quality', 0)
        
        # Determine dominant style
        if growth_score > value_score + 0.2:
            dominant_style = 'Growth'
        elif value_score > growth_score + 0.2:
            dominant_style = 'Value'
        else:
            dominant_style = 'Balanced'
        
        return {
            'dominant_style': dominant_style,
            'growth_tilt': round(growth_score, 4),
            'value_tilt': round(value_score, 4),
            'quality_score': round(quality_score, 4),
            'style_consistency': 'High' if abs(growth_score - value_score) > 0.3 else 'Low'
        }
    
    @staticmethod
    def _calculate_risk_factor_contributions(factor_exposures: Dict, holdings: List[Dict]) -> Dict:
        """Calculate how much each factor contributes to portfolio risk"""
        total_risk = 0.15  # Assumed portfolio volatility
        
        # Risk contribution from each factor (simplified)
        risk_contributions = {}
        factor_volatilities = {
            'growth': 0.20, 'value': 0.16, 'momentum': 0.18,
            'quality': 0.12, 'low_volatility': 0.08, 'size': 0.22
        }
        
        total_factor_risk = 0
        for factor, exposure in factor_exposures.items():
            factor_vol = factor_volatilities.get(factor, 0.15)
            factor_risk = abs(exposure) * factor_vol
            risk_contributions[factor] = round(factor_risk, 4)
            total_factor_risk += factor_risk
        
        # Normalize to sum to total portfolio risk
        normalization_factor = total_risk / total_factor_risk if total_factor_risk > 0 else 1
        for factor in risk_contributions:
            risk_contributions[factor] *= normalization_factor
            risk_contributions[factor] = round(risk_contributions[factor], 4)
        
        return risk_contributions
    
    @staticmethod
    def _generate_factor_recommendations(factor_exposures: Dict, style_analysis: Dict) -> List[str]:
        """Generate recommendations based on factor analysis"""
        recommendations = []
        
        # Check for extreme exposures
        for factor, exposure in factor_exposures.items():
            if abs(exposure) > 0.8:
                recommendations.append(f"High {factor} exposure - consider rebalancing")
        
        # Style recommendations
        if style_analysis['style_consistency'] == 'Low':
            recommendations.append("Portfolio lacks clear style focus - consider defining investment style")
        
        # Factor concentration
        max_exposure = max(abs(exp) for exp in factor_exposures.values())
        if max_exposure > 0.6:
            recommendations.append("High factor concentration detected - diversify factor exposures")
        
        return recommendations if recommendations else ["Factor exposures are well-balanced"]
    
    @staticmethod
    def _assess_current_risk(portfolio_metrics: Dict) -> str:
        """Assess current risk level of portfolio"""
        volatility = portfolio_metrics.get('volatility', 0)
        max_drawdown = abs(portfolio_metrics.get('max_drawdown', 0))
        
        risk_score = volatility * 0.6 + max_drawdown * 0.4
        
        if risk_score < 0.12:
            return 'Low'
        elif risk_score < 0.20:
            return 'Moderate'
        else:
            return 'High'
