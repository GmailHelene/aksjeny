#!/usr/bin/env python3
"""
Omfattende test av alle filer, endepunkter og funksjonalitet i Aksjeradar
For produksjon på aksjeradar.trade
"""
import os
import sys
import subprocess
import requests
import time
import glob
from datetime import datetime
from pathlib import Path
import json

class AksjeradarProductionTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            'files': [],
            'endpoints': [],
            'features': [],
            'errors': []
        }
        self.production_ready = True
        
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print('='*60)
        
    def print_status(self, status, message, details=None):
        """Print status with icon"""
        icon = "✅" if status else "❌"
        print(f"{icon} {message}")
        if details:
            print(f"   💡 {details}")
        if not status:
            self.production_ready = False
            
    def test_file_structure(self):
        """Test critical file structure"""
        self.print_header("FILE STRUCTURE TEST")
        
        critical_files = [
            # Core application files
            '/workspaces/aksjeny/app/__init__.py',
            '/workspaces/aksjeny/app/extensions.py',
            '/workspaces/aksjeny/app/models/__init__.py',
            '/workspaces/aksjeny/app/models/user.py',
            '/workspaces/aksjeny/app/models/portfolio.py',
            '/workspaces/aksjeny/app/models/tip.py',
            
            # Routes
            '/workspaces/aksjeny/app/routes/main.py',
            '/workspaces/aksjeny/app/routes/portfolio.py',
            '/workspaces/aksjeny/app/routes/analysis.py',
            '/workspaces/aksjeny/app/routes/stocks.py',
            
            # Templates
            '/workspaces/aksjeny/app/templates/base.html',
            '/workspaces/aksjeny/app/templates/index.html',
            '/workspaces/aksjeny/app/templates/demo.html',
            '/workspaces/aksjeny/app/templates/pricing.html',
            '/workspaces/aksjeny/app/templates/login.html',
            '/workspaces/aksjeny/app/templates/register.html',
            
            # Static files
            '/workspaces/aksjeny/app/static/css/main.css',
            '/workspaces/aksjeny/app/static/js/main.js',
            '/workspaces/aksjeny/app/static/manifest.json',
            
            # Configuration
            '/workspaces/aksjeny/app/config.py',
            '/workspaces/aksjeny/app/requirements.txt',
            '/workspaces/aksjeny/app/Procfile',
            '/workspaces/aksjeny/app/wsgi.py',
            
            # Deployment
            '/workspaces/aksjeny/app/railway_deploy.sh',
            '/workspaces/aksjeny/app/deploy.sh'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                self.print_status(True, f"Found: {file_path}")
                self.test_results['files'].append({'path': file_path, 'status': 'found'})
            else:
                self.print_status(False, f"Missing: {file_path}")
                self.test_results['files'].append({'path': file_path, 'status': 'missing'})
                
    def test_python_syntax(self):
        """Test Python syntax in all .py files"""
        self.print_header("PYTHON SYNTAX TEST")
        
        python_files = glob.glob('/workspaces/aksjeny/app/**/*.py', recursive=True)
        syntax_errors = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file, 'exec')
                self.print_status(True, f"Syntax OK: {py_file}")
            except SyntaxError as e:
                self.print_status(False, f"Syntax Error: {py_file}", f"Line {e.lineno}: {e.msg}")
                syntax_errors += 1
            except Exception as e:
                self.print_status(False, f"Error reading: {py_file}", str(e))
                
        if syntax_errors == 0:
            self.print_status(True, f"All {len(python_files)} Python files have valid syntax")
        else:
            self.print_status(False, f"{syntax_errors} Python files have syntax errors")
            
    def test_imports(self):
        """Test critical imports"""
        self.print_header("IMPORT TEST")
        
        critical_imports = [
            'flask',
            'flask_login',
            'flask_sqlalchemy',
            'flask_wtf',
            'werkzeug',
            'requests',
            'pandas',
            'numpy',
            'yfinance',
            'sqlalchemy'
        ]
        
        for module in critical_imports:
            try:
                __import__(module)
                self.print_status(True, f"Import OK: {module}")
            except ImportError as e:
                self.print_status(False, f"Import Error: {module}", str(e))
                
    def test_endpoints(self):
        """Test all critical endpoints"""
        self.print_header("ENDPOINT TEST")
        
        endpoints = [
            # Public pages
            {'url': '/', 'method': 'GET', 'expected': 200, 'description': 'Homepage'},
            {'url': '/demo', 'method': 'GET', 'expected': 200, 'description': 'Demo page'},
            {'url': '/ai-explained', 'method': 'GET', 'expected': 200, 'description': 'AI explanation'},
            {'url': '/pricing', 'method': 'GET', 'expected': 200, 'description': 'Pricing page'},
            {'url': '/pricing/', 'method': 'GET', 'expected': 200, 'description': 'Pricing page (trailing slash)'},
            {'url': '/login', 'method': 'GET', 'expected': 200, 'description': 'Login page'},
            {'url': '/register', 'method': 'GET', 'expected': 200, 'description': 'Register page'},
            
            # API endpoints
            {'url': '/api/health', 'method': 'GET', 'expected': 200, 'description': 'Health check'},
            {'url': '/api/version', 'method': 'GET', 'expected': 200, 'description': 'Version info'},
            
            # Protected pages (should redirect or show access control)
            {'url': '/portfolio', 'method': 'GET', 'expected': [200, 302], 'description': 'Portfolio page'},
            {'url': '/analysis', 'method': 'GET', 'expected': [200, 302], 'description': 'Analysis page'},
            {'url': '/stocks', 'method': 'GET', 'expected': [200, 302], 'description': 'Stocks page'},
            
            # Static files
            {'url': '/static/css/main.css', 'method': 'GET', 'expected': [200, 404], 'description': 'Main CSS'},
            {'url': '/static/js/main.js', 'method': 'GET', 'expected': [200, 404], 'description': 'Main JS'},
            {'url': '/static/manifest.json', 'method': 'GET', 'expected': [200, 404], 'description': 'PWA Manifest'},
            
            # Error pages
            {'url': '/nonexistent', 'method': 'GET', 'expected': 404, 'description': 'Non-existent page'},
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint['url']}", 
                    timeout=10,
                    allow_redirects=False
                )
                
                expected = endpoint['expected']
                if isinstance(expected, list):
                    status_ok = response.status_code in expected
                else:
                    status_ok = response.status_code == expected
                
                self.print_status(
                    status_ok, 
                    f"{endpoint['description']}: {response.status_code}",
                    f"URL: {endpoint['url']}"
                )
                
                self.test_results['endpoints'].append({
                    'url': endpoint['url'],
                    'status': response.status_code,
                    'success': status_ok,
                    'description': endpoint['description']
                })
                
            except requests.exceptions.RequestException as e:
                self.print_status(False, f"{endpoint['description']}: Connection Error", str(e))
                self.test_results['endpoints'].append({
                    'url': endpoint['url'],
                    'status': 'error',
                    'success': False,
                    'error': str(e)
                })
                
    def test_database_models(self):
        """Test database models"""
        self.print_header("DATABASE MODELS TEST")
        
        try:
            # Test basic import
            sys.path.insert(0, '/workspaces/aksjeny/app')
            from models import User, Portfolio, StockTip
            self.print_status(True, "Database models imported successfully")
            
            # Test model attributes
            user_attrs = ['id', 'username', 'email', 'password_hash']
            for attr in user_attrs:
                if hasattr(User, attr):
                    self.print_status(True, f"User model has {attr} attribute")
                else:
                    self.print_status(False, f"User model missing {attr} attribute")
                    
        except Exception as e:
            self.print_status(False, "Database models import failed", str(e))
            
    def test_configuration(self):
        """Test configuration files"""
        self.print_header("CONFIGURATION TEST")
        
        # Test requirements.txt
        req_file = '/workspaces/aksjeny/app/requirements.txt'
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                requirements = f.read()
                required_packages = ['flask', 'flask-login', 'flask-sqlalchemy', 'requests']
                
                for package in required_packages:
                    if package.lower() in requirements.lower():
                        self.print_status(True, f"Requirements contains {package}")
                    else:
                        self.print_status(False, f"Requirements missing {package}")
        else:
            self.print_status(False, "requirements.txt not found")
            
        # Test Procfile for Railway deployment
        procfile = '/workspaces/aksjeny/app/Procfile'
        if os.path.exists(procfile):
            with open(procfile, 'r') as f:
                content = f.read()
                if 'web:' in content:
                    self.print_status(True, "Procfile contains web process")
                else:
                    self.print_status(False, "Procfile missing web process")
        else:
            self.print_status(False, "Procfile not found")
            
    def test_production_readiness(self):
        """Test production readiness"""
        self.print_header("PRODUCTION READINESS TEST")
        
        # Test environment variables
        env_vars = [
            'SECRET_KEY',
            'DATABASE_URL',
            'FLASK_ENV',
            'STRIPE_SECRET_KEY',
            'STRIPE_PUBLISHABLE_KEY'
        ]
        
        for var in env_vars:
            if var in os.environ:
                self.print_status(True, f"Environment variable {var} is set")
            else:
                self.print_status(False, f"Environment variable {var} is missing", 
                                "Set in Railway dashboard or .env file")
                
        # Test CSRF protection
        try:
            response = requests.post(f"{self.base_url}/login", data={}, timeout=5)
            if 'csrf' in response.text.lower() or response.status_code in [400, 403]:
                self.print_status(True, "CSRF protection is active")
            else:
                self.print_status(False, "CSRF protection may not be working")
        except:
            self.print_status(False, "Could not test CSRF protection")
            
    def test_mobile_responsiveness(self):
        """Test mobile responsiveness"""
        self.print_header("MOBILE RESPONSIVENESS TEST")
        
        try:
            # Test with mobile user agent
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
            }
            
            response = requests.get(f"{self.base_url}/", headers=mobile_headers, timeout=5)
            if response.status_code == 200:
                if 'viewport' in response.text:
                    self.print_status(True, "Mobile viewport meta tag found")
                else:
                    self.print_status(False, "Mobile viewport meta tag missing")
                    
                if 'bootstrap' in response.text.lower() or 'responsive' in response.text.lower():
                    self.print_status(True, "Responsive framework detected")
                else:
                    self.print_status(False, "No responsive framework detected")
            else:
                self.print_status(False, f"Mobile test failed with status {response.status_code}")
                
        except Exception as e:
            self.print_status(False, "Mobile responsiveness test failed", str(e))
            
    def test_security_headers(self):
        """Test security headers"""
        self.print_header("SECURITY HEADERS TEST")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000'
            }
            
            for header, expected in security_headers.items():
                if header in headers:
                    self.print_status(True, f"Security header {header} is present")
                else:
                    self.print_status(False, f"Security header {header} is missing")
                    
        except Exception as e:
            self.print_status(False, "Security headers test failed", str(e))
            
    def generate_report(self):
        """Generate final test report"""
        self.print_header("FINAL TEST REPORT")
        
        # Count results
        total_files = len(self.test_results['files'])
        found_files = len([f for f in self.test_results['files'] if f['status'] == 'found'])
        
        total_endpoints = len(self.test_results['endpoints'])
        working_endpoints = len([e for e in self.test_results['endpoints'] if e['success']])
        
        print(f"📁 Files: {found_files}/{total_files} found")
        print(f"🌐 Endpoints: {working_endpoints}/{total_endpoints} working")
        
        if self.production_ready:
            print(f"\n🎉 PRODUCTION READY!")
            print(f"✅ Aksjeradar is ready for deployment to aksjeradar.trade")
            print(f"🚀 All critical tests passed successfully")
        else:
            print(f"\n⚠️  ISSUES FOUND")
            print(f"❌ Some tests failed - review errors above")
            print(f"🔧 Fix issues before deploying to production")
            
        # Save detailed report
        report_file = f"/tmp/aksjeradar_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        print(f"📄 Detailed report saved to: {report_file}")
        
        return self.production_ready
        
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive Aksjeradar testing...")
        print(f"🎯 Target: Production deployment to aksjeradar.trade")
        print(f"⏰ Started: {datetime.now()}")
        
        # Run all test suites
        self.test_file_structure()
        self.test_python_syntax()
        self.test_imports()
        self.test_endpoints()
        self.test_database_models()
        self.test_configuration()
        self.test_production_readiness()
        self.test_mobile_responsiveness()
        self.test_security_headers()
        
        # Generate final report
        return self.generate_report()

def main():
    """Main test runner"""
    base_url = "http://localhost:5000"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"✅ Server is running at {base_url}")
    except:
        print(f"❌ Server is not running at {base_url}")
        print("🔧 Please start the server first:")
        print("   cd /workspaces/aksjeny/app && python standalone_test_server.py")
        return False
    
    # Run tests
    tester = AksjeradarProductionTester(base_url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
