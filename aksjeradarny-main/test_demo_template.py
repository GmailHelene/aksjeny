#!/usr/bin/env python3
"""
Simple template render test with proper Flask context
"""

import sys
import os
sys.path.insert(0, '.')

from app import create_app

def test_demo_template():
    app = create_app()
    
    with app.test_client() as client:
        try:
            response = client.get('/demo')
            print(f"✅ Demo endpoint status: {response.status_code}")
            if response.status_code == 200:
                print(f"📝 Response length: {len(response.data)} bytes")
                print("✅ Demo template renders successfully")
                return True
            else:
                print(f"❌ Demo endpoint returned: {response.status_code}")
                print(f"📝 Response: {response.data.decode()[:200]}...")
                return False
        except Exception as e:
            print(f"❌ Demo template error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_demo_template()
