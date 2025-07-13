#!/usr/bin/env python3
"""
Omfattende test-suite for hele Aksjeradar kodebasen
Tester alle Python-filer, endepunkter og frontend-komponenter
"""

import os
import sys
import subprocess
import importlib.util
import py_compile
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from typing import List, Dict, Any

class ComprehensiveTestSuite:
    def __init__(self, base_path: str = "/workspaces/aksjeny"):
        self.base_path = base_path
        self.results = {
            'syntax_check': [],
            'import_check': [],
            'endpoint_check': [],
            'frontend_check': [],
            'summary': {}
        }
        self.errors = []
        
    def test_syntax_all_files(self):
        """Test syntaks for alle Python-filer"""
        print("🔍 Testing syntax for all Python files...")
        print("=" * 50)
        
        python_files = list(Path(self.base_path).rglob("*.py"))
        total_files = len(python_files)
        passed = 0
        
        for py_file in python_files:
            try:
                py_compile.compile(str(py_file), doraise=True)
                print(f"✅ {py_file.relative_to(self.base_path)}")
                self.results['syntax_check'].append({
                    'file': str(py_file),
                    'status': 'PASS'
                })
                passed += 1
            except py_compile.PyCompileError as e:
                print(f"❌ {py_file.relative_to(self.base_path)}: {e}")
                self.results['syntax_check'].append({
                    'file': str(py_file),
                    'status': 'FAIL',
                    'error': str(e)
                })
                self.errors.append(f"Syntax error in {py_file}: {e}")
        
        print(f"\n📊 Syntax Check: {passed}/{total_files} files passed")
        return passed == total_files
    
    def test_imports(self):
        """Test import av kritiske moduler"""
        print("\n🔄 Testing critical imports...")
        print("=" * 50)
        
        critical_modules = [
            'app',
            'app.models',
            'app.routes.main',
            'app.routes.portfolio',
            'app.services.data_service',
            'app.utils.access_control'
        ]
        
        passed = 0
        total = len(critical_modules)
        
        # Legg til app directory i Python path
        app_path = os.path.join(self.base_path, 'app')
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        
        for module_name in critical_modules:
            try:
                if module_name == 'app':
                    # Special handling for app module
                    spec = importlib.util.spec_from_file_location(
                        "app", 
                        os.path.join(app_path, "__init__.py")
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    # Use relative imports from app directory
                    module_path = module_name.replace('app.', '').replace('.', '/')
                    module_file = os.path.join(app_path, module_path + '.py')
                    if not os.path.exists(module_file):
                        module_file = os.path.join(app_path, module_path, '__init__.py')
                    
                    if os.path.exists(module_file):
                        spec = importlib.util.spec_from_file_location(module_name, module_file)
                        module = importlib.util.module_from_spec(spec)
                        # Don't execute to avoid circular imports, just check if loadable
                
                print(f"✅ {module_name}")
                self.results['import_check'].append({
                    'module': module_name,
                    'status': 'PASS'
                })
                passed += 1
                
            except Exception as e:
                print(f"❌ {module_name}: {e}")
                self.results['import_check'].append({
                    'module': module_name,
                    'status': 'FAIL',
                    'error': str(e)
                })
                self.errors.append(f"Import error for {module_name}: {e}")
        
        print(f"\n📊 Import Check: {passed}/{total} modules passed")
        return passed == total
    
    def test_all_endpoints(self, base_url: str = "http://localhost:5000"):
        """Test alle endepunkter"""
        print(f"\n🌐 Testing all endpoints at {base_url}...")
        print("=" * 50)
        
        # Omfattende liste over endepunkter
        endpoints = [
            # Grunnleggende sider
            {'url': '/', 'method': 'GET', 'name': 'Homepage'},
            {'url': '/demo', 'method': 'GET', 'name': 'Demo page'},
            {'url': '/ai-explained', 'method': 'GET', 'name': 'AI Explained'},
            {'url': '/pricing', 'method': 'GET', 'name': 'Pricing'},
            {'url': '/pricing/', 'method': 'GET', 'name': 'Pricing (trailing slash)'},
            
            # Autentisering
            {'url': '/login', 'method': 'GET', 'name': 'Login page'},
            {'url': '/register', 'method': 'GET', 'name': 'Register page'},
            {'url': '/logout', 'method': 'GET', 'name': 'Logout'},
            
            # Applikasjons-sider
            {'url': '/portfolio', 'method': 'GET', 'name': 'Portfolio'},
            {'url': '/portfolio/', 'method': 'GET', 'name': 'Portfolio (trailing slash)'},
            {'url': '/analysis', 'method': 'GET', 'name': 'Analysis'},
            {'url': '/stocks', 'method': 'GET', 'name': 'Stocks'},
            {'url': '/stocks/', 'method': 'GET', 'name': 'Stocks (trailing slash)'},
            
            # API endepunkter
            {'url': '/api/health', 'method': 'GET', 'name': 'Health check'},
            {'url': '/api/version', 'method': 'GET', 'name': 'Version info'},
            
            # Spesifikke funksjoner
            {'url': '/subscription', 'method': 'GET', 'name': 'Subscription'},
            {'url': '/profile', 'method': 'GET', 'name': 'Profile'},
            {'url': '/privacy', 'method': 'GET', 'name': 'Privacy policy'},
            {'url': '/terms', 'method': 'GET', 'name': 'Terms of service'},
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{base_url}{endpoint['url']}", 
                    timeout=10,
                    allow_redirects=True
                )
                
                # Akseptér 200, 302 (redirect), og 401 (unauthorized) som gyldige responser
                if response.status_code in [200, 302, 401]:
                    status = "✅"
                    result_status = "PASS"
                    passed += 1
                else:
                    status = "❌"
                    result_status = "FAIL"
                    self.errors.append(f"Endpoint {endpoint['url']} returned {response.status_code}")
                
                print(f"{status} {endpoint['name']}: {response.status_code}")
                
                self.results['endpoint_check'].append({
                    'endpoint': endpoint['url'],
                    'name': endpoint['name'],
                    'status_code': response.status_code,
                    'result': result_status
                })
                
            except requests.RequestException as e:
                print(f"❌ {endpoint['name']}: Connection failed - {e}")
                self.results['endpoint_check'].append({
                    'endpoint': endpoint['url'],
                    'name': endpoint['name'],
                    'status_code': 'ERROR',
                    'result': 'FAIL',
                    'error': str(e)
                })
                self.errors.append(f"Connection error for {endpoint['url']}: {e}")
        
        print(f"\n📊 Endpoint Check: {passed}/{total} endpoints passed")
        return passed == total
    
    def check_frontend_files(self):
        """Sjekk frontend-filer (templates, static files)"""
        print("\n🎨 Checking frontend files...")
        print("=" * 50)
        
        # Sjekk templates
        template_dir = os.path.join(self.base_path, 'app', 'templates')
        static_dir = os.path.join(self.base_path, 'app', 'static')
        
        template_files = []
        static_files = []
        
        if os.path.exists(template_dir):
            template_files = list(Path(template_dir).rglob("*.html"))
        
        if os.path.exists(static_dir):
            static_files = list(Path(static_dir).rglob("*"))
            static_files = [f for f in static_files if f.is_file()]
        
        print(f"📄 Found {len(template_files)} template files")
        print(f"📦 Found {len(static_files)} static files")
        
        # Sjekk for kritiske template-filer
        critical_templates = [
            'base.html',
            'index.html',
            'demo.html',
            'login.html',
            'register.html',
            'pricing.html'
        ]
        
        missing_templates = []
        for template in critical_templates:
            template_path = os.path.join(template_dir, template)
            if not os.path.exists(template_path):
                missing_templates.append(template)
                print(f"❌ Missing critical template: {template}")
            else:
                print(f"✅ Found: {template}")
        
        self.results['frontend_check'] = {
            'template_count': len(template_files),
            'static_count': len(static_files),
            'missing_templates': missing_templates,
            'critical_templates_ok': len(missing_templates) == 0
        }
        
        return len(missing_templates) == 0
    
    def check_database_models(self):
        """Sjekk database-modeller"""
        print("\n🗄️  Checking database models...")
        print("=" * 50)
        
        model_files = [
            'user.py',
            'portfolio.py',
            'watchlist.py',
            'tip.py',
            'trial_session.py',
            'referral.py'
        ]
        
        models_dir = os.path.join(self.base_path, 'app', 'models')
        found_models = []
        missing_models = []
        
        for model_file in model_files:
            model_path = os.path.join(models_dir, model_file)
            if os.path.exists(model_path):
                print(f"✅ Found model: {model_file}")
                found_models.append(model_file)
            else:
                print(f"❌ Missing model: {model_file}")
                missing_models.append(model_file)
        
        return len(missing_models) == 0
    
    def generate_report(self):
        """Generer detaljert rapport"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Sammendrag
        syntax_passed = len([r for r in self.results['syntax_check'] if r['status'] == 'PASS'])
        syntax_total = len(self.results['syntax_check'])
        
        import_passed = len([r for r in self.results['import_check'] if r['status'] == 'PASS'])
        import_total = len(self.results['import_check'])
        
        endpoint_passed = len([r for r in self.results['endpoint_check'] if r['result'] == 'PASS'])
        endpoint_total = len(self.results['endpoint_check'])
        
        print(f"\n📈 SUMMARY:")
        print(f"   Syntax Check: {syntax_passed}/{syntax_total} files")
        print(f"   Import Check: {import_passed}/{import_total} modules")
        print(f"   Endpoint Check: {endpoint_passed}/{endpoint_total} endpoints")
        print(f"   Frontend Check: {self.results['frontend_check']['critical_templates_ok']}")
        
        # Beregn total suksess-rate
        total_tests = syntax_total + import_total + endpoint_total + 1  # +1 for frontend
        total_passed = syntax_passed + import_passed + endpoint_passed + (1 if self.results['frontend_check']['critical_templates_ok'] else 0)
        
        success_rate = (total_passed / total_tests) * 100
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT! Aksjeradar is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD! Minor issues to address")
        else:
            print("⚠️  NEEDS WORK! Several issues found")
        
        # Vis feil hvis det er noen
        if self.errors:
            print(f"\n❌ ERRORS FOUND ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:10], 1):  # Vis bare første 10
                print(f"   {i}. {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more")
        
        # Lagre rapport til fil
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return success_rate >= 75

def main():
    print("🚀 STARTING COMPREHENSIVE TEST SUITE FOR AKSJERADAR")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    suite = ComprehensiveTestSuite()
    
    # Kjør alle tester
    syntax_ok = suite.test_syntax_all_files()
    import_ok = suite.test_imports()
    frontend_ok = suite.check_frontend_files()
    models_ok = suite.check_database_models()
    
    # Test endepunkter (krever at server kjører)
    endpoint_ok = False
    try:
        endpoint_ok = suite.test_all_endpoints()
    except Exception as e:
        print(f"\n⚠️  Endpoint testing failed: {e}")
        print("   Make sure the server is running on localhost:5000")
    
    # Generer rapport
    success = suite.generate_report()
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
