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

def main():
    """Main application entry point"""
    
    # Determine environment
    config_name = os.getenv('FLASK_ENV', 'development')
    
    print(f"🚀 Starting Aksjeradar in {config_name} mode...")
    
    try:
        # Create Flask application
        app = create_app(config_name)
        
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
