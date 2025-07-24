#!/usr/bin/env python3
"""
WSGI entry point for Railway deployment
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set production environment
os.environ.setdefault('FLASK_ENV', 'production')

try:
    from app import create_app
    app = create_app('production')
    
    # Ensure app is ready
    with app.app_context():
        from app.extensions import db
        # Create tables if they don't exist
        try:
            db.create_all()
            print("✅ Database tables initialized")
        except Exception as e:
            print(f"⚠️ Database initialization warning: {e}")
    
    print("✅ WSGI app initialized successfully")

except Exception as e:
    print(f"❌ WSGI app initialization failed: {e}")
    import traceback
    traceback.print_exc()
    raise

# Export for gunicorn
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
