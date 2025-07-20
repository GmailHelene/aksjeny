#!/usr/bin/env python3

"""
Test script for checking all navigation links and template functionality
"""

import requests
import sys
from urllib.parse import urljoin

def test_endpoints(base_url="http://localhost:3000"):
    """Test viktiger endpoints for navigasjon"""
    
    endpoints_to_test = [
        # Basic routes
        ("Hjem", "/"),
        ("Login", "/login"),
        ("Nyheter", "/news/"),
        
        # Demo routes (should work without login)
        ("Demo", "/demo"),
        ("Demo Stocks", "/demo/stocks"),
        ("Demo Portfolio", "/demo/portfolio"),
        ("Demo Analysis", "/demo/analysis"),
        
        # Pricing
        ("Pricing", "/pricing/"),
        
        # Authenticated routes (will redirect if not logged in)
        ("Stocks Index", "/stocks/"),
        ("Oslo Børs", "/stocks/list/oslo"),
        ("Global Stocks", "/stocks/list/global"),
        ("Crypto", "/stocks/list/crypto"),
        ("Currency", "/stocks/list/currency"),
        ("Stock Search", "/stocks/search"),
        
        # Analysis routes
        ("Analysis Index", "/analysis/"),
        ("Technical Analysis", "/analysis/technical"),
        ("Warren Buffett", "/analysis/warren-buffett"),
        ("Benjamin Graham", "/analysis/benjamin-graham"),
        ("Market Overview", "/analysis/market-overview"),
        ("Currency Overview", "/analysis/currency-overview"),
        ("AI Analysis", "/analysis/ai"),
        ("Sentiment", "/analysis/sentiment"),
        ("Screener", "/analysis/screener"),
        
        # Portfolio routes
        ("Portfolio Overview", "/portfolio/overview"),
        ("Watchlist", "/portfolio/watchlist"),
        
        # Other
        ("Financial Dashboard", "/financial-dashboard"),
        ("Profile", "/profile/"),
        ("Settings", "/settings"),
    ]
    
    print(f"Testing {len(endpoints_to_test)} endpoints...")
    print("=" * 60)
    
    results = []
    
    for name, endpoint in endpoints_to_test:
        url = urljoin(base_url, endpoint)
        try:
            response = requests.get(url, timeout=10, allow_redirects=False)
            status = response.status_code
            
            if status == 200:
                result = "✅ OK"
            elif status == 302:
                result = f"🔄 REDIRECT (til {response.headers.get('Location', 'unknown')})"
            elif status == 404:
                result = "❌ NOT FOUND"
            elif status == 500:
                result = "💥 SERVER ERROR"
            else:
                result = f"⚠️  STATUS {status}"
                
            print(f"{name:<25} {endpoint:<30} {result}")
            results.append((name, endpoint, status))
            
        except requests.exceptions.Timeout:
            print(f"{name:<25} {endpoint:<30} ⏱️  TIMEOUT")
            results.append((name, endpoint, "TIMEOUT"))
        except requests.exceptions.ConnectionError:
            print(f"{name:<25} {endpoint:<30} 🔌 CONNECTION ERROR")
            results.append((name, endpoint, "CONNECTION_ERROR"))
        except Exception as e:
            print(f"{name:<25} {endpoint:<30} 💥 ERROR: {e}")
            results.append((name, endpoint, f"ERROR: {e}"))
    
    print("=" * 60)
    
    # Sammendrag
    ok_count = sum(1 for _, _, status in results if status == 200)
    redirect_count = sum(1 for _, _, status in results if status == 302)
    not_found_count = sum(1 for _, _, status in results if status == 404)
    error_count = sum(1 for _, _, status in results if isinstance(status, int) and status >= 500)
    
    print(f"\n📊 SAMMENDRAG:")
    print(f"✅ OK (200): {ok_count}")
    print(f"🔄 Redirects (302): {redirect_count}")
    print(f"❌ Not Found (404): {not_found_count}")
    print(f"💥 Server Errors (5xx): {error_count}")
    
    return results

if __name__ == "__main__":
    test_endpoints()
