#!/usr/bin/env python3
"""
Pre-GitHub push test - sjekker at alt fungerer som forventet
"""
import sys
import os
import traceback
import requests
from datetime import datetime

# Legg til prosjektets rot til Python path
sys.path.insert(0, os.path.abspath('.'))

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_test(message, success=True):
    """Log test resultat med farge"""
    color = Color.GREEN if success else Color.RED
    symbol = "✅" if success else "❌"
    print(f"{color}{symbol} {message}{Color.END}")

def test_basic_imports():
    """Test grunnleggende imports"""
    print(f"{Color.BLUE}🔍 Testing Basic Imports{Color.END}")
    print("-" * 40)
    
    try:
        import flask
        log_test(f"Flask import OK (version: {flask.__version__})")
        
        from app import create_app
        log_test("App import OK")
        
        from app.extensions import db
        log_test("Extensions import OK")
        
        from app.models.user import User
        log_test("User model import OK")
        
        return True
    except Exception as e:
        log_test(f"Import error: {e}", False)
        traceback.print_exc()
        return False

def test_app_creation():
    """Test app creation"""
    print(f"\n{Color.BLUE}🚀 Testing App Creation{Color.END}")
    print("-" * 40)
    
    try:
        from app import create_app
        app = create_app()
        log_test("App creation OK")
        
        # Test app context
        with app.app_context():
            log_test("App context OK")
            
            # Test database connection
            from app.extensions import db
            db.create_all()
            log_test("Database creation OK")
            
        return True
    except Exception as e:
        log_test(f"App creation error: {e}", False)
        traceback.print_exc()
        return False

def test_key_routes():
    """Test nøkkel-ruter"""
    print(f"\n{Color.BLUE}🔗 Testing Key Routes{Color.END}")
    print("-" * 40)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test homepage
            response = client.get('/')
            log_test(f"Homepage: {response.status_code}", response.status_code in [200, 302])
            
            # Test demo page
            response = client.get('/demo')
            log_test(f"Demo page: {response.status_code}", response.status_code in [200, 302])
            
            # Test pricing page
            response = client.get('/pricing/')
            log_test(f"Pricing page: {response.status_code}", response.status_code in [200, 302])
            
            # Test login page
            response = client.get('/auth/login')
            log_test(f"Login page: {response.status_code}", response.status_code in [200, 302])
            
            # Test register page
            response = client.get('/auth/register')
            log_test(f"Register page: {response.status_code}", response.status_code in [200, 302])
            
        return True
    except Exception as e:
        log_test(f"Route testing error: {e}", False)
        traceback.print_exc()
        return False

def test_static_files():
    """Test at statiske filer finnes"""
    print(f"\n{Color.BLUE}📁 Testing Static Files{Color.END}")
    print("-" * 40)
    
    static_files = [
        'static/css/style.css',
        'static/js/main.js',
        'static/images/logo.png',
        'static/favicon.ico'
    ]
    
    all_good = True
    for file_path in static_files:
        full_path = os.path.join(os.getcwd(), file_path)
        exists = os.path.exists(full_path)
        log_test(f"{file_path}: {'Found' if exists else 'Missing'}", exists)
        if not exists:
            all_good = False
    
    return all_good

def test_templates():
    """Test at viktige templates finnes"""
    print(f"\n{Color.BLUE}📄 Testing Templates{Color.END}")
    print("-" * 40)
    
    templates = [
        'templates/base.html',
        'templates/index.html',
        'templates/demo.html',
        'templates/pricing/index.html',
        'templates/auth/login.html',
        'templates/auth/register.html'
    ]
    
    all_good = True
    for template in templates:
        full_path = os.path.join(os.getcwd(), template)
        exists = os.path.exists(full_path)
        log_test(f"{template}: {'Found' if exists else 'Missing'}", exists)
        if not exists:
            all_good = False
    
    return all_good

def test_config_files():
    """Test konfigurasjonsfiler"""
    print(f"\n{Color.BLUE}⚙️ Testing Config Files{Color.END}")
    print("-" * 40)
    
    config_files = [
        'requirements.txt',
        'config.py',
        'run.py',
        'README.md'
    ]
    
    all_good = True
    for config_file in config_files:
        full_path = os.path.join(os.getcwd(), config_file)
        exists = os.path.exists(full_path)
        log_test(f"{config_file}: {'Found' if exists else 'Missing'}", exists)
        if not exists:
            all_good = False
    
    return all_good

def test_database_models():
    """Test database modeller"""
    print(f"\n{Color.BLUE}🗄️ Testing Database Models{Color.END}")
    print("-" * 40)
    
    try:
        from app import create_app
        from app.models.user import User
        from app.models.watchlist import Watchlist
        from app.models.portfolio import Portfolio
        from app.extensions import db
        
        app = create_app()
        with app.app_context():
            # Test model creation
            db.create_all()
            log_test("Database models created successfully")
            
            # Test basic model functionality
            user_count = User.query.count()
            log_test(f"User model accessible (count: {user_count})")
            
        return True
    except Exception as e:
        log_test(f"Database model error: {e}", False)
        traceback.print_exc()
        return False

def test_services():
    """Test services"""
    print(f"\n{Color.BLUE}🔧 Testing Services{Color.END}")
    print("-" * 40)
    
    try:
        from app.services.data_service import DataService
        log_test("DataService import OK")
        
        from app.services.analysis_service import AnalysisService
        log_test("AnalysisService import OK")
        
        # Test basic service functionality
        test_data = DataService.get_fallback_data()
        log_test(f"DataService fallback data: {len(test_data) if test_data else 0} items")
        
        return True
    except Exception as e:
        log_test(f"Services error: {e}", False)
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Kjør alle tester"""
    print(f"{Color.BOLD}🧪 AKSJERADAR PRE-GITHUB PUSH TEST{Color.END}")
    print("=" * 60)
    print(f"Tidspunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("App Creation", test_app_creation),
        ("Key Routes", test_key_routes),
        ("Static Files", test_static_files),
        ("Templates", test_templates),
        ("Config Files", test_config_files),
        ("Database Models", test_database_models),
        ("Services", test_services)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            log_test(f"{test_name} failed with exception: {e}", False)
            results.append((test_name, False))
    
    # Sammendrag
    print(f"\n{Color.BOLD}📊 TEST RESULTS SUMMARY{Color.END}")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        color = Color.GREEN if result else Color.RED
        print(f"{color}{test_name}: {status}{Color.END}")
    
    print("-" * 60)
    success_rate = (passed / total) * 100
    overall_color = Color.GREEN if success_rate >= 80 else Color.YELLOW if success_rate >= 60 else Color.RED
    print(f"{overall_color}Overall: {passed}/{total} tests passed ({success_rate:.1f}%){Color.END}")
    
    if success_rate >= 80:
        print(f"\n{Color.GREEN}🎉 APP IS READY FOR GITHUB PUSH!{Color.END}")
    elif success_rate >= 60:
        print(f"\n{Color.YELLOW}⚠️ App has some issues but might be deployable{Color.END}")
    else:
        print(f"\n{Color.RED}❌ App needs fixes before GitHub push{Color.END}")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
