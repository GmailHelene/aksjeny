#!/usr/bin/env python3
"""
Forenklet endepunkt-test som ikke krever Flask-server
"""
import sys
import os
import requests
import json
from datetime import datetime

# Legg til prosjektkatalogen i Python-stien
sys.path.insert(0, '/workspaces/aksjeradarny')

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def test_app_creation():
    """Test om Flask-appen kan opprettes uten å kjøre den"""
    print(f"{Color.BLUE}🧪 Testing Flask app creation...{Color.END}")
    
    try:
        from app import create_app
        print(f"{Color.GREEN}✅ Successfully imported create_app{Color.END}")
        
        app = create_app()
        print(f"{Color.GREEN}✅ Successfully created Flask app{Color.END}")
        
        # List all routes
        with app.app_context():
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                    'path': str(rule)
                })
            
            print(f"{Color.GREEN}✅ Found {len(routes)} routes{Color.END}")
            
            # Group routes by blueprint
            blueprints = {}
            for route in routes:
                bp = route['endpoint'].split('.')[0] if '.' in route['endpoint'] else 'app'
                if bp not in blueprints:
                    blueprints[bp] = []
                blueprints[bp].append(route)
            
            print(f"\n{Color.BOLD}📍 ROUTE OVERVIEW:{Color.END}")
            print("=" * 80)
            
            total_routes = 0
            for bp_name, bp_routes in sorted(blueprints.items()):
                print(f"\n{Color.BLUE}{bp_name.upper()} BLUEPRINT ({len(bp_routes)} routes):{Color.END}")
                for route in sorted(bp_routes, key=lambda x: x['path']):
                    methods = ', '.join(route['methods']) if route['methods'] else 'GET'
                    print(f"  {methods:10} {route['path']:50} -> {route['endpoint']}")
                total_routes += len(bp_routes)
            
            print(f"\n{Color.GREEN}📊 SUMMARY: {total_routes} total routes found{Color.END}")
            
            # Save route information to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"route_overview_{timestamp}.json"
            
            route_data = {
                'timestamp': datetime.now().isoformat(),
                'total_routes': total_routes,
                'blueprints': blueprints
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(route_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"{Color.BLUE}📄 Route information saved to: {filename}{Color.END}")
            
            return True
            
    except Exception as e:
        print(f"{Color.RED}❌ Error creating Flask app: {e}{Color.END}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test import av alle viktige moduler"""
    print(f"\n{Color.BLUE}📦 Testing module imports...{Color.END}")
    
    modules_to_test = [
        'app',
        'app.routes.main', 
        'app.routes.stocks',
        'app.routes.analysis',
        'app.routes.portfolio',
        'app.routes.api',
        'app.routes.health',
        'app.models',
        'config'
    ]
    
    results = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"{Color.GREEN}✅ {module:30} imported successfully{Color.END}")
            results.append((module, True, None))
        except Exception as e:
            print(f"{Color.RED}❌ {module:30} failed: {str(e)[:50]}{Color.END}")
            results.append((module, False, str(e)))
    
    success_count = sum(1 for _, success, _ in results if success)
    print(f"\n{Color.BLUE}📊 Import summary: {success_count}/{len(modules_to_test)} modules imported successfully{Color.END}")
    
    return results

def test_database_models():
    """Test database model imports"""
    print(f"\n{Color.BLUE}🗄️  Testing database models...{Color.END}")
    
    try:
        from app.models.user import User
        print(f"{Color.GREEN}✅ User model imported{Color.END}")
        
        from app.models.portfolio import Portfolio
        print(f"{Color.GREEN}✅ Portfolio model imported{Color.END}")
        
        from app.models.watchlist import Watchlist
        print(f"{Color.GREEN}✅ Watchlist model imported{Color.END}")
        
        return True
        
    except Exception as e:
        print(f"{Color.RED}❌ Database model error: {e}{Color.END}")
        return False

def test_with_running_server():
    """Test hvis en server allerede kjører"""
    print(f"\n{Color.BLUE}🌐 Testing connection to running server...{Color.END}")
    
    base_url = "http://localhost:5000"
    
    # Test basic endpoints
    test_endpoints = [
        "/health",
        "/",
        "/demo",
        "/login",
        "/api/crypto"
    ]
    
    results = []
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ PASS" if response.status_code in [200, 302, 401, 403] else "❌ FAIL"
            print(f"{Color.GREEN if '✅' in status else Color.RED}{status} {endpoint:20} [{response.status_code}]{Color.END}")
            results.append((endpoint, response.status_code, True))
        except requests.exceptions.ConnectionError:
            print(f"{Color.YELLOW}⚠️  NO CONNECTION {endpoint:20} [Server not running]{Color.END}")
            results.append((endpoint, None, False))
        except Exception as e:
            print(f"{Color.RED}❌ ERROR {endpoint:20} [{str(e)[:30]}]{Color.END}")
            results.append((endpoint, None, False))
    
    return results

def main():
    """Hovedfunksjon"""
    print(f"{Color.BOLD}🚀 Aksjeradar Static Analysis{Color.END}")
    print("=" * 60)
    print(f"Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test imports
    import_results = test_imports()
    
    # Test database models
    db_success = test_database_models()
    
    # Test app creation and route discovery
    app_success = test_app_creation()
    
    # Test if server is running
    server_results = test_with_running_server()
    
    # Final summary
    print(f"\n{Color.BOLD}📊 FINAL SUMMARY:{Color.END}")
    print("=" * 60)
    
    import_success = sum(1 for _, success, _ in import_results if success)
    print(f"Module imports:     {import_success}/{len(import_results)} ({'✅' if import_success > len(import_results)//2 else '❌'})")
    print(f"Database models:    {'✅ Working' if db_success else '❌ Failed'}")
    print(f"App creation:       {'✅ Working' if app_success else '❌ Failed'}")
    
    server_connections = sum(1 for _, _, connected in server_results if connected)
    print(f"Server connection:  {server_connections}/{len(server_results)} endpoints ({'✅' if server_connections > 0 else '❌'})")
    
    overall_success = app_success and db_success and import_success > len(import_results)//2
    print(f"\nOverall status:     {'✅ READY FOR TESTING' if overall_success else '❌ NEEDS FIXES'}")
    
    if overall_success:
        print(f"\n{Color.GREEN}🎉 The application appears to be properly configured!{Color.END}")
        print(f"{Color.BLUE}💡 To run endpoint tests, start the server with: python run.py{Color.END}")
    else:
        print(f"\n{Color.RED}⚠️  Some issues were found. Check the details above.{Color.END}")

if __name__ == "__main__":
    main()
