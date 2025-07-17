#!/usr/bin/env python3
"""
Quick API endpoint test script
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

try:
    from app import create_app
    from app.services.data_service import DataService
    
    print("Testing Flask app creation...")
    app = create_app('testing')
    print("✅ Flask app created successfully")
    
    print("\nTesting DataService methods...")
    
    # Test get_oslo_stocks
    try:
        oslo_stocks = DataService.get_oslo_stocks()
        print(f"✅ get_oslo_stocks: {len(oslo_stocks)} stocks")
    except Exception as e:
        print(f"❌ get_oslo_stocks failed: {e}")
    
    # Test get_global_stocks
    try:
        global_stocks = DataService.get_global_stocks()
        print(f"✅ get_global_stocks: {len(global_stocks)} stocks")
    except Exception as e:
        print(f"❌ get_global_stocks failed: {e}")
    
    # Test get_crypto_data
    try:
        crypto_data = DataService.get_crypto_data()
        print(f"✅ get_crypto_data: {len(crypto_data)} cryptocurrencies")
    except Exception as e:
        print(f"❌ get_crypto_data failed: {e}")
    
    # Test get_global_indices
    try:
        indices = DataService.get_global_indices()
        print(f"✅ get_global_indices: {len(indices)} indices")
    except Exception as e:
        print(f"❌ get_global_indices failed: {e}")
    
    print("\n✅ All basic tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
