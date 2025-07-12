#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

print("Starting import tests...")

try:
    print("1. Testing Flask import...")
    import flask
    print("✅ Flask OK")
    
    print("2. Testing basic app structure...")
    from app import create_app
    print("✅ App import OK")
    
    print("3. Creating app...")
    app = create_app()
    print("✅ App creation OK")
    
    print("4. Testing app context...")
    with app.app_context():
        print("✅ App context OK")
        
        # List all routes
        routes = list(app.url_map.iter_rules())
        print(f"✅ Found {len(routes)} total routes")
        
        # Find market-intel routes
        market_routes = [r for r in routes if 'market-intel' in r.rule]
        print(f"Market-intel routes: {len(market_routes)}")
        for route in market_routes:
            print(f"  {route.rule} -> {route.endpoint}")
            
        # Test specific endpoint
        if market_routes:
            print("✅ Market intel routes found!")
        else:
            print("❌ No market intel routes found!")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
