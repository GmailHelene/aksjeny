#!/usr/bin/env python3
"""
Simple test to check what's causing portfolio 500 error
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    from app import create_app
    from app.models import Portfolio, PortfolioStock
    from app.extensions import db
    
    app = create_app()
    
    with app.app_context():
        print("✅ App created successfully")
        
        # Test database connection
        try:
            portfolios = Portfolio.query.all()
            print(f"✅ Database connected. Found {len(portfolios)} portfolios")
        except Exception as e:
            print(f"❌ Database error: {e}")
        
        # Test portfolio import
        print("✅ Portfolio models imported successfully")
        
        # Test DataService import
        try:
            from app.services.data_service import DataService
            print("✅ DataService imported successfully")
        except Exception as e:
            print(f"❌ DataService import error: {e}")
            
except Exception as e:
    print(f"❌ General error: {e}")
    import traceback
    traceback.print_exc()
