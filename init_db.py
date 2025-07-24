
import os
from app import create_app
from app.extensions import db

# Use environment variable for config
config_name = os.getenv('FLASK_ENV', 'production')
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
