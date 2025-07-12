#!/usr/bin/env python3
"""
Test for duplicate routes and blueprint issues
"""
import os
import sys

# Add project root to path
sys.path.insert(0, '/workspaces/aksjeradarv6')

def test_blueprint_uniqueness():
    """Test if blueprints can be registered without conflicts"""
    print("🔍 Testing blueprint registration...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-key'
        app.config['TESTING'] = True
        
        # Import and register main blueprint
        from app.routes.main import main
        print("✅ Main blueprint imported")
        
        app.register_blueprint(main)
        print("✅ Main blueprint registered")
        
        # Check for duplicate route names
        route_endpoints = []
        duplicate_routes = []
        
        for rule in app.url_map.iter_rules():
            if rule.endpoint in route_endpoints:
                duplicate_routes.append(rule.endpoint)
            else:
                route_endpoints.append(rule.endpoint)
        
        if duplicate_routes:
            print(f"❌ Found duplicate routes: {duplicate_routes}")
            return False
        else:
            print(f"✅ No duplicate routes found ({len(route_endpoints)} unique routes)")
        
        # Check for restricted_access route specifically
        restricted_routes = [rule for rule in app.url_map.iter_rules() if 'restricted_access' in rule.rule]
        print(f"✅ Found {len(restricted_routes)} restricted_access route(s)")
        for route in restricted_routes:
            print(f"   - {route.endpoint} -> {route.rule}")
        
        return True
        
    except Exception as e:
        print(f"❌ Blueprint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_run_py():
    """Test run.py configuration"""
    print("\n🔍 Testing run.py configuration...")
    
    try:
        # Read run.py content
        with open('/workspaces/aksjeradarv6/run.py', 'r') as f:
            content = f.read()
        
        # Count create_app calls
        create_app_calls = content.count('create_app(')
        print(f"✅ Found {create_app_calls} create_app() calls in run.py")
        
        if create_app_calls > 2:
            print("⚠️ Multiple create_app() calls detected - this could cause issues")
            return False
        
        # Check for proper conditional execution
        if '__name__ == \'__main__\'' in content:
            print("✅ Proper conditional execution found")
        else:
            print("⚠️ Missing conditional execution guard")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ run.py test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting blueprint conflict tests...\n")
    
    blueprint_ok = test_blueprint_uniqueness()
    run_py_ok = test_run_py()
    
    print(f"\n📊 Test Results:")
    print(f"   Blueprint test: {'✅ PASS' if blueprint_ok else '❌ FAIL'}")
    print(f"   run.py test: {'✅ PASS' if run_py_ok else '❌ FAIL'}")
    
    if blueprint_ok and run_py_ok:
        print("\n🎉 All tests passed! Blueprint conflicts should be resolved.")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
        sys.exit(1)
