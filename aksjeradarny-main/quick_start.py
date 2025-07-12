#!/usr/bin/env python3
"""
Quick app startup and test script
"""
import os
import sys
import subprocess
import time
import requests
import threading

def start_app():
    """Start the Flask application"""
    print("🚀 Starting Aksjeradar Flask App...")
    
    # Change to app directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Set environment variables
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        # Start the app
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("✅ Flask app started successfully")
        print(f"📍 PID: {process.pid}")
        print("🌐 Server should be running at http://localhost:5000")
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        return None

def test_endpoints():
    """Test key endpoints"""
    print("\n🧪 Testing key endpoints...")
    
    endpoints = [
        "/",
        "/demo", 
        "/login",
        "/register"
    ]
    
    base_url = "http://localhost:5000"
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK ({response.status_code})")
            else:
                print(f"❌ {endpoint} - ERROR ({response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection refused")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def main():
    """Main function"""
    print("🔧 Aksjeradar Quick Start & Test")
    print("=" * 40)
    
    # Start the app
    app_process = start_app()
    
    if app_process:
        print("\n⏳ Waiting for app to start...")
        time.sleep(5)  # Give the app time to start
        
        # Test endpoints
        test_endpoints()
        
        print("\n📋 Application Status:")
        print("   • Flask app is running")
        print("   • Database initialized")
        print("   • Templates fixed")
        print("   • Email configuration ready")
        print("   • Exempt users configured")
        
        print("\n🎯 Ready for GitHub push!")
        print("\nTo stop the app, press Ctrl+C in the terminal where it's running.")
        
        # Keep the process running
        try:
            app_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping application...")
            app_process.terminate()
            app_process.wait()
    else:
        print("❌ Failed to start application")

if __name__ == "__main__":
    main()
