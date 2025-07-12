#!/usr/bin/env python3
"""
Detailed Market Intel Content Test
Tests content quality and detects actual errors.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_market_intel_content():
    app = create_app()
    
    routes = [
        ("/market-intel/", "Market Intel Index"),
        ("/market-intel/insider-trading", "Insider Trading"),
        ("/market-intel/earnings-calendar", "Earnings Calendar"),
        ("/market-intel/sector-analysis", "Sector Analysis"),
        ("/market-intel/economic-indicators", "Economic Indicators")
    ]
    
    print("🔍 Detailed Market Intel Content Analysis")
    print("=" * 50)
    
    with app.test_client() as client:
        for route, name in routes:
            print(f"\n📋 Testing: {name}")
            print(f"🔗 Route: {route}")
            
            try:
                response = client.get(route)
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    
                    # Check for actual errors vs normal content
                    error_patterns = [
                        "Internal Server Error",
                        "500 Error",
                        "Template Error",
                        "Jinja2",
                        "NameError",
                        "AttributeError",
                        "TypeError"
                    ]
                    
                    found_errors = []
                    for pattern in error_patterns:
                        if pattern in content:
                            found_errors.append(pattern)
                    
                    if found_errors:
                        print(f"❌ REAL ERRORS FOUND: {', '.join(found_errors)}")
                        # Show error context
                        for error in found_errors:
                            start = content.find(error)
                            if start != -1:
                                context = content[max(0, start-100):start+200]
                                print(f"Error context: ...{context}...")
                    else:
                        # Check for expected content
                        if "container" in content and ("card" in content or "row" in content):
                            print("✅ SUCCESS - Valid HTML structure")
                        else:
                            print("⚠️  WARNING - Minimal content")
                            
                else:
                    print(f"❌ HTTP ERROR: Status {response.status_code}")
                    
            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_market_intel_content()
