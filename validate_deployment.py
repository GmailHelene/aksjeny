#!/usr/bin/env python3
"""
Production Deployment Validation Script
======================================

Validates the application is ready for Railway deployment.
"""

import sys
import os
import importlib.util

def check_requirements():
    """Check if production requirements can be installed"""
    print("🔍 Checking production requirements...")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf',
        'flask_mail', 'flask_socketio', 'gunicorn', 'eventlet',
        'python_dotenv', 'requests', 'psycopg2', 'yfinance',
        'pandas', 'numpy', 'matplotlib', 'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(package)
            else:
                print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    
    print("✅ All required packages available")
    return True

def check_app_creation():
    """Test app creation"""
    print("\n🔍 Testing app creation...")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app import create_app
        
        app = create_app()
        print("✅ App creation successful")
        
        # Test real-time service
        try:
            from app.services.realtime_data_service import get_real_time_service
            rt_service = get_real_time_service()
            print("✅ Real-time service available")
        except Exception as e:
            print(f"⚠️ Real-time service warning: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """Test database connectivity"""
    print("\n🔍 Testing database setup...")
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            # Test database connection
            db.create_all()
            print("✅ Database tables created successfully")
            
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def check_docker_files():
    """Check Docker configuration"""
    print("\n🔍 Checking Docker configuration...")
    
    # Check if Dockerfile exists
    if not os.path.exists('Dockerfile'):
        print("❌ Dockerfile not found")
        return False
    
    print("✅ Dockerfile found")
    
    # Check if production requirements exist
    if not os.path.exists('requirements-prod.txt'):
        print("❌ requirements-prod.txt not found")
        return False
    
    print("✅ Production requirements found")
    
    return True

def check_socketio_compatibility():
    """Check SocketIO compatibility"""
    print("\n🔍 Testing SocketIO compatibility...")
    
    try:
        from flask_socketio import SocketIO
        from app import create_app
        
        app = create_app()
        socketio = SocketIO(app, async_mode='eventlet')
        
        print("✅ SocketIO initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ SocketIO initialization failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 Railway Deployment Validation")
    print("=" * 50)
    
    checks = [
        check_requirements,
        check_app_creation,
        check_database,
        check_docker_files,
        check_socketio_compatibility
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Validation Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)} checks")
    
    if all(results):
        print("\n🎉 All checks passed! Ready for Railway deployment!")
        print("\n📋 Next steps:")
        print("1. git add .")
        print("2. git commit -m 'Fix: Docker deployment with SocketIO support'")
        print("3. git push origin main")
        print("4. Deploy to Railway")
        return True
    else:
        print("\n❌ Some checks failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
