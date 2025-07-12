#!/usr/bin/env python3
"""
Test script to specifically check BTC-USD details endpoint
"""
import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

from app import create_app
from flask import url_for
import requests

def test_btc_usd_details():
    """Test the BTC-USD details endpoint"""
    app = create_app()
    
    with app.test_client() as client:
        print("Testing BTC-USD details endpoint...")
        
        # Test the endpoint
        response = client.get('/stocks/details/BTC-USD')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ BTC-USD details page loads successfully")
            content = response.get_data(as_text=True)
            
            # Check for specific content
            if "BTC-USD" in content:
                print("✅ BTC-USD ticker found in content")
            else:
                print("❌ BTC-USD ticker not found in content")
                
            if "Bitcoin USD" in content or "Bitcoin" in content:
                print("✅ Bitcoin name found in content")
            else:
                print("❌ Bitcoin name not found in content")
                
            # Check for error messages
            if "Error" in content or "error" in content:
                print("⚠️  Error message detected in content")
                # Find and print error context
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'error' in line.lower() or 'Error' in line:
                        print(f"Error context: {line.strip()}")
                        
            # Check for fallback data indicators
            if "N/A" in content:
                print("ℹ️  Fallback data (N/A) detected - this is expected for crypto")
                
        else:
            print(f"❌ Failed to load BTC-USD details page: {response.status_code}")
            if response.status_code == 500:
                print("Server error - checking for exceptions...")
                
        # Test ETH-USD as well
        print("\nTesting ETH-USD details endpoint...")
        response = client.get('/stocks/details/ETH-USD')
        print(f"ETH-USD Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ ETH-USD details page also loads successfully")
        else:
            print(f"❌ ETH-USD failed: {response.status_code}")

if __name__ == "__main__":
    test_btc_usd_details()
