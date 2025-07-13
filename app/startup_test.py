#!/usr/bin/env python3
"""
Aksjeradar Application Startup Test
Verifies that the application can start and serve requests
"""
import os
import sys
import time
import requests
import threading
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class Color:
    """Terminal color codes for pretty output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a formatted header"""
    print(f"\n{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{message.center(80)}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}\n")

def print_section(message):
    """Print a formatted section header"""
    print(f"\n{Color.BLUE}{Color.BOLD}{'-' * 80}{Color.ENDC}")
    print(f"{Color.BLUE}{Color.BOLD}{message}{Color.ENDC}")
    print(f"{Color.BLUE}{Color.BOLD}{'-' * 80}{Color.ENDC}\n")

def print_result(name, success, message=""):
    """Print a test result"""
    if success:
        result = f"{Color.GREEN}✓ PASS{Color.ENDC}"
    else:
        result = f"{Color.RED}✗ FAIL{Color.ENDC}"
    
    print(f"{result} - {name}")
    if message:
        print(f"     {message}")
    return success

def run_flask_app(port=5000):
    """Run the Flask app in a separate thread"""
    from app import create_app
    app = create_app('development')
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def wait_for_server(port=5000, max_attempts=5):
    """Wait for the server to be ready"""
    url = f"http://localhost:{port}/"
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            if response.status_code in (200, 301, 302):
                return True
        except requests.RequestException:
            pass
        
        time.sleep(1)
    
    return False

def run_startup_test():
    """Run the startup test"""
    print_header("Aksjeradar Application Startup Test")
    
    # Start the Flask app in a separate thread
    port = 5001  # Use a different port to avoid conflicts
    app_thread = threading.Thread(target=run_flask_app, args=(port,))
    app_thread.daemon = True
    
    try:
        print_section("Starting Flask Application")
        app_thread.start()
        
        # Wait for the server to be ready
        if wait_for_server(port=port):
            print_result("Server Startup", True, "Server is running and responding to requests")
        else:
            print_result("Server Startup", False, "Server failed to start or is not responding")
            return False
        
        # Try to access a few key endpoints
        print_section("Testing Key Endpoints")
        
        endpoints = [
            ('Home Page', '/'),
            ('Login Page', '/login'),
            ('Register Page', '/register'),
            ('Demo Page', '/demo')
        ]
        
        success_count = 0
        for name, endpoint in endpoints:
            url = f"http://localhost:{port}{endpoint}"
            try:
                response = requests.get(url)
                if response.status_code in (200, 301, 302):
                    print_result(name, True, f"Status: {response.status_code}")
                    success_count += 1
                else:
                    print_result(name, False, f"Status: {response.status_code}")
            except requests.RequestException as e:
                print_result(name, False, f"Error: {str(e)}")
        
        overall_success = success_count == len(endpoints)
        print_section("Test Results")
        print_result("Overall Test", overall_success, 
                     f"Successfully accessed {success_count} out of {len(endpoints)} endpoints")
        
        return overall_success
    
    except Exception as e:
        print_result("Startup Test", False, f"Error: {str(e)}")
        return False
    finally:
        # No need to stop the thread, it will be terminated when the script exits
        pass

if __name__ == "__main__":
    success = run_startup_test()
    sys.exit(0 if success else 1)
