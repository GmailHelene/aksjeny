#!/usr/bin/env python3
"""
Test app startup to identify issues
"""
import os
import sys
import traceback

print("Starting comprehensive app startup test...")

try:
    print("1. Testing environment...")
    print(f"   Python version: {sys.version}")
    print(f"   Current directory: {os.getcwd()}")
    
    print("2. Testing imports...")
    
    # Test basic imports
    import flask
    print(f"   Flask version: {flask.__version__}")
    
    # Test app import
    from app import create_app
    print("   ✅ App module imported successfully")
    
    print("3. Testing app creation...")
    app = create_app('development')
    print("   ✅ App created successfully")
    
    print("4. Testing app context...")
    with app.app_context():
        print("   ✅ App context works")
        
        # Test database connection
        from app.extensions import db
        print("   ✅ Database extension imported")
        
        # Create all tables
        db.create_all()
        print("   ✅ Database tables created")
        
        # Test simple query
        try:
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1'))
            print("   ✅ Database query works")
        except Exception as e:
            print(f"   ⚠️ Database query failed: {e}")
        
        # Test health endpoint
        try:
            from app.routes.health import health
            print("   ✅ Health blueprint imported")
        except Exception as e:
            print(f"   ⚠️ Health blueprint import failed: {e}")
            
    print("5. Testing basic routes...")
    with app.test_client() as client:
        try:
            response = client.get('/')
            print(f"   ✅ Root route: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Root route failed: {e}")
            
        try:
            response = client.get('/health')
            print(f"   ✅ Health route: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ Health route failed: {e}")
            
    print("\n🎉 App startup test completed successfully!")
    
except Exception as e:
    print(f"\n❌ App startup test failed: {e}")
    traceback.print_exc()
    sys.exit(1)
