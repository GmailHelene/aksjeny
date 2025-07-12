#!/usr/bin/env python3
"""
Enhanced Market Intel Routes Test
Tests all market intel endpoints and content.
"""

import requests
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_all_market_intel_routes():
    app = create_app()
    
    market_intel_routes = [
        "/market-intel/",
        "/market-intel/insider-trading",
        "/market-intel/insider-trading?ticker=EQNR.OL",
        "/market-intel/earnings-calendar",
        "/market-intel/sector-analysis",
        "/market-intel/economic-indicators"
    ]
    
    print("🔍 Testing All Market Intel Routes")
    print("=" * 40)
    
    with app.test_client() as client:
        for route in market_intel_routes:
            print(f"\n📋 Testing: {route}")
            print(f"🔗 Route: {route}")
            
            try:
                response = client.get(route)
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    # Check for common template errors
                    content = response.get_data(as_text=True)
                    if "Error" in content or "Exception" in content:
                        print("⚠️  WARNING: Error detected in response content")
                        # Print first 500 chars of content for debugging
                        print(f"Content preview: {content[:500]}...")
                    else:
                        print("✅ SUCCESS")
                elif response.status_code == 404:
                    print("❌ NOT FOUND")
                else:
                    print(f"⚠️  WARNING: Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_all_market_intel_routes()
