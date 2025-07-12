#!/usr/bin/env python3
import os
os.chdir('/workspaces/aksjeradarny')

try:
    from app import create_app
    app = create_app()
    
    target_routes = ['/demo', '/ai-explained', '/portfolio/advanced/', '/blog/', '/investment-guides/', '/pricing/', '/api/stocks/search', '/api/market-data']
    found_routes = []
    
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if rule.rule in target_routes:
                found_routes.append(rule.rule)
    
    print("ROUTE STATUS:")
    for target in target_routes:
        status = "FOUND" if target in found_routes else "MISSING"
        print(f"{target}: {status}")
    
    print(f"\nSUMMARY: {len(found_routes)}/{len(target_routes)} routes found")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
