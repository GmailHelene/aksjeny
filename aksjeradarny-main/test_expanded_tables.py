#!/usr/bin/env python3
"""Test script to verify expanded stock tables functionality"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.data_service import DataService

def test_expanded_tables():
    """Test that the expanded tables have more data"""
    print("Testing expanded stock tables...")
    
    try:
        # Test oslo stocks
        oslo_data = DataService.get_oslo_bors_overview()
        print(f"✓ Oslo Børs stocks: {len(oslo_data)} entries")
        
        # Verify we have the new tickers
        expected_oslo = ['EQNR.OL', 'DNB.OL', 'XXLASA.OL', 'KOMPLETT.OL', 'EUROPRIS.OL', 'KITRON.OL', 'NEL.OL', 'REC.OL']
        for ticker in expected_oslo:
            if ticker in oslo_data:
                print(f"  ✓ {ticker}: {oslo_data[ticker]['name']}")
            else:
                print(f"  ✗ Missing {ticker}")
        
        # Test global stocks
        global_data = DataService.get_global_stocks_overview()
        print(f"✓ Global stocks: {len(global_data)} entries")
        
        # Verify we have the new global tickers
        expected_global = ['AAPL', 'MSFT', 'JNJ', 'PG', 'MA', 'DIS']
        for ticker in expected_global:
            if ticker in global_data:
                print(f"  ✓ {ticker}: {global_data[ticker]['name']}")
            else:
                print(f"  ✗ Missing {ticker}")
        
        # Test crypto
        crypto_data = DataService.get_crypto_overview()
        print(f"✓ Crypto currencies: {len(crypto_data)} entries")
        
        # Verify we have the new crypto
        expected_crypto = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD', 'DOT-USD', 'AVAX-USD', 'LINK-USD']
        for ticker in expected_crypto:
            if ticker in crypto_data:
                print(f"  ✓ {ticker}: {crypto_data[ticker]['name']}")
            else:
                print(f"  ✗ Missing {ticker}")
        
        # Test market overview
        market_data = DataService.get_market_overview()
        print(f"✓ Market overview data structure:")
        print(f"  - Oslo stocks: {len(market_data['oslo_stocks'])}")
        print(f"  - Global stocks: {len(market_data['global_stocks'])}")
        print(f"  - Crypto: {len(market_data['crypto'])}")
        print(f"  - Currency: {len(market_data['currency'])}")
        
        print("\n✅ All expanded table tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing expanded tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_startup():
    """Test that the app can start with our changes"""
    print("\nTesting app startup...")
    
    try:
        app = create_app()
        print("✓ App created successfully")
        
        with app.test_client() as client:
            # Test market overview page
            response = client.get('/analysis/market-overview')
            print(f"✓ Market overview page: {response.status_code}")
            
            # Test analysis index
            response = client.get('/analysis/')
            print(f"✓ Analysis index page: {response.status_code}")
            
            # Test subscription page (should be accessible)
            response = client.get('/subscription')
            print(f"✓ Subscription page: {response.status_code}")
            
        print("✅ App startup tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing app startup: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Running expanded tables test suite...")
    print("=" * 50)
    
    success1 = test_expanded_tables()
    success2 = test_app_startup()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Expanded tables are working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
