#!/usr/bin/env python3
"""
Enhanced monitoring script for the improved rate limiting system
"""
import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

from app import create_app
from app.services.rate_limiter import rate_limiter
from app.services.data_service import DataService
import time

def test_enhanced_rate_limiting():
    """Test the enhanced rate limiting with circuit breaker"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Testing Enhanced Rate Limiting System")
        print("=" * 50)
        
        # Test circuit breaker status
        print(f"Circuit Breaker Status: {'OPEN' if rate_limiter.is_circuit_open('yahoo_finance') else 'CLOSED'}")
        
        # Test a few stock requests to see caching in action
        test_tickers = ['EQNR.OL', 'DNB.OL', 'BTC-USD']
        
        for ticker in test_tickers:
            print(f"\n📊 Testing {ticker}...")
            start_time = time.time()
            
            try:
                stock_info = DataService.get_stock_info(ticker)
                end_time = time.time()
                
                if stock_info:
                    print(f"✅ {ticker}: Success in {end_time - start_time:.2f}s")
                    print(f"   Name: {stock_info.get('longName', 'N/A')}")
                    print(f"   Price: {stock_info.get('regularMarketPrice', 'N/A')}")
                else:
                    print(f"❌ {ticker}: No data returned")
                    
            except Exception as e:
                print(f"⚠️  {ticker}: Error - {str(e)}")
        
        print("\n" + "=" * 50)
        print("Enhanced rate limiting test completed!")
        print("Monitor production logs for 429 error reduction.")

if __name__ == "__main__":
    test_enhanced_rate_limiting()
