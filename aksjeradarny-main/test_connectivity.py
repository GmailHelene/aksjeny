#!/usr/bin/env python3
"""
Simple connectivity test to check if Flask app is running
"""

import requests
import sys

def test_connectivity():
    print("Testing Flask app connectivity...")
    
    urls_to_test = [
        "http://localhost:5000",
        "http://localhost:5001", 
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5001"
    ]
    
    for url in urls_to_test:
        try:
            print(f"Trying {url}...")
            response = requests.get(f"{url}/", timeout=3)
            if response.status_code == 200:
                print(f"✅ Flask app is running on {url}")
                return url
            else:
                print(f"❌ {url} returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {url}")
        except Exception as e:
            print(f"❌ Error with {url}: {str(e)}")
    
    print("\n❌ Flask app is not running on any common ports")
    print("To start the Flask app, run: python run.py")
    return None

if __name__ == "__main__":
    result = test_connectivity()
    sys.exit(0 if result else 1)
