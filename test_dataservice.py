#!/usr/bin/env python3
"""
Quick test script to verify DataService methods are working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.data_service import DataService

def test_dataservice_methods():
    print("Testing DataService methods...")
    
    # Test Oslo Børs overview
    print("\n1. Testing get_oslo_bors_overview():")
    oslo_stocks = DataService.get_oslo_bors_overview()
    print(f"   Type: {type(oslo_stocks)}")
    print(f"   Length: {len(oslo_stocks) if oslo_stocks else 0}")
    if oslo_stocks:
        print(f"   First 3 tickers: {list(oslo_stocks.keys())[:3]}")
        first_ticker = list(oslo_stocks.keys())[0]
        print(f"   Sample data for {first_ticker}: {oslo_stocks[first_ticker]}")
    
    # Test Global stocks overview  
    print("\n2. Testing get_global_stocks_overview():")
    global_stocks = DataService.get_global_stocks_overview()
    print(f"   Type: {type(global_stocks)}")
    print(f"   Length: {len(global_stocks) if global_stocks else 0}")
    if global_stocks:
        print(f"   First 3 tickers: {list(global_stocks.keys())[:3]}")
    
    # Test Crypto overview
    print("\n3. Testing get_crypto_overview():")
    crypto_data = DataService.get_crypto_overview()
    print(f"   Type: {type(crypto_data)}")
    print(f"   Length: {len(crypto_data) if crypto_data else 0}")
    if crypto_data:
        print(f"   Crypto tickers: {list(crypto_data.keys())}")
        if 'BTC-USD' in crypto_data:
            print(f"   BTC-USD data: {crypto_data['BTC-USD']}")
    
    # Test Currency overview
    print("\n4. Testing get_currency_overview():")
    try:
        currency_data = DataService.get_currency_overview()
        print(f"   Type: {type(currency_data)}")
        print(f"   Length: {len(currency_data) if currency_data else 0}")
        if currency_data:
            print(f"   First 3 currencies: {list(currency_data.keys())[:3]}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_dataservice_methods()
