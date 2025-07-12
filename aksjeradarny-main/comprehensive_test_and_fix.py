#!/usr/bin/env python3
"""
Comprehensive test script to identify and fix issues in Aksjeradar
"""

import os
import sys
import subprocess
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ComprehensiveTestRunner:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': [],
            'fixes_applied': []
        }
        
    def log(self, message: str, level: str = 'INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '🔵',
            'SUCCESS': '✅', 
            'ERROR': '❌',
            'WARNING': '⚠️',
            'FIX': '🔧'
        }.get(level, '📝')
        print(f"{timestamp} {prefix} {message}")
        
    def test_imports(self) -> bool:
        """Test all critical imports"""
        self.log("Testing critical imports...")
        
        imports_to_test = [
            ("Flask", "flask"),
            ("SQLAlchemy", "sqlalchemy"),
            ("Flask-Login", "flask_login"),
            ("pandas", "pandas"),
            ("yfinance", "yfinance"),
            ("stripe", "stripe"),
            ("requests", "requests"),
            ("flask_wtf", "flask_wtf"),
            ("flask_mail", "flask_mail"),
            ("redis", "redis"),
            ("celery", "celery")
        ]
        
        all_passed = True
        for name, module in imports_to_test:
            try:
                __import__(module)
                self.log(f"Import {name}: OK", "SUCCESS")
            except ImportError as e:
                self.log(f"Import {name}: FAILED - {e}", "ERROR")
                self.test_results['errors'].append(f"Missing module: {module}")
                all_passed = False
                
        return all_passed
        
    def test_app_structure(self) -> bool:
        """Test app structure and required files"""
        self.log("Testing app structure...")
        
        required_files = [
            "app/__init__.py",
            "app/routes/__init__.py",
            "app/routes/main.py",
            "app/routes/stocks.py",
            "app/routes/analysis.py",
            "app/routes/portfolio.py",
            "app/models/__init__.py",
            "app/models/user.py",
            "app/utils/__init__.py",
            "app/utils/access_control.py",
            "app/templates/base.html",
            "app/templates/index.html",
            "config.py",
            "run.py"
        ]
        
        all_exist = True
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log(f"File {file_path}: EXISTS", "SUCCESS")
            else:
                self.log(f"File {file_path}: MISSING", "ERROR")
                self.test_results['errors'].append(f"Missing file: {file_path}")
                all_exist = False
                
        return all_exist
        
    def test_database_models(self) -> bool:
        """Test database models and relationships"""
        self.log("Testing database models...")
        
        try:
            from app import create_app
            from app.extensions import db
            from app.models.user import User
            
            app = create_app()
            with app.app_context():
                # Test User model
                user = User(username="test", email="test@test.com")
                user.set_password("test123")
                
                # Check required attributes
                required_attrs = [
                    'has_subscription', 'subscription_type', 'trial_start',
                    'trial_used', 'is_admin', 'referral_code'
                ]
                
                for attr in required_attrs:
                    if not hasattr(user, attr):
                        self.log(f"User model missing attribute: {attr}", "ERROR")
                        self.test_results['errors'].append(f"User model missing: {attr}")
                        return False
                        
                self.log("Database models OK", "SUCCESS")
                return True
                
        except Exception as e:
            self.log(f"Database model test failed: {e}", "ERROR")
            self.test_results['errors'].append(f"Database model error: {str(e)}")
            return False
            
    def test_endpoints(self) -> bool:
        """Test all app endpoints"""
        self.log("Testing endpoints...")
        
        try:
            # Start the app in test mode
            from app import create_app
            app = create_app()
            client = app.test_client()
            
            endpoints_to_test = [
                ("/", "GET", 200),
                ("/login", "GET", 200),
                ("/register", "GET", 200),
                ("/privacy", "GET", 200),
                ("/subscription", "GET", 200),
                ("/demo", "GET", 200),
                ("/api/search?q=EQNR", "GET", [200, 401]),
                ("/stocks/", "GET", [200, 302]),
                ("/analysis/", "GET", [200, 302]),
                ("/portfolio/", "GET", [200, 302])
            ]
            
            all_passed = True
            for endpoint, method, expected_status in endpoints_to_test:
                try:
                    if method == "GET":
                        response = client.get(endpoint)
                    else:
                        response = client.post(endpoint)
                        
                    expected_statuses = expected_status if isinstance(expected_status, list) else [expected_status]
                    
                    if response.status_code in expected_statuses:
                        self.log(f"{method} {endpoint}: {response.status_code} OK", "SUCCESS")
                    else:
                        self.log(f"{method} {endpoint}: {response.status_code} (expected {expected_status})", "ERROR")
                        self.test_results['errors'].append(f"Endpoint {endpoint} returned {response.status_code}")
                        all_passed = False
                        
                except Exception as e:
                    self.log(f"{method} {endpoint}: ERROR - {e}", "ERROR")
                    self.test_results['errors'].append(f"Endpoint {endpoint} error: {str(e)}")
                    all_passed = False
                    
            return all_passed
            
        except Exception as e:
            self.log(f"Endpoint testing failed: {e}", "ERROR")
            return False
            
    def fix_missing_files(self):
        """Create any missing critical files"""
        self.log("Checking and fixing missing files...")
        
        # Create missing __init__.py files
        init_dirs = [
            "app",
            "app/routes",
            "app/models", 
            "app/utils",
            "app/services",
            "app/templates",
            "app/static"
        ]
        
        for dir_path in init_dirs:
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                os.makedirs(dir_path, exist_ok=True)
                with open(init_file, 'w') as f:
                    f.write("# Auto-generated __init__.py\n")
                self.log(f"Created {init_file}", "FIX")
                self.test_results['fixes_applied'].append(f"Created {init_file}")
                
    def fix_config_issues(self):
        """Fix common configuration issues"""
        self.log("Checking configuration...")
        
        # Check if config.py exists
        if not os.path.exists("config.py"):
            self.log("Creating default config.py", "FIX")
            config_content = '''import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Mail config
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 25))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Stripe config
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_dummy')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_dummy')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_dummy')
    
    # App config
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    TESTING = False
'''
            with open("config.py", 'w') as f:
                f.write(config_content)
            self.test_results['fixes_applied'].append("Created config.py")
            
    def fix_run_py(self):
        """Ensure run.py exists and is correct"""
        if not os.path.exists("run.py"):
            self.log("Creating run.py", "FIX")
            run_content = '''#!/usr/bin/env python3
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
            with open("run.py", 'w') as f:
                f.write(run_content)
            os.chmod("run.py", 0o755)
            self.test_results['fixes_applied'].append("Created run.py")
            
    def test_access_control(self) -> bool:
        """Test access control implementation"""
        self.log("Testing access control...")
        
        try:
            from app.utils.access_control import access_required, UNRESTRICTED_ENDPOINTS, EXEMPT_EMAILS
            
            # Check if decorator exists
            if not callable(access_required):
                self.log("access_required decorator not callable", "ERROR")
                return False
                
            # Check unrestricted endpoints
            expected_unrestricted = {
                'main.register', 'main.login', 'main.logout',
                'main.privacy', 'main.subscription', 'main.demo'
            }
            
            missing = expected_unrestricted - UNRESTRICTED_ENDPOINTS
            if missing:
                self.log(f"Missing unrestricted endpoints: {missing}", "WARNING")
                self.test_results['warnings'].append(f"Missing unrestricted endpoints: {missing}")
                
            # Check exempt emails
            if not EXEMPT_EMAILS:
                self.log("No exempt emails defined", "WARNING")
                self.test_results['warnings'].append("No exempt emails defined")
                
            self.log("Access control OK", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Access control test failed: {e}", "ERROR")
            self.test_results['errors'].append(f"Access control error: {str(e)}")
            return False
            
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("🚀 COMPREHENSIVE TEST REPORT")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nTotal Tests: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['errors']:
            print(f"\n❌ ERRORS ({len(self.test_results['errors'])}):")
            for error in self.test_results['errors']:
                print(f"   • {error}")
                
        if self.test_results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(self.test_results['warnings'])}):")
            for warning in self.test_results['warnings']:
                print(f"   • {warning}")
                
        if self.test_results['fixes_applied']:
            print(f"\n🔧 FIXES APPLIED ({len(self.test_results['fixes_applied'])}):")
            for fix in self.test_results['fixes_applied']:
                print(f"   • {fix}")
                
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
    def run_all_tests(self):
        """Run all tests and fixes"""
        print("🔍 STARTING COMPREHENSIVE SYSTEM TEST")
        print("="*60)
        
        # Apply fixes first
        self.fix_missing_files()
        self.fix_config_issues()
        self.fix_run_py()
        
        # Run tests
        tests = [
            ("Import Test", self.test_imports),
            ("App Structure", self.test_app_structure),
            ("Database Models", self.test_database_models),
            ("Access Control", self.test_access_control),
            ("Endpoints", self.test_endpoints)
        ]
        
        for test_name, test_func in tests:
            self.test_results['total_tests'] += 1
            try:
                if test_func():
                    self.test_results['passed'] += 1
                else:
                    self.test_results['failed'] += 1
            except Exception as e:
                self.log(f"{test_name} crashed: {e}", "ERROR")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"{test_name} crashed: {str(e)}")
                
        # Generate report
        self.generate_report()

def main():
    """Main entry point"""
    runner = ComprehensiveTestRunner()
    runner.run_all_tests()
    
    # Return exit code based on results
    if runner.test_results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
