#!/usr/bin/env python3
"""
Fast startup test for optimized Aksjeradar app
"""
import time
import sys
import os

def test_fast_startup():
    """Test optimized app startup time"""
    print("🚀 Testing optimized app startup...")
    
    start_time = time.time()
    
    try:
        # Test import speed
        import_start = time.time()
        from app import create_app
        import_time = time.time() - import_start
        print(f"✅ Import time: {import_time:.2f}s")
        
        # Test app creation speed
        create_start = time.time()
        app = create_app('development')
        create_time = time.time() - create_start
        print(f"✅ App creation time: {create_time:.2f}s")
        
        # Test route registration
        route_start = time.time()
        with app.test_client() as client:
            # Test basic routes
            response = client.get('/')
            print(f"✅ Home route: {response.status_code}")
            
            response = client.get('/demo')
            print(f"✅ Demo route: {response.status_code}")
            
            response = client.get('/ai-explained')
            print(f"✅ AI-explained route: {response.status_code}")
            
        route_time = time.time() - route_start
        print(f"✅ Route testing time: {route_time:.2f}s")
        
        total_time = time.time() - start_time
        print(f"\n🎉 Total startup time: {total_time:.2f}s")
        
        if total_time < 5.0:
            print("🚀 EXCELLENT: Startup time under 5 seconds!")
        elif total_time < 10.0:
            print("✅ GOOD: Startup time under 10 seconds")
        else:
            print("⚠️ SLOW: Startup time over 10 seconds")
            
        return True
        
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_fast_startup()
    sys.exit(0 if success else 1)
