#!/usr/bin/env python3
"""
Test spesifikke funksjoner i appen
"""
import requests
import time

def test_endpoints():
    """Test hovedendepunkter"""
    base_url = "http://localhost:5000"
    
    endpoints = [
        "/",
        "/health/",
        "/stocks/",
        "/analysis/",
        "/login",
        "/register",
        "/api/health"
    ]
    
    print("🧪 TESTING ENDPOINTS")
    print("=" * 30)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code in [200, 302] else "❌"
            print(f"{status} {endpoint} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - ERROR: {e}")
    
    print("\n🎯 MANUAL TEST URLs:")
    for endpoint in endpoints:
        print(f"• {base_url}{endpoint}")

if __name__ == '__main__':
    print("⏰ Waiting 3 seconds for server to start...")
    time.sleep(3)
    test_endpoints()
