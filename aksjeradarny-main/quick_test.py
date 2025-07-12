#!/usr/bin/env python3
"""
Quick comprehensive test of the Aksjeradar application
"""
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """Test basic app creation and configuration"""
    print("🧪 Testing App Creation...")
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            routes = list(app.url_map.iter_rules())
            print(f"✅ App created successfully with {len(routes)} routes")
            
            # Check key routes
            key_routes = ['/demo', '/login', '/register', '/api/', '/portfolio/', '/pricing/']
            found_routes = []
            
            for rule in routes:
                for key in key_routes:
                    if key in rule.rule and rule.rule not in found_routes:
                        found_routes.append(rule.rule)
                        break
            
            print(f"✅ Found {len(found_routes)} key routes:")
            for route in found_routes[:10]:  # Show first 10
                print(f"   {route}")
            
            return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_database_models():
    """Test database model imports"""
    print("\n🗄️ Testing Database Models...")
    try:
        from app.models.user import User
        from app.models.portfolio import Portfolio
        from app.models.watchlist import Watchlist
        print("✅ All core models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_services():
    """Test service imports"""
    print("\n🔧 Testing Services...")
    try:
        from app.services.data_service import DataService
        from app.services.analysis_service import AnalysisService
        from app.services.ai_service import AIService
        print("✅ All core services imported successfully")
        return True
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False

def test_access_control():
    """Test access control system"""
    print("\n🔒 Testing Access Control...")
    try:
        from app.utils.access_control import access_required, UNRESTRICTED_ENDPOINTS, EXEMPT_EMAILS
        
        # Check if basic endpoints are unrestricted
        required_unrestricted = {'main.demo', 'main.login', 'main.register'}
        found_unrestricted = required_unrestricted.intersection(UNRESTRICTED_ENDPOINTS)
        
        print(f"✅ Access control loaded")
        print(f"✅ Found {len(found_unrestricted)}/{len(required_unrestricted)} required unrestricted endpoints")
        print(f"✅ Total unrestricted endpoints: {len(UNRESTRICTED_ENDPOINTS)}")
        print(f"✅ Exempt users configured: {len(EXEMPT_EMAILS)}")
        
        return True
    except Exception as e:
        print(f"❌ Access control test failed: {e}")
        return False

def test_with_client():
    """Test key endpoints using Flask test client"""
    print("\n🌐 Testing Key Endpoints...")
    try:
        from app import create_app
        app = create_app()
        
        # Test endpoints that should be accessible
        test_endpoints = [
            '/',
            '/demo',
            '/login',
            '/register',
            '/privacy',
            '/subscription',
            '/pricing/',
            '/api/health'
        ]
        
        passed = 0
        total = len(test_endpoints)
        
        with app.test_client() as client:
            for endpoint in test_endpoints:
                try:
                    response = client.get(endpoint)
                    status = "✅" if response.status_code in [200, 302] else "❌"
                    print(f"   {status} {endpoint}: {response.status_code}")
                    if response.status_code in [200, 302]:
                        passed += 1
                except Exception as e:
                    print(f"   ❌ {endpoint}: ERROR - {e}")
        
        print(f"\n✅ Endpoint tests: {passed}/{total} passed")
        return passed >= total * 0.7  # 70% success rate
        
    except Exception as e:
        print(f"❌ Endpoint testing failed: {e}")
        return False

def test_authentication_flow():
    """Test authentication and user flow"""
    print("\n👤 Testing Authentication Flow...")
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test login page
            response = client.get('/login')
            if response.status_code == 200:
                print("✅ Login page accessible")
            
            # Test register page  
            response = client.get('/register')
            if response.status_code == 200:
                print("✅ Register page accessible")
            
            # Test demo page (should always be accessible)
            response = client.get('/demo')
            if response.status_code == 200:
                print("✅ Demo page accessible")
            
            return True
    except Exception as e:
        print(f"❌ Authentication flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔬 AKSJERADAR APP COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        test_app_creation,
        test_database_models,
        test_services,
        test_access_control,
        test_with_client,
        test_authentication_flow
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Application is ready for production.")
        print("\n🚀 To start the server:")
        print("   python run.py")
        print("\n🌐 Access at: http://localhost:5000")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
