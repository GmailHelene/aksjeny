#!/usr/bin/env python3
"""
Minimal Flask app to test blueprint conflicts
"""
import sys
sys.path.insert(0, '/workspaces/aksjeradarv6')

from flask import Flask

print("Creating minimal Flask app...")
app = Flask(__name__)

try:
    print("Testing main blueprint import...")
    from app.routes.main import main
    print("✅ Main blueprint imported successfully")
    
    print("Testing blueprint registration...")
    app.register_blueprint(main)
    print("✅ Main blueprint registered successfully")
    
    print("Checking routes...")
    for rule in app.url_map.iter_rules():
        if 'restricted_access' in rule.rule:
            print(f"Found restricted_access route: {rule.endpoint} -> {rule.rule}")
    
    print("🎉 No blueprint conflicts detected!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
