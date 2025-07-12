#!/usr/bin/env python3
"""
Test script for EQNR.OL data retrieval and fallback logic
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.data_service import DataService, FALLBACK_OSLO_DATA, FALLBACK_STOCK_INFO
from app.services.analysis_service import AnalysisService
import json

def test_eqnr_data():
    print("=" * 60)
    print("TESTING EQNR.OL DATA RETRIEVAL")
    print("=" * 60)
    
    # Test 1: Check if EQNR.OL is in fallback data
    print("\n1. Checking fallback data availability:")
    print(f"   EQNR.OL in FALLBACK_OSLO_DATA: {'EQNR.OL' in FALLBACK_OSLO_DATA}")
    print(f"   EQNR.OL in FALLBACK_STOCK_INFO: {'EQNR.OL' in FALLBACK_STOCK_INFO}")
    
    if 'EQNR.OL' in FALLBACK_OSLO_DATA:
        print(f"   FALLBACK_OSLO_DATA['EQNR.OL']: {FALLBACK_OSLO_DATA['EQNR.OL']}")
    
    # Test 2: Test get_stock_info method
    print("\n2. Testing get_stock_info('EQNR.OL'):")
    try:
        stock_info = DataService.get_stock_info('EQNR.OL')
        if stock_info:
            print(f"   Success! Got {len(stock_info)} fields")
            print(f"   ticker: {stock_info.get('ticker', 'N/A')}")
            print(f"   shortName: {stock_info.get('shortName', 'N/A')}")
            print(f"   regularMarketPrice: {stock_info.get('regularMarketPrice', 'N/A')}")
            print(f"   sector: {stock_info.get('sector', 'N/A')}")
        else:
            print("   Failed! No data returned")
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test get_oslo_stocks_overview
    print("\n3. Testing get_oslo_stocks_overview():")
    try:
        oslo_data = DataService.get_oslo_stocks_overview()
        if oslo_data and 'EQNR.OL' in oslo_data:
            print(f"   Success! EQNR.OL found in oslo data")
            print(f"   EQNR.OL data: {oslo_data['EQNR.OL']}")
        else:
            print(f"   EQNR.OL not found in oslo data. Available tickers: {list(oslo_data.keys())[:10]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Test technical analysis fallback
    print("\n4. Testing technical analysis fallback:")
    try:
        tech_data = AnalysisService.get_fallback_technical_data('EQNR.OL')
        if tech_data:
            print(f"   Success! Got technical data")
            print(f"   last_price: {tech_data.get('last_price', 'N/A')}")
            print(f"   signal: {tech_data.get('signal', 'N/A')}")
            print(f"   rsi: {tech_data.get('rsi', 'N/A')}")
        else:
            print("   No technical data available")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Test stock data retrieval (yfinance)
    print("\n5. Testing get_stock_data('EQNR.OL'):")
    try:
        stock_data = DataService.get_stock_data('EQNR.OL', period='1d')
        if hasattr(stock_data, 'empty') and not stock_data.empty:
            print(f"   Success! Got stock data with shape: {stock_data.shape}")
            print(f"   Columns: {list(stock_data.columns)}")
            print(f"   Last close price: {stock_data['Close'].iloc[-1]:.2f}")
        else:
            print("   No live stock data available or empty dataset")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_eqnr_data()
