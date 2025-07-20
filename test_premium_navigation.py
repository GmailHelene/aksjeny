#!/usr/bin/env python3
"""Test navigation som innlogget premium bruker"""

import requests
import time

# Login session
session = requests.Session()

# Login først
login_data = {
    'email': 'helene721@gmail.com',
    'password': 'test123',
    'remember_me': False
}

print("=== LOGGER INN SOM PREMIUM BRUKER ===")
try:
    login_resp = session.post('http://localhost:3000/login', data=login_data, allow_redirects=False)
    if login_resp.status_code in [302, 200]:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_resp.status_code}")
        exit(1)
except Exception as e:
    print(f"💥 Login error: {e}")
    exit(1)

time.sleep(0.5)

# Test endpoints som innlogget bruker
def test_authenticated_endpoint(url, name):
    try:
        r = session.get(url, timeout=5, allow_redirects=False)
        if r.status_code == 200:
            print(f"✅ {name}: OK (200) - Premium innhold tilgjengelig")
        elif r.status_code == 302:
            print(f"🔄 {name}: Redirect (302) - Krever videre autentisering?")
        else:
            print(f"❌ {name}: Error ({r.status_code})")
    except Exception as e:
        print(f"💥 {name}: Exception - {e}")

print("\n=== TESTER PREMIUM NAVIGATION ===")
premium_endpoints = [
    ("http://localhost:3000/portfolio/overview", "Portfolio Overview"),
    ("http://localhost:3000/portfolio/watchlist", "Portfolio Watchlist"), 
    ("http://localhost:3000/analysis/", "Analysis Main"),
    ("http://localhost:3000/analysis/technical", "Technical Analysis"),
    ("http://localhost:3000/stocks/details/EQNR.OL", "Stock Details (EQNR)"),
    ("http://localhost:3000/news/", "News"),
    ("http://localhost:3000/stocks/search", "Stocks Search"),
]

for url, name in premium_endpoints:
    test_authenticated_endpoint(url, name)
    time.sleep(0.1)

print("\n=== PREMIUM USER STATUS ===")
print("Tester om helene721 har tilgang til alle premium funksjoner...")
