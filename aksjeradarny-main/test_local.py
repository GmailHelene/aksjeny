import os
import webbrowser
from app import create_app
from app.extensions import db

def setup_test_environment():
    """Set up the test environment with dummy data"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
    with app.app_context():
        db.create_all()
        
    return app

if __name__ == '__main__':
    print("Starting Aksjeradar in test mode...")
    app = setup_test_environment()
    
    # Open browser automatically
    port = 5000
    webbrowser.open(f'http://localhost:{port}')
    
    # Run the app
    app.run(host='0.0.0.0', debug=True, port=port)
