from flask import Flask
import os
import sys

# Add the parent directory to sys.path
app_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, app_dir)

# Import create_app from app/__init__.py
from app import create_app

# Determine config based on environment
# Railway sets RAILWAY_ENVIRONMENT, use that as primary indicator
if os.getenv('RAILWAY_ENVIRONMENT'):
    config_name = 'production'
    print(f"🚂 Railway environment detected, using production config")
    print(f"🔧 PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
    print(f"🔧 DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")
elif os.getenv('FLASK_ENV'):
    config_name = os.getenv('FLASK_ENV')
    print(f"🔧 FLASK_ENV detected: {config_name}")
else:
    config_name = 'production'  # Default to production for safety
    print(f"🔧 No environment specified, defaulting to: {config_name}")

print(f"🔧 Creating app with config: {config_name}")

try:
    app = create_app(config_name)
    print("✅ App created successfully for WSGI")
    
    # Test basic functionality
    with app.app_context():
        print("✅ App context working for WSGI")
            
except Exception as e:
    print(f"❌ Failed to create app: {e}")
    import traceback
    print(f"❌ Full traceback: {traceback.format_exc()}")
    # Create minimal fallback app for health checks
    app = Flask(__name__)
    @app.route('/health/ready')
    def health():
        return {'status': 'error', 'message': f'App failed to initialize: {str(e)}'}, 500
    @app.route('/')
    def home():
        return {'status': 'error', 'message': f'App failed to initialize: {str(e)}'}, 500

# Entry point
if __name__ == '__main__':
    # Allow port to be set via environment variable or command-line argument
    import sys
    port = 5000
    # Check for command-line argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except Exception:
            pass
    # Check for environment variable
    port = int(os.environ.get('PORT', port))
    # Use debug mode only in development
    debug_mode = config_name == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)