from flask import Flask
import os
import sys

# Add the parent directory to sys.path
app_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, app_dir)

# Import create_app from app/__init__.py
from app import create_app


app = create_app('development')

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