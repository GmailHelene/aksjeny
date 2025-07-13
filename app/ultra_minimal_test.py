#!/usr/bin/env python3
"""
Ultra-minimal test to verify app works
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("Starting ultra-minimal test...")
    
    # Test just the basic Flask setup
    from flask import Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    
    # Add a simple route
    @app.route('/')
    def home():
        return "Hello World!"
    
    @app.route('/demo')
    def demo():
        return "Demo page works!"
    
    # Test it
    with app.test_client() as client:
        response = client.get('/')
        print(f"Home: {response.status_code} - {response.get_data(as_text=True)}")
        
        response = client.get('/demo')
        print(f"Demo: {response.status_code} - {response.get_data(as_text=True)}")
    
    print("✅ Ultra-minimal test passed!")
    
    # Now test with just main blueprint  
    print("\nTesting with main blueprint...")
    from app.routes.main import main
    
    app2 = Flask(__name__)
    app2.config['SECRET_KEY'] = 'test-key'
    app2.register_blueprint(main)
    
    with app2.test_client() as client:
        response = client.get('/demo')
        print(f"Blueprint demo: {response.status_code}")
    
    print("✅ Blueprint test passed!")
