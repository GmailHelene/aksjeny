#!/usr/bin/env python3
"""Test endpoints directly with detailed error info"""
import requests
import time
import subprocess
import sys
from threading import Thread
import os

def start_server():
    """Start Flask server"""
    os.chdir("/workspaces/aksjeradarv6")
    subprocess.run([sys.executable, "run.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def test_endpoint_details():
    """Test endpoints and show detailed error info"""
    time.sleep(3)  # Wait for server start
    
    routes = ["/demo", "/ai-explained", "/pricing/"]
    
    for route in routes:
        try:
            response = requests.get(f"http://localhost:5000{route}", timeout=5)
            print(f"\n🔍 {route}:")
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            if response.status_code != 200:
                print(f"   Content: {response.text[:200]}...")
            else:
                print(f"   Content length: {len(response.text)} bytes")
        except Exception as e:
            print(f"\n❌ {route}: {e}")

if __name__ == "__main__":
    # Start server
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    test_endpoint_details()
