#!/usr/bin/env python3
"""Direct test of route registration"""
try:
    from app import create_app
    print("✅ App import successful")
    
    app = create_app()
    print("✅ App creation successful")
    
    with app.app_context():
        found_routes = []
        target_routes = ['/demo', '/ai-explained', '/pricing/', '/api/stocks/search', '/api/market-data']
        
        for rule in app.url_map.iter_rules():
            if rule.rule in target_routes:
                found_routes.append(rule.rule)
                print(f"✅ Found: {rule.rule} -> {rule.endpoint}")
        
        missing = set(target_routes) - set(found_routes)
        if missing:
            print(f"❌ Missing routes: {missing}")
        else:
            print("🎉 All target routes found!")
            
        print(f"\nTotal routes in app: {len(list(app.url_map.iter_rules()))}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
