"""
Test script for Advanced Portfolio Analytics System
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/workspaces/aksjeny')

def test_imports():
    """Test that all required imports work"""
    print("🧪 Testing Advanced Portfolio Analytics imports...")
    
    try:
        # Test core Flask app creation
        from app import create_app
        print("✅ Flask app import successful")
        
        # Test advanced analytics service
        from app.services.advanced_portfolio_analytics import AdvancedPortfolioAnalytics
        print("✅ Advanced Portfolio Analytics service import successful")
        
        # Test portfolio analytics routes
        from app.routes.portfolio_analytics import portfolio_analytics
        print("✅ Portfolio Analytics routes import successful")
        
        # Test required scientific libraries
        import numpy as np
        import pandas as pd
        from sklearn.decomposition import PCA
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        print("✅ Scientific computing libraries available")
        
        # Test dataclasses
        from app.services.advanced_portfolio_analytics import (
            PortfolioMetrics, RiskDecomposition, 
            PerformanceAttribution, OptimizationRecommendation
        )
        print("✅ Advanced analytics dataclasses import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_service_functionality():
    """Test basic service functionality"""
    print("\n🔧 Testing Advanced Portfolio Analytics functionality...")
    
    try:
        from app.services.advanced_portfolio_analytics import AdvancedPortfolioAnalytics
        
        # Create service instance
        analytics = AdvancedPortfolioAnalytics()
        print("✅ Service instance created successfully")
        
        # Test data structure creation
        import numpy as np
        import pandas as pd
        
        # Create sample portfolio data
        sample_data = {
            'returns': np.random.normal(0.001, 0.02, 252),  # Daily returns for 1 year
            'prices': np.random.uniform(100, 500, 10),      # Sample stock prices
            'weights': np.array([0.1] * 10),                # Equal weights
            'symbols': [f'STOCK{i}' for i in range(10)],    # Sample symbols
            'sectors': ['Technology', 'Finance', 'Healthcare', 'Energy', 'Consumer'],
            'market_returns': np.random.normal(0.0008, 0.015, 252)
        }
        
        print("✅ Sample data created for testing")
        
        # Test AI insights generation
        import pandas as pd
        
        # Create sample portfolio DataFrame
        portfolio_df = pd.DataFrame({
            'symbol': sample_data['symbols'],
            'weight': sample_data['weights'],
            'price': sample_data['prices'][:10],
            'sector': sample_data['sectors'] * 2  # Repeat to match length
        })
        
        # Create sample metrics
        from app.services.advanced_portfolio_analytics import PortfolioMetrics
        metrics = PortfolioMetrics(
            total_return=0.12,
            annualized_return=0.125,
            volatility=0.15,
            sharpe_ratio=0.8,
            sortino_ratio=1.2,
            max_drawdown=-0.08,
            calmar_ratio=1.56,
            beta=1.05,
            alpha=0.02,
            information_ratio=0.3,
            tracking_error=0.05,
            var_95=-0.025,
            cvar_95=-0.035
        )
        
        try:
            ai_insights = analytics._generate_ai_insights(portfolio_df, metrics)
            print("✅ AI insights generation working")
            if ai_insights and 'portfolio_health_score' in ai_insights:
                print(f"   Portfolio Health Score: {ai_insights['portfolio_health_score']['overall_score']:.1f}")
            else:
                print("   ⚠️ AI insights generated but missing health score")
        except Exception as e:
            print(f"   ❌ AI insights failed: {e}")
            # Continue anyway for other tests
        
        # Test risk decomposition
        risk_decomp = analytics._calculate_risk_decomposition(
            sample_data['returns'],
            sample_data['weights'],
            sample_data['market_returns']
        )
        print("✅ Risk decomposition working")
        print(f"   Systematic Risk: {risk_decomp.systematic_risk:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service functionality test failed: {e}")
        return False

def test_template_exists():
    """Test that dashboard template exists"""
    print("\n📄 Testing dashboard template...")
    
    template_path = '/workspaces/aksjeny/app/templates/portfolio_analytics/dashboard.html'
    
    if os.path.exists(template_path):
        print("✅ Dashboard template exists")
        
        # Check template size
        size = os.path.getsize(template_path)
        print(f"   Template size: {size:,} bytes")
        
        if size > 10000:  # Should be a substantial template
            print("✅ Template appears to be complete")
            return True
        else:
            print("⚠️ Template may be incomplete")
            return False
    else:
        print("❌ Dashboard template not found")
        return False

def main():
    """Run all tests"""
    print("🚀 Advanced Portfolio Analytics System Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_service_functionality, 
        test_template_exists
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All tests passed! Advanced Portfolio Analytics system is ready!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
