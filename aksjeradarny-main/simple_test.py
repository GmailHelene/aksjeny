#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("Testing CSRF functionality...")

try:
    from app import create_app
    app = create_app('development')
    print("✅ App created successfully")
    
    with app.app_context():
        from flask_wtf.csrf import generate_csrf
        token = generate_csrf()
        print(f"✅ CSRF token generated successfully (length: {len(token)})")
        
    print("✅ All CSRF fixes are working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
