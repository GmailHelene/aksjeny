
import os
from app import create_app
from app.extensions import db

# Determine config based on environment
# Railway sets RAILWAY_ENVIRONMENT, use that as primary indicator
if os.getenv('RAILWAY_ENVIRONMENT'):
    config_name = 'production'
    print(f"🚂 Railway environment detected, using production config")
elif os.getenv('FLASK_ENV'):
    config_name = os.getenv('FLASK_ENV')
    print(f"🔧 FLASK_ENV detected: {config_name}")
else:
    config_name = 'production'  # Default to production for safety
    print(f"🔧 No environment specified, defaulting to: {config_name}")

print(f"🔧 Initializing database with config: {config_name}")

try:
    app = create_app(config_name)
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
