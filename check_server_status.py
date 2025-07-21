import requests
import subprocess
import sys
import os

def check_server():
    """Check if Flask server is running"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        print("✅ Server is running!")
        print(f"Status code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def start_server_if_needed():
    """Start server if it's not running"""
    if not check_server():
        print("\n🚀 Starting Flask server...")
        
        # Set environment variables
        os.environ.setdefault('EMAIL_USERNAME', 'support@luxushair.com')
        os.environ.setdefault('EMAIL_PASSWORD', 'suetozoydejwntii')
        os.environ.setdefault('EMAIL_PORT', '587')
        os.environ.setdefault('EMAIL_SERVER', 'imap.gmail.com')
        os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway')
        
        try:
            # Start server in background
            subprocess.Popen([sys.executable, 'app.py'])
            print("✅ Server started!")
            print("🌐 Available at: http://localhost:5000")
        except Exception as e:
            print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    print("🔍 Checking server status...")
    start_server_if_needed()
