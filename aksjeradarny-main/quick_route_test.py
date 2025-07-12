#!/usr/bin/env python3
"""
Quick route test for Aksjeradar
"""
import requests
import time
import subprocess
import sys
from threading import Thread

def start_server():
    """Start the Flask server"""
    subprocess.run([sys.executable, "run.py"], cwd="/workspaces/aksjeradarv6")

def test_routes():
    """Test key routes"""
    base_url = "http://localhost:5000"
    
    routes_to_test = [
        "/",
        "/demo", 
        "/ai-explained",
        "/portfolio/advanced/",
        "/blog/",
        "/investment-guides/",
        "/pricing/",
        "/api/stocks/search",
        "/api/market-data"
    ]
    
    time.sleep(3)  # Give server time to start
    
    print("🧪 QUICK ROUTE TEST")
    print("==================")
    
    passed = 0
    failed = 0
    
    for route in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {route} - OK ({response.status_code})")
                passed += 1
            else:
                print(f"❌ {route} - FAIL ({response.status_code})")
                failed += 1
        except Exception as e:
            print(f"❌ {route} - ERROR ({e})")
            failed += 1
    
    print(f"\n📊 RESULTS: {passed} passed, {failed} failed")
    return passed, failed

if __name__ == "__main__":
    # Start server in background
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test routes
    passed, failed = test_routes()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"⚠️ {failed} TESTS FAILED")
        sys.exit(1)
