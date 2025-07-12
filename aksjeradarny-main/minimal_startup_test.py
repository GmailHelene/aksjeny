#!/usr/bin/env python3
"""
Minimal startup test to identify bottleneck
"""
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_step_by_step():
    print("=== STEP-BY-STEP ANALYSIS ===")
    
    total_start = time.time()
    
    # Step 1: Basic Flask
    start = time.time()
    from flask import Flask
    print(f"1. Flask import: {time.time() - start:.3f}s")
    
    # Step 2: Extensions
    start = time.time()
    from app.extensions import db, login_manager, mail
    print(f"2. Extensions import: {time.time() - start:.3f}s")
    
    # Step 3: Config
    start = time.time()
    from config import config
    print(f"3. Config import: {time.time() - start:.3f}s")
    
    # Step 4: Main blueprint
    start = time.time()
    from app.routes.main import main
    print(f"4. Main blueprint import: {time.time() - start:.3f}s")
    
    # Step 5: Basic app creation
    start = time.time()
    app = Flask(__name__)
    app.config.from_object(config['development'])
    print(f"5. Basic app creation: {time.time() - start:.3f}s")
    
    # Step 6: Extensions init
    start = time.time()
    db.init_app(app)
    login_manager.init_app(app)
    print(f"6. Extensions init: {time.time() - start:.3f}s")
    
    # Step 7: Blueprint registration
    start = time.time()
    app.register_blueprint(main)
    print(f"7. Blueprint registration: {time.time() - start:.3f}s")
    
    print(f"\n📊 Total time: {time.time() - total_start:.3f}s")
    
    # Step 8: Test basic functionality
    start = time.time()
    with app.test_client() as client:
        try:
            response = client.get('/demo')  # Simple route
            print(f"8. Demo route test: {response.status_code} ({time.time() - start:.3f}s)")
        except Exception as e:
            print(f"8. Demo route test FAILED: {e}")
    
    return time.time() - total_start

if __name__ == "__main__":
    try:
        total_time = test_step_by_step()
        print(f"\n🎯 Analysis complete in {total_time:.3f}s")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
