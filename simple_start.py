#!/usr/bin/env python3
"""
Railway-optimized startup with proper PORT handling
"""
import os
import sys

# Force production mode
os.environ['FLASK_ENV'] = 'production'

print("🚀 Railway startup with proper PORT handling")

try:
    from app import create_app
    app = create_app('production')
    
    # Get port from Railway environment, default to 5000 for local testing
    port = int(os.environ.get('PORT', 5000))
    print(f"📡 Starting app on port {port}")
    
    # Railway automatically provides port, we just bind to all interfaces
    # Railway will route traffic correctly
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)