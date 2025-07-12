import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    from app import create_app
    print("Successfully imported create_app")
    app = create_app("testing")
    print("Successfully created app instance")
    with app.app_context():
        print("Entered app context")
        # Try to access a simple Flask-Login object to see if it's initialized
        from flask_login import current_user
        print(f"current_user: {current_user}")
        # Try to access db to see if it's initialized
        from app.extensions import db
        print(f"db: {db}")
        print("Exited app context")
except Exception as e:
    print(f"Error during import or app creation: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


