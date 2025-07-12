#!/usr/bin/env python3
"""
Simple test for EQNR.OL data
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    from app.services.data_service import FALLBACK_STOCK_INFO
    print("EQNR.OL in FALLBACK_STOCK_INFO:", 'EQNR.OL' in FALLBACK_STOCK_INFO)
    
    if 'EQNR.OL' in FALLBACK_STOCK_INFO:
        print("EQNR.OL data:", FALLBACK_STOCK_INFO['EQNR.OL'])
    
    # Test the get_stock_info function
    from app.services.data_service import DataService
    print("\nTesting get_stock_info...")
    result = DataService.get_stock_info('EQNR.OL')
    print("Result type:", type(result))
    print("Has data:", bool(result))
    if result:
        print("Keys:", list(result.keys())[:10])
        print("shortName:", result.get('shortName', 'N/A'))
        print("regularMarketPrice:", result.get('regularMarketPrice', 'N/A'))
        
except Exception as e:
    print("Error:", e)
    import traceback
    traceback.print_exc()
