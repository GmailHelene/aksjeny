from flask import Flask
import os
import sys

# Add the parent directory to sys.path
app_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, app_dir)

# Import create_app from app/__init__.py
from app import create_app

# Use environment variable for config, default to production
config_name = os.getenv('FLASK_ENV', 'production')
print(f"🔧 Creating app with config: {config_name}")

try:
    app = create_app(config_name)
    print("✅ App created successfully for WSGI")
except Exception as e:
    print(f"❌ Failed to create app: {e}")
    # Create minimal fallback app for health checks
    app = Flask(__name__)
    @app.route('/health/ready')
    def health():
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
    app.run(host='0.0.0.0', port=port, debug=True)