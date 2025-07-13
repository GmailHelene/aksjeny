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
    app.run(host='0.0.0.0', port=5000, debug=True)