#!/usr/bin/env python3
"""
Test portfolio functionality with debug info
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    from app import create_app
    from app.models import User, Portfolio, PortfolioStock
    from app.extensions import db
    from flask_login import login_user
    
    app = create_app()
    
    with app.app_context():
        print("✅ App created successfully")
        
        # Test if we can create a test user and login
        from werkzeug.security import generate_password_hash
        
        test_user = User.query.filter_by(email='test@test.com').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@test.com',
                password_hash=generate_password_hash('testpass'),
                is_subscriber=True,
                subscription_status='active'
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created")
        else:
            print("✅ Test user exists")
        
        # Now test the portfolio route directly
        with app.test_client() as client:
            # Login first
            login_response = client.post('/login', data={
                'email': 'test@test.com',
                'password': 'testpass'
            }, follow_redirects=True)
            print(f"Login status: {login_response.status_code}")
            
            # Try to access portfolio overview
            portfolio_response = client.get('/portfolio/overview')
            print(f"Portfolio overview status: {portfolio_response.status_code}")
            
            if portfolio_response.status_code != 200:
                print(f"Error: {portfolio_response.data.decode()[:500]}")
                
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
