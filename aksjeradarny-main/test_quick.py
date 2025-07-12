#!/usr/bin/env python3
"""
Rask test av app oppstart og grunnleggende funksjonalitet
"""
import sys
import os
import traceback
from datetime import datetime

# Legg til prosjektets rot til Python path
sys.path.insert(0, os.path.abspath('.'))

def test_app_startup():
    """Test at appen kan startes opp"""
    print("🚀 Testing app startup...")
    
    try:
        # Test basic imports
        from app import create_app
        from app.extensions import db
        print("✅ Basic imports OK")
        
        # Create app
        app = create_app('development')
        print("✅ App creation OK")
        
        # Test app context
        with app.app_context():
            print("✅ App context OK")
            
            # Create all tables
            db.create_all()
            print("✅ Database creation OK")
            
            # Test basic routes
            with app.test_client() as client:
                # Test demo page (should be accessible)
                response = client.get('/demo')
                print(f"✅ Demo page: {response.status_code}")
                
                # Test pricing page
                response = client.get('/pricing/')
                print(f"✅ Pricing page: {response.status_code}")
                
                # Test auth pages
                response = client.get('/auth/login')
                print(f"✅ Login page: {response.status_code}")
                
                response = client.get('/auth/register')
                print(f"✅ Register page: {response.status_code}")
        
        print("\n🎉 App startup test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ App startup test FAILED: {e}")
        traceback.print_exc()
        return False

def test_static_assets():
    """Test at viktige statiske filer finnes"""
    print("\n📁 Testing static assets...")
    
    required_files = [
        'app/static/css/style.css',
        'app/static/js/main.js',
        'app/templates/base.html',
        'app/templates/index.html',
        'app/templates/demo.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required static assets found")
        return True

def test_environment_setup():
    """Test at miljøet er satt opp riktig"""
    print("\n⚙️ Testing environment setup...")
    
    try:
        # Test at nødvendige Python pakker er tilgjengelige
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_wtf
        import stripe
        import yfinance
        import pandas
        print("✅ All required Python packages available")
        
        # Test at konfigurasjon kan lastes
        from config import config
        dev_config = config['development']()
        print("✅ Configuration loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False

def main():
    """Hovedtest"""
    print("=" * 60)
    print("🧪 AKSJERADAR QUICK TEST")
    print("=" * 60)
    print(f"Tidspunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Static Assets", test_static_assets),
        ("App Startup", test_app_startup)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
    
    # Sammendrag
    print("\n" + "=" * 60)
    print("📊 RESULTS:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    success_rate = (passed / total) * 100
    print(f"\nOverall: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED - READY FOR GITHUB!")
        print("Du kan nå trygt pushe til GitHub.")
    elif success_rate >= 75:
        print("\n⚠️ MOSTLY GOOD - Minor issues")
        print("Applikasjonen fungerer stort sett, men det kan være mindre problemer.")
    else:
        print("\n❌ SIGNIFICANT ISSUES - FIX BEFORE PUSH")
        print("Det er viktige problemer som må fixes før push til GitHub.")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
