from flask import Flask
import os
import sys

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import create_app from the current directory's __init__.py
from __init__ import create_app

app = create_app('development')

# Entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)