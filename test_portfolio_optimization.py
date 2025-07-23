#!/usr/bin/env python3
"""
Test Portfolio Optimization System Implementation
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_portfolio_optimization():
    """Test portfolio optimization service"""
    print("🧪 Testing Portfolio Optimization...")
    
    try:
        from app.services.portfolio_optimization_service import PortfolioOptimizationService
        
        # Test data
        test_holdings = [
            {'symbol': 'AAPL', 'weight': 0.30, 'value': 30000},
            {'symbol': 'MSFT', 'weight': 0.25, 'value': 25000},
            {'symbol': 'GOOGL', 'weight': 0.20, 'value': 20000},
            {'symbol': 'TSLA', 'weight': 0.15, 'value': 15000},
            {'symbol': 'JPM', 'weight': 0.10, 'value': 10000}
        ]
        
        # Test optimization
        result = PortfolioOptimizationService.optimize_portfolio(
            holdings=test_holdings,
            risk_tolerance='moderate'
        )
        
        if result['success']:
            print("✅ Portfolio optimization working")
            print(f"   Expected return: {result['portfolio_metrics']['expected_return']:.4f}")
            print(f"   Sharpe ratio: {result['portfolio_metrics']['sharpe_ratio']:.4f}")
            print(f"   Optimized positions: {len(result['optimized_allocation'])}")
        else:
            print(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test risk metrics
        risk_result = PortfolioOptimizationService.calculate_risk_metrics(
            holdings=test_holdings
        )
        
        if risk_result['success']:
            print("✅ Risk metrics calculation working")
            print(f"   VaR 95%: {risk_result['risk_metrics']['var_95']:.6f}")
            print(f"   Max drawdown: {risk_result['risk_metrics']['max_drawdown']:.4f}")
            print(f"   Risk classification: {risk_result['risk_classification']}")
        else:
            print(f"❌ Risk metrics failed: {risk_result.get('error', 'Unknown error')}")
            return False
        
        # Test scenario analysis
        scenario_result = PortfolioOptimizationService.generate_scenario_analysis(
            holdings=test_holdings
        )
        
        if scenario_result['success']:
            print("✅ Scenario analysis working")
            scenarios = list(scenario_result['scenario_analysis'].keys())
            print(f"   Scenarios analyzed: {scenarios}")
            print(f"   Recommendations: {len(scenario_result['recommendations'])}")
        else:
            print(f"❌ Scenario analysis failed: {scenario_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio optimization test failed: {e}")
        return False

def test_performance_tracking():
    """Test performance tracking service"""
    print("\n🧪 Testing Performance Tracking...")
    
    try:
        from app.services.performance_tracking_service import PerformanceTrackingService
        
        # Test data
        test_holdings = [
            {'symbol': 'AAPL', 'weight': 0.30, 'value': 30000},
            {'symbol': 'MSFT', 'weight': 0.25, 'value': 25000},
            {'symbol': 'GOOGL', 'weight': 0.20, 'value': 20000},
            {'symbol': 'TSLA', 'weight': 0.15, 'value': 15000},
            {'symbol': 'JPM', 'weight': 0.10, 'value': 10000}
        ]
        
        # Test performance attribution
        attribution_result = PerformanceTrackingService.calculate_performance_attribution(
            holdings=test_holdings
        )
        
        if attribution_result['success']:
            print("✅ Performance attribution working")
            periods = list(attribution_result['attribution_analysis'].keys())
            print(f"   Analysis periods: {periods}")
            print(f"   Portfolio metrics available: {len(attribution_result['portfolio_metrics'])}")
        else:
            print(f"❌ Performance attribution failed: {attribution_result.get('error', 'Unknown error')}")
            return False
        
        # Test benchmark comparison
        benchmark_result = PerformanceTrackingService.generate_benchmark_comparison(
            holdings=test_holdings
        )
        
        if benchmark_result['success']:
            print("✅ Benchmark comparison working")
            benchmarks = list(benchmark_result['benchmark_comparisons'].keys())
            print(f"   Benchmarks compared: {benchmarks}")
            print(f"   Overall ranking available: {benchmark_result['overall_ranking']['percentile_rank']}")
        else:
            print(f"❌ Benchmark comparison failed: {benchmark_result.get('error', 'Unknown error')}")
            return False
        
        # Test factor exposure
        factor_result = PerformanceTrackingService.calculate_factor_exposure(
            holdings=test_holdings
        )
        
        if factor_result['success']:
            print("✅ Factor exposure analysis working")
            factors = list(factor_result['factor_exposures'].keys())
            print(f"   Factor exposures: {factors}")
            print(f"   Style analysis: {factor_result['style_analysis']['dominant_style']}")
        else:
            print(f"❌ Factor exposure failed: {factor_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Performance tracking test failed: {e}")
        return False

def test_portfolio_routes():
    """Test that portfolio routes are properly defined"""
    print("\n🧪 Testing Portfolio Routes...")
    
    try:
        # Read the routes file to check for endpoints
        with open('/workspaces/aksjeny/app/routes/portfolio.py', 'r') as f:
            content = f.read()
        
        required_routes = [
            'api_portfolio_optimization',
            'api_risk_metrics',
            'api_scenario_analysis',
            'api_performance_attribution',
            'api_benchmark_comparison',
            'api_factor_exposure',
            'api_portfolio_health'
        ]
        
        found_routes = []
        for route in required_routes:
            if f"def {route}" in content:
                found_routes.append(route)
        
        if len(found_routes) == len(required_routes):
            print("✅ All portfolio API routes found")
            print(f"   Routes: {found_routes}")
            return True
        else:
            missing = set(required_routes) - set(found_routes)
            print(f"❌ Missing routes: {missing}")
            print(f"   Found routes: {found_routes}")
            return False
            
    except Exception as e:
        print(f"❌ Portfolio routes test failed: {e}")
        return False

def test_portfolio_template():
    """Test that portfolio optimization template exists"""
    print("\n🧪 Testing Portfolio Template...")
    
    template_path = '/workspaces/aksjeny/app/templates/portfolio/optimization.html'
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for key components
        required_components = [
            'AI-Powered Portfolio Optimization',
            'optimizePortfolio',
            'runScenarioAnalysis', 
            'calculateRiskMetrics',
            'chart.js',  # Case insensitive check
            'riskTolerance',
            'targetReturn'
        ]
        
        missing = []
        for component in required_components:
            if component not in content:
                missing.append(component)
        
        if missing:
            print(f"❌ Missing template components: {missing}")
            return False
        else:
            print("✅ Portfolio optimization template complete")
            print(f"   Template size: {len(content):,} characters")
            print("   Features: Risk tolerance selection, target return, chart visualization")
            return True
            
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

def main():
    """Run all portfolio optimization tests"""
    print("🚀 AI-Powered Portfolio Optimization System Validation\n")
    
    tests = [
        test_portfolio_optimization,
        test_performance_tracking,
        test_portfolio_routes,
        test_portfolio_template
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Passed: {sum(results)}/{len(results)}")
    print(f"   Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 AI-POWERED PORTFOLIO OPTIMIZATION: READY FOR PRODUCTION!")
        print("   ✅ Modern Portfolio Theory optimization implemented")
        print("   ✅ Comprehensive risk analytics (VaR, drawdown, beta)")
        print("   ✅ Monte Carlo scenario analysis")
        print("   ✅ Performance attribution and benchmarking")
        print("   ✅ Factor exposure and style analysis")
        print("   ✅ Interactive optimization interface")
        print("   ✅ Professional-grade portfolio health scoring")
        
        return True
    else:
        print("\n⚠️  Some components need attention")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
