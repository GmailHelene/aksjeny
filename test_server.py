import subprocess
import time
import requests
import os

def check_if_server_running():
    """Check if server is already running"""
    try:
        response = requests.get('http://localhost:5000', timeout=2)
        print("✅ Server is already running!")
        return True
    except:
        print("❌ Server is not running")
        return False

def start_minimal_server():
    """Start a minimal Flask server for testing"""
    print("🚀 Starting minimal test server...")
    
    # Create a simple test server
    test_server_code = '''
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Server is working!</h1><p>Go to <a href='/test-reset'>Test Reset</a></p>"

@app.route('/test-reset')
def test_reset():
    return "<h1>Reset page works!</h1><p>Server is running correctly</p>"

if __name__ == '__main__':
    print("🌐 Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
    
    # Write test server to file
    with open('test_server_minimal.py', 'w') as f:
        f.write(test_server_code)
    
    print("📝 Created test server file")
    print("🚀 Starting server...")
    print("📍 Test URL: http://localhost:5000")
    print("📍 Reset test: http://localhost:5000/test-reset")
    print("\nPress Ctrl+C to stop")
    
    try:
        subprocess.run(['python3', 'test_server_minimal.py'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    if not check_if_server_running():
        start_minimal_server()
    else:
        print("🌐 Visit: http://localhost:5000")
