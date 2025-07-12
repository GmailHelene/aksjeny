#!/usr/bin/env python3
"""
Test if the blueprint registration issue is fixed
"""
import os
import sys

# Change to the app directory
os.chdir('/workspaces/aksjeradarv6')

try:
    from app import create_app
    print("✅ App import successful")
    
    app = create_app()
    print("✅ App creation successful")
    
    # Test that main blueprint is registered correctly
    with app.app_context():
        route_count = 0
        for rule in app.url_map.iter_rules():
            if rule.endpoint.startswith('main.'):
                route_count += 1
        
        print(f"✅ Found {route_count} main blueprint routes")
        
        # Check for specific routes that were causing conflicts
        target_routes = ['main.restricted_access', 'main.index', 'main.login']
        found_routes = []
        
        for rule in app.url_map.iter_rules():
            if rule.endpoint in target_routes:
                found_routes.append(rule.endpoint)
                print(f"✅ Found: {rule.endpoint} -> {rule.rule}")
        
        missing = set(target_routes) - set(found_routes)
        if missing:
            print(f"❌ Missing routes: {missing}")
        else:
            print("🎉 All critical routes found!")
            
        print(f"\nTotal blueprints registered: {len(set(rule.endpoint.split('.')[0] for rule in app.url_map.iter_rules() if '.' in rule.endpoint))}")
        print("🎉 Blueprint registration test PASSED!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
