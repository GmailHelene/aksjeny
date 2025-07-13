#!/usr/bin/env python3
"""
Simplified Aksjeradar Application Test
Tests if the application can be created and registered routes are working
"""
import os
import sys
from pathlib import Path

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

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

def test_app_creation():
    """Test if the application can be created"""
    print_section("Testing Application Creation")
    
    try:
        # Import create_app function
        from app import create_app
        print_result("Import create_app", True)
    except ImportError as e:
        print_result("Import create_app", False, f"Error: {str(e)}")
        return False
    
    try:
        # Create the application
        app = create_app('testing')
        print_result("Create Application", True)
    except Exception as e:
        print_result("Create Application", False, f"Error: {str(e)}")
        return False
    
    return True

def test_routes(app):
    """Test routes in the application"""
    print_section("Checking Registered Routes")
    
    # Get all registered routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append((rule.endpoint, rule.rule))
    
    print(f"Found {len(routes)} registered routes")
    
    # Check for essential routes
    essential_routes = [
        'static',  # Flask built-in static route
        'main.index',  # Main index page
        'main.login',  # Login page
        'main.register',  # Registration page
    ]
    
    missing_routes = []
    for route in essential_routes:
        found = any(route == endpoint for endpoint, _ in routes)
        print_result(f"Route: {route}", found)
        if not found:
            missing_routes.append(route)
    
    if missing_routes:
        print(f"{Color.YELLOW}Warning: {len(missing_routes)} essential routes are missing{Color.ENDC}")
    
    # Print all registered routes for reference
    print("\nAll registered routes:")
    for endpoint, rule in sorted(routes, key=lambda x: x[0]):
        print(f"  {endpoint}: {rule}")
    
    return not missing_routes

def run_app_test():
    """Run the application test"""
    print_header("Aksjeradar Application Test")
    
    # Test app creation
    if not test_app_creation():
        return False
    
    # Import the app again for route testing
    try:
        from app import create_app
        app = create_app('testing')
        test_routes(app)
    except Exception as e:
        print_result("Route Testing", False, f"Error: {str(e)}")
        return False
    
    print_section("Test Complete")
    print("Application initialization test completed successfully")
    return True

if __name__ == "__main__":
    success = run_app_test()
    sys.exit(0 if success else 1)
