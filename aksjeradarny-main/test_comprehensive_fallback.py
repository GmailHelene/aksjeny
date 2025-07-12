#!/usr/bin/env python3
"""
Comprehensive test for EQNR.OL and other tickers fallback logic
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_comprehensive_fallback():
    print("=" * 60)
    print("COMPREHENSIVE FALLBACK TESTING")
    print("=" * 60)
    
    from app.services.data_service import DataService
    from app.services.analysis_service import AnalysisService
    
    # Test tickers
    test_tickers = ['EQNR.OL', 'DNB.OL', 'AAPL', 'MSFT', 'UNKNOWN.OL', 'UNKNOWN']
    
    for ticker in test_tickers:
        print(f"\n--- Testing {ticker} ---")
        
        # Test 1: get_stock_info
        try:
            stock_info = DataService.get_stock_info(ticker)
            if stock_info:
                print(f"✓ get_stock_info: Success - {stock_info.get('shortName', 'N/A')} @ {stock_info.get('regularMarketPrice', 'N/A')}")
            else:
                print(f"✗ get_stock_info: No data")
        except Exception as e:
            print(f"✗ get_stock_info: Error - {e}")
        
        # Test 2: get_stock_data
        try:
            stock_data = DataService.get_stock_data(ticker, period='1d')
            if hasattr(stock_data, 'empty') and not stock_data.empty:
                print(f"✓ get_stock_data: Success - {stock_data.shape} rows, last close: {stock_data['Close'].iloc[-1]:.2f}")
            else:
                print(f"✗ get_stock_data: No data or empty")
        except Exception as e:
            print(f"✗ get_stock_data: Error - {e}")
        
        # Test 3: get_technical_analysis
        try:
            tech_analysis = AnalysisService.get_technical_analysis(ticker)
            if tech_analysis:
                print(f"✓ get_technical_analysis: Success - Signal: {tech_analysis.get('overall_signal', 'N/A')}, RSI: {tech_analysis.get('rsi', 'N/A')}")
            else:
                print(f"✗ get_technical_analysis: No data")
        except Exception as e:
            print(f"✗ get_technical_analysis: Error - {e}")
    
    # Test 4: Market overview data
    print(f"\n--- Testing Market Overview ---")
    try:
        oslo_stocks = DataService.get_oslo_bors_overview()
        if 'EQNR.OL' in oslo_stocks:
            eqnr_data = oslo_stocks['EQNR.OL']
            print(f"✓ Oslo stocks overview: EQNR.OL found - {eqnr_data.get('name', 'N/A')} @ {eqnr_data.get('last_price', 'N/A')}")
        else:
            print(f"✗ Oslo stocks overview: EQNR.OL not found")
            
        global_stocks = DataService.get_global_stocks_overview()
        if 'AAPL' in global_stocks:
            aapl_data = global_stocks['AAPL']
            print(f"✓ Global stocks overview: AAPL found - {aapl_data.get('name', 'N/A')} @ {aapl_data.get('last_price', 'N/A')}")
        else:
            print(f"✗ Global stocks overview: AAPL not found")
    except Exception as e:
        print(f"✗ Market overview: Error - {e}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_comprehensive_fallback()
