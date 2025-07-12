#!/usr/bin/env python3
"""
Comprehensive test to verify all blueprint registration issues are resolved
"""
import os
import sys

# Set up environment
os.environ['SECRET_KEY'] = 'test-key-12345'
os.environ['WTF_CSRF_SECRET_KEY'] = 'test-csrf-key-12345'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

def test_blueprint_registration():
    """Test that all blueprints register correctly without conflicts"""
    print("🔍 Testing Blueprint Registration...")
    
    try:
        from app import create_app
        print("✅ App module imported successfully")
        
        app = create_app('development')
        print("✅ App created successfully")
        
        # Test blueprint registration
        blueprints = list(app.blueprints.keys())
        print(f"✅ Found {len(blueprints)} registered blueprints:")
        for bp in sorted(blueprints):
            print(f"   - {bp}")
        
        # Test main blueprint specifically
        if 'main' in blueprints:
            print("✅ Main blueprint registered successfully")
        else:
            print("❌ Main blueprint missing!")
            return False
        
        # Test for route conflicts
        routes = {}
        conflicts = []
        
        for rule in app.url_map.iter_rules():
            endpoint = rule.endpoint
            path = rule.rule
            
            if endpoint in routes:
                conflicts.append(f"Duplicate endpoint: {endpoint} -> {path} vs {routes[endpoint]}")
            else:
                routes[endpoint] = path
        
        if conflicts:
            print("❌ Route conflicts found:")
            for conflict in conflicts:
                print(f"   {conflict}")
            return False
        else:
            print(f"✅ No route conflicts found ({len(routes)} unique routes)")
        
        # Test specific routes that were causing issues
        critical_routes = [
            'main.restricted_access',
            'main.index',
            'main.login',
            'main.register'
        ]
        
        missing_routes = []
        for route in critical_routes:
            if route not in routes:
                missing_routes.append(route)
        
        if missing_routes:
            print(f"❌ Missing critical routes: {missing_routes}")
            return False
        else:
            print("✅ All critical routes found")
        
        # Test app context
        with app.app_context():
            print("✅ App context works correctly")
        
        print("🎉 All blueprint registration tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint registration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_run_py_compatibility():
    """Test that run.py works correctly"""
    print("\n🔍 Testing run.py Compatibility...")
    
    try:
        from run import app
        print("✅ App imported from run.py successfully")
        
        # Test that it's a Flask app
        from flask import Flask
        if isinstance(app, Flask):
            print("✅ App is a valid Flask application")
        else:
            print(f"❌ App is not a Flask application: {type(app)}")
            return False
        
        # Test that we can get routes
        with app.app_context():
            route_count = len(list(app.url_map.iter_rules()))
            print(f"✅ App has {route_count} routes registered")
        
        print("🎉 run.py compatibility test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ run.py compatibility test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("BLUEPRINT REGISTRATION CONFLICT RESOLUTION TEST")
    print("=" * 60)
    
    test1_passed = test_blueprint_registration()
    test2_passed = test_run_py_compatibility()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Blueprint registration conflicts resolved")
        print("✅ App is ready for deployment")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print("❌ Blueprint registration issues remain")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
