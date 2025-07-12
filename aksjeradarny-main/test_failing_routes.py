#!/usr/bin/env python3
"""
Simple endpoint test for Aksjeradar - focused on failing routes
"""
import requests
import time
import subprocess
import signal
import sys
from threading import Thread
import os

def start_server():
    """Start the Flask server"""
    os.chdir("/workspaces/aksjeradarv6")
    subprocess.run([sys.executable, "run.py"])

def test_failing_routes():
    """Test the routes that were failing"""
    base_url = "http://localhost:5000"
    
    failing_routes = [
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
    
    print("🧪 TESTING PREVIOUSLY FAILING ROUTES")
    print("====================================")
    
    passed = 0
    failed = 0
    
    for route in failing_routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {route} - FIXED! ({response.status_code})")
                passed += 1
            else:
                print(f"❌ {route} - Still failing ({response.status_code})")
                failed += 1
        except Exception as e:
            print(f"❌ {route} - ERROR ({e})")
            failed += 1
    
    print(f"\n📊 RESULTS:")
    print(f"✅ Fixed: {passed}")
    print(f"❌ Still failing: {failed}")
    print(f"📈 Improvement: {passed}/{len(failing_routes)} routes now work")
    
    return passed, failed

if __name__ == "__main__":
    # Start server in background
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test routes
    try:
        passed, failed = test_failing_routes()
        
        if failed == 0:
            print("🎉 ALL PREVIOUSLY FAILING ROUTES NOW WORK!")
            sys.exit(0)
        else:
            print(f"⚠️ {failed} routes still need work")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        sys.exit(1)
