#!/usr/bin/env python3
"""
Aksjeradar - Main application entry point
"""

import os
import sys
from app import create_app, db
from app.extensions import socketio

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create Flask application instance for WSGI servers (like gunicorn)
config_name = os.getenv('FLASK_ENV', 'production')
print(f"🔧 Creating app with config: {config_name}")

try:
    app = create_app(config_name)
    print("✅ App created successfully for WSGI")
    
    # Initialize database tables
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created/verified for WSGI")
        except Exception as e:
            print(f"⚠️ Database setup warning for WSGI: {e}")
            
except Exception as e:
    print(f"❌ Failed to create WSGI app: {e}")
    import traceback
    traceback.print_exc()
    # Create a minimal app as fallback
    from flask import Flask
    app = Flask(__name__)
    @app.route('/health/ready')
    def health():
        return {'status': 'error', 'message': 'App failed to initialize'}, 500

def main():
    """Main application entry point"""
    
    # Use the global app instance
    global app
    
    print(f"🚀 Starting Aksjeradar in {config_name} mode...")
    
    try:
        # Create database tables if they don't exist
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables created/verified")
            except Exception as e:
                print(f"⚠️ Database setup warning: {e}")
        
        # Determine host and port
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5001))
        debug = config_name == 'development'
        
        print(f"🌐 Server starting on http://{host}:{port}")
        print(f"📊 Debug mode: {debug}")
        
        # Start the application with SocketIO
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
