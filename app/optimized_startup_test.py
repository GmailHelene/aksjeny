#!/usr/bin/env python3
"""
Optimalisert app startup test
Test hvor raskt appen starter opp etter optimaliseringer
"""
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    print("=== OPTIMALISERT APP STARTUP TEST ===")
    
    # Test 1: Import speed
    start_time = time.time()
    
    print("1. Testing Flask import...")
    import_start = time.time()
    from flask import Flask
    print(f"   Flask import: {(time.time() - import_start):.3f}s")
    
    print("2. Testing app module import...")
    import_start = time.time()
    from app import create_app
    print(f"   App module import: {(time.time() - import_start):.3f}s")
    
    print("3. Testing app creation...")
    creation_start = time.time()
    app = create_app('development')
    creation_time = time.time() - creation_start
    print(f"   App creation: {creation_time:.3f}s")
    
    print("4. Testing basic app functionality...")
    func_start = time.time()
    with app.test_client() as client:
        # Test basic routes
        response = client.get('/')
        home_status = response.status_code
        
        response = client.get('/demo')
        demo_status = response.status_code
        
        response = client.get('/ai-explained')
        ai_status = response.status_code
    func_time = time.time() - func_start
    print(f"   Basic functionality test: {func_time:.3f}s")
    
    total_time = time.time() - start_time
    
    print("\n=== RESULTS ===")
    print(f"📊 Total startup time: {total_time:.3f}s")
    print(f"🏠 Home page: {home_status}")
    print(f"🎮 Demo page: {demo_status}")
    print(f"🤖 AI-explained page: {ai_status}")
    
    # Performance assessment
    if total_time < 2.0:
        print("✅ EXCELLENT: Very fast startup!")
    elif total_time < 5.0:
        print("✅ GOOD: Acceptable startup time")
    elif total_time < 10.0:
        print("⚠️  SLOW: Could be improved")
    else:
        print("❌ VERY SLOW: Needs optimization")
    
    return total_time, home_status, demo_status, ai_status

def test_lazy_loading():
    print("\n=== LAZY LOADING TEST ===")
    
    try:
        from app.routes.main import get_user_model, get_data_service, get_forms, get_stripe, get_pytz
        
        print("1. Testing lazy imports...")
        
        # Test User model import
        start = time.time()
        User = get_user_model()
        print(f"   User model: {(time.time() - start):.3f}s")
        
        # Test DataService import
        start = time.time()
        DataService = get_data_service()
        print(f"   DataService: {(time.time() - start):.3f}s")
        
        # Test Forms import
        start = time.time()
        forms = get_forms()
        print(f"   Forms: {(time.time() - start):.3f}s")
        
        # Test Stripe import
        start = time.time()
        stripe = get_stripe()
        print(f"   Stripe: {(time.time() - start):.3f}s")
        
        # Test pytz import
        start = time.time()
        pytz = get_pytz()
        print(f"   Pytz: {(time.time() - start):.3f}s")
        
        print("✅ All lazy imports working correctly!")
        
    except Exception as e:
        print(f"❌ Lazy loading test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        total_time, home, demo, ai = test_app_startup()
        test_lazy_loading()
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Startup time: {total_time:.3f}s")
        print(f"   All basic routes working: {all([home == 200, demo == 200, ai == 200])}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
