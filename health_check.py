#!/usr/bin/env python3
"""
Simple health check script for Railway deployment
"""

import requests
import sys
import time
import os

def check_health():
    """Check if the application is healthy"""
    max_retries = 5
    retry_delay = 2
    
    port = os.getenv('PORT', '5000')
    health_url = f"http://localhost:{port}/health/ready"
    
    print(f"Checking health at {health_url}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Health check passed (attempt {attempt + 1})")
                return True
            else:
                print(f"❌ Health check failed with status {response.status_code} (attempt {attempt + 1})")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Health check failed with error: {e} (attempt {attempt + 1})")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    
    print(f"❌ Health check failed after {max_retries} attempts")
    return False

if __name__ == '__main__':
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)
