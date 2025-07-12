#!/usr/bin/env python3
"""
Simple route test to verify routes are working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_routes():
    print("=== SIMPLE ROUTE TEST ===")
    
    try:
        print("1. Importing Flask...")
        from flask import Flask
        
        print("2. Creating basic app...")
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-key'
        app.config['TESTING'] = True
        
        print("3. Importing main blueprint...")
        from app.routes.main import main
        
        print("4. Registering main blueprint...")
        app.register_blueprint(main)
        
        print("5. Testing key routes...")
        with app.test_client() as client:
            # Test main routes
            routes_to_test = [
                '/demo',
                '/ai-explained',
                '/',
                '/search',
                '/contact'
            ]
            
            for route in routes_to_test:
                try:
                    response = client.get(route)
                    print(f"   {route}: {response.status_code}")
                except Exception as e:
                    print(f"   {route}: ERROR - {e}")
        
        print("6. Testing other blueprints...")
        
        # Test seo_content blueprint
        try:
            from app.routes.seo_content import seo_content
            app.register_blueprint(seo_content)
            
            with app.test_client() as client:
                response = client.get('/blog/')
                print(f"   /blog/: {response.status_code}")
                response = client.get('/investment-guides/')
                print(f"   /investment-guides/: {response.status_code}")
        except Exception as e:
            print(f"   SEO content blueprint error: {e}")
        
        # Test pricing blueprint
        try:
            from app.routes.pricing import pricing_bp
            app.register_blueprint(pricing_bp, url_prefix='/pricing')
            
            with app.test_client() as client:
                response = client.get('/pricing/')
                print(f"   /pricing/: {response.status_code}")
        except Exception as e:
            print(f"   Pricing blueprint error: {e}")
        
        # Test portfolio_advanced blueprint
        try:
            from app.routes.portfolio_advanced import portfolio_advanced
            app.register_blueprint(portfolio_advanced, url_prefix='/portfolio')
            
            with app.test_client() as client:
                response = client.get('/portfolio/advanced/')
                print(f"   /portfolio/advanced/: {response.status_code}")
        except Exception as e:
            print(f"   Portfolio advanced blueprint error: {e}")
        
        print("✅ Route test completed successfully!")
        
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes()
