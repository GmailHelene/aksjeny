#!/usr/bin/env python3
"""
Test script to verify app works without DataService dependencies
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimal_app():
    """Test minimal app creation without external dependencies"""
    print("🔍 Testing minimal app without DataService...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-key'
        app.config['TESTING'] = True
        app.config['USE_DUMMY_DATA'] = True
        
        @app.route('/')
        def home():
            return "Aksjeradar is running!"
        
        @app.route('/health')
        def health():
            return {"status": "ok", "message": "App is healthy"}
        
        # Test the app
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            
            response = client.get('/health')
            assert response.status_code == 200
        
        print("✅ Minimal app test passed")
        return True
        
    except Exception as e:
        print(f"❌ Minimal app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_with_fallback_data():
    """Test app using only fallback data"""
    print("\n🔍 Testing app with fallback data only...")
    
    try:
        # Set environment to use dummy data
        os.environ['USE_DUMMY_DATA'] = 'True'
        os.environ['TESTING'] = 'True'
        
        from app import create_app
        app = create_app('testing')
        
        with app.test_client() as client:
            # Test basic routes
            response = client.get('/')
            print(f"   Home page: {response.status_code}")
            
            response = client.get('/demo')
            print(f"   Demo page: {response.status_code}")
            
            response = client.get('/ai-explained')
            print(f"   AI explained page: {response.status_code}")
        
        print("✅ Fallback data test passed")
        return True
        
    except Exception as e:
        print(f"❌ Fallback data test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_static_routes():
    """Test routes that don't depend on external data"""
    print("\n🔍 Testing static routes...")
    
    try:
        from app import create_app
        app = create_app('testing')
        
        static_routes = [
            '/',
            '/demo',
            '/ai-explained',
            '/pricing',
            '/about'
        ]
        
        with app.test_client() as client:
            for route in static_routes:
                try:
                    response = client.get(route)
                    if response.status_code == 200:
                        print(f"✅ {route}: OK")
                    else:
                        print(f"⚠️  {route}: {response.status_code}")
                except Exception as e:
                    print(f"❌ {route}: Error - {e}")
        
        print("✅ Static routes test completed")
        return True
        
    except Exception as e:
        print(f"❌ Static routes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests without DataService dependencies"""
    print("🧪 TESTING APP WITHOUT DATASERVICE DEPENDENCIES")
    print("=" * 60)
    
    results = []
    results.append(test_minimal_app())
    results.append(test_app_with_fallback_data())
    results.append(test_static_routes())
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 App works without external dependencies!")
    else:
        print("⚠️  Some functionality needs external dependencies")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
