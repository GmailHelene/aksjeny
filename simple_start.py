#!/usr/bin/env python3
"""
Ultra-simple Railway startup - no PORT variables
"""
import os
import sys

# Force production mode
os.environ['FLASK_ENV'] = 'production'

print("🚀 Ultra-simple Railway startup")

try:
    from app import create_app
    app = create_app('production')
    
    # Railway automatically provides port, we just bind to all interfaces
    # Railway will route traffic correctly
    app.run(
        host='0.0.0.0',
        port=5000,  # Hardcoded - Railway will handle the routing
        debug=False
    )
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
