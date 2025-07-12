#!/usr/bin/env python3
"""
Test script to verify that analysis limits are properly enforced
"""

import requests
import subprocess
import time
import signal
import os
from datetime import datetime

def start_flask_app():
    """Start Flask app in background"""
    print("Starting Flask app...")
    process = subprocess.Popen(
        ['python', 'app.py'],
        cwd='/workspaces/aksjeradarv6',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(3)
    
    return process

def test_analysis_limits():
    """Test that analysis limits are enforced for free users"""
    try:
        print("\n=== Testing Analysis Limit Enforcement ===")
        
        # Create a session to maintain cookies
        session = requests.Session()
        
        # First, test a stock details page (should trigger analysis)
        print("\nTesting stock details page analysis...")
        response = session.get('http://localhost:5000/stocks/details/EQNR.OL')
        print(f"Stock details response: {response.status_code}")
        
        # Test API analysis endpoints
        print("\nTesting API analysis endpoints...")
        
        # Test indicators endpoint
        response = session.get('http://localhost:5000/analysis/api/analysis/indicators?symbol=EQNR.OL')
        print(f"Indicators API response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Indicators API accessible")
        elif response.status_code == 429:
            print("✅ Analysis limit enforced on indicators API")
            data = response.json()
            print(f"   Limit message: {data.get('error', 'No message')}")
        
        # Test signals endpoint  
        response = session.get('http://localhost:5000/analysis/api/analysis/signals?symbol=EQNR.OL')
        print(f"Signals API response: {response.status_code}")
        if response.status_code == 200:
            print("✅ Signals API accessible")
        elif response.status_code == 429:
            print("✅ Analysis limit enforced on signals API")
            data = response.json()
            print(f"   Limit message: {data.get('error', 'No message')}")
        
        # Test multiple requests to trigger limit
        print("\nTesting multiple analysis requests to trigger limit...")
        limit_reached = False
        
        for i in range(8):  # Try 8 requests (should exceed 5-request limit)
            response = session.get(f'http://localhost:5000/analysis/api/analysis/indicators?symbol=EQNR.OL&_test={i}')
            print(f"Request {i+1}: Status {response.status_code}")
            
            if response.status_code == 429:
                print(f"✅ Analysis limit enforced at request {i+1}")
                data = response.json()
                print(f"   Daily limit: {data.get('daily_limit', 'Unknown')}")
                print(f"   Remaining: {data.get('remaining', 'Unknown')}")
                limit_reached = True
                break
            elif response.status_code != 200:
                print(f"❌ Unexpected error at request {i+1}: {response.status_code}")
                break
                
            time.sleep(0.5)  # Small delay between requests
        
        if not limit_reached:
            print("❌ Analysis limit was not enforced - this may indicate an issue")
        
        # Test technical analysis route
        print("\nTesting technical analysis route...")
        response = session.get('http://localhost:5000/analysis/technical?ticker=EQNR.OL')
        print(f"Technical analysis response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Technical analysis accessible")
        elif response.status_code == 302:
            print("✅ Redirected (likely to pricing page due to limit)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing analysis limits: {e}")
        return False

def main():
    """Main test function"""
    process = None
    try:
        # Start Flask app
        process = start_flask_app()
        
        # Test analysis limits
        success = test_analysis_limits()
        
        if success:
            print("\n✅ Analysis limit enforcement test completed")
        else:
            print("\n❌ Analysis limit enforcement test failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        # Clean up
        if process:
            print("\nStopping Flask app...")
            process.terminate()
            process.wait()

if __name__ == "__main__":
    main()
