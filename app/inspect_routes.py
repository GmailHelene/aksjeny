#!/usr/bin/env python3
"""
Flask server test with route inspection
"""
import sys
sys.path.append('/workspaces/aksjeradarv6')

from app import create_app

def inspect_routes():
    """Inspect all registered routes"""
    print("🔍 INSPECTING REGISTERED ROUTES")
    print("================================")
    
    app = create_app()
    
    target_routes = [
        '/demo',
        '/ai-explained', 
        '/portfolio/advanced/',
        '/blog/',
        '/investment-guides/',
        '/pricing/',
        '/api/stocks/search',
        '/api/market-data'
    ]
    
    found_routes = []
    all_routes = []
    
    with app.app_context():
        for rule in app.url_map.iter_rules():
            route_str = rule.rule
            all_routes.append(route_str)
            
            if route_str in target_routes:
                found_routes.append(route_str)
                print(f"✅ FOUND: {route_str} -> {rule.endpoint}")
        
        print("\n📋 TARGET ROUTES STATUS:")
        for target in target_routes:
            if target in found_routes:
                print(f"✅ {target} - REGISTERED")
            else:
                print(f"❌ {target} - MISSING")
        
        print(f"\n📊 SUMMARY:")
        print(f"Found: {len(found_routes)}/{len(target_routes)} target routes")
        print(f"Total routes in app: {len(all_routes)}")
        
        # Look for similar routes
        print(f"\n🔍 SIMILAR ROUTES:")
        for route in all_routes:
            for target in target_routes:
                if target not in found_routes and (target.replace('/', '') in route or route in target):
                    print(f"   {route} (similar to {target})")

if __name__ == "__main__":
    inspect_routes()
