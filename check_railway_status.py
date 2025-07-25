#!/usr/bin/env python3
"""
Check Railway deployment status and test the deployed application
"""
import requests
import time
import sys

# Railway environment URL (replace with your actual deployment URL)
RAILWAY_URL = "https://aksjeny-production.up.railway.app"

def check_deployment_status():
    """Check if Railway deployment is working"""
    print("🚀 Checking Railway deployment status...")
    
    try:
        # Test the health endpoint
        response = requests.get(f"{RAILWAY_URL}/health/", timeout=30)
        print(f"✅ Health check response: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
        
        # Test the main page
        response = requests.get(RAILWAY_URL, timeout=30)
        print(f"✅ Main page response: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 Railway deployment is working successfully!")
            return True
        else:
            print(f"❌ Railway deployment returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Railway deployment might still be starting")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out - Railway deployment might be slow")
        return False
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")
        return False

def wait_for_deployment(max_attempts=10):
    """Wait for deployment to be ready"""
    for attempt in range(max_attempts):
        print(f"\n📡 Attempt {attempt + 1}/{max_attempts}")
        if check_deployment_status():
            return True
        print("⏰ Waiting 30 seconds before next check...")
        time.sleep(30)
    
    print("❌ Deployment not ready after all attempts")
    return False

if __name__ == "__main__":
    print("🔍 Railway Deployment Status Checker")
    print("=" * 50)
    
    if wait_for_deployment():
        print("\n🎉 SUCCESS: Railway deployment is working!")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Railway deployment is not responding")
        sys.exit(1)
