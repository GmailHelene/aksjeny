#!/usr/bin/env python3
"""
Railway production startup script with health check
"""
import os
import sys
import time
from app import create_app, db

def wait_for_database(app, max_retries=30, delay=2):
    """Wait for database to be ready"""
    print("🔄 Waiting for database connection...")
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Try to execute a simple query
                db.session.execute(db.text('SELECT 1'))
                db.session.commit()
                print("✅ Database connection established")
                return True
        except Exception as e:
            print(f"⏳ Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print("❌ Database connection failed after maximum retries")
                return False
    
    return False

def main():
    """Main startup function"""
    print("🚀 Starting Aksjeradar production server...")
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    
    try:
        # Create Flask app
        app = create_app('production')
        print("✅ Flask app created successfully")
        
        # Wait for database
        if not wait_for_database(app):
            print("❌ Database connection failed - exiting")
            sys.exit(1)
        
        # Initialize database tables if needed
        with app.app_context():
            try:
                db.create_all()
                print("✅ Database tables initialized")
            except Exception as e:
                print(f"⚠️ Database table creation warning: {e}")
        
        # Get port from environment with proper Railway handling
        port_env = os.environ.get('PORT', '5000')
        try:
            port = int(port_env)
        except ValueError:
            print(f"⚠️ Invalid PORT value: {port_env}, using default 5000")
            port = 5000
        
        print(f"🌐 Starting server on port {port}")
        
        # Start the application
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
