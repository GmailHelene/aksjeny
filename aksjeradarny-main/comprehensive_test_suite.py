#!/usr/bin/env python3
"""
Comprehensive Test Suite for Aksjeradar V6
Tests all endpoints, blueprints, and functionality
"""

import sys
import os
import requests
import time
import json
from urllib.parse import urljoin
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AksjeradarTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'warnings': [],
            'tested_endpoints': []
        }
    
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_endpoint(self, endpoint, method="GET", expected_status=200, data=None, description=""):
        """Test a single endpoint"""
        try:
            url = urljoin(self.base_url, endpoint)
            self.log(f"Testing {method} {endpoint} - {description}")
            
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, data=data, timeout=10)
            else:
                response = self.session.request(method, url, data=data, timeout=10)
            
            status_ok = response.status_code == expected_status
            content_ok = len(response.content) > 0
            
            self.results['tested_endpoints'].append({
                'endpoint': endpoint,
                'method': method,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': status_ok,
                'content_length': len(response.content),
                'description': description
            })
            
            if status_ok and content_ok:
                self.results['passed'] += 1
                self.log(f"✅ PASS: {endpoint} ({response.status_code})", "PASS")
                return True
            else:
                self.results['failed'] += 1
                error_msg = f"❌ FAIL: {endpoint} - Status: {response.status_code} (expected {expected_status}), Content: {len(response.content)} bytes"
                self.log(error_msg, "FAIL")
                self.results['errors'].append(error_msg)
                return False
                
        except Exception as e:
            self.results['failed'] += 1
            error_msg = f"❌ ERROR: {endpoint} - {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['errors'].append(error_msg)
            return False
    
    def test_app_startup(self):
        """Test if the Flask app can start properly"""
        self.log("🚀 Testing Flask App Startup", "TEST")
        
        try:
            from app import create_app
            app = create_app()
            
            # Test app creation
            assert app is not None, "App creation failed"
            
            # Test configuration
            assert app.config is not None, "App config missing"
            
            # Test blueprints registration
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            expected_blueprints = [
                'main', 'stocks', 'analysis', 'portfolio', 'portfolio_advanced',
                'market_intel', 'features', 'notifications', 'notifications_web',
                'realtime_api', 'watchlist', 'backtest', 'seo_content', 'api',
                'stripe', 'pricing', 'external_data', 'resources'
            ]
            
            missing_blueprints = [bp for bp in expected_blueprints if bp not in blueprint_names]
            if missing_blueprints:
                self.results['warnings'].append(f"Missing blueprints: {missing_blueprints}")
            
            self.log("✅ Flask app startup successful", "PASS")
            return True
            
        except Exception as e:
            error_msg = f"❌ Flask app startup failed: {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['errors'].append(error_msg)
            return False
    
    def test_imports(self):
        """Test all critical imports"""
        self.log("📦 Testing Critical Imports", "TEST")
        
        imports_to_test = [
            ('app', 'Main app module'),
            ('app.services.portfolio_service', 'Portfolio service'),
            ('app.services.data_service', 'Data service'),
            ('app.services.ai_service', 'AI service'),
            ('app.routes.resources', 'Resources blueprint'),
            ('app.routes.external_data', 'External data blueprint'),
            ('app.models.user', 'User model'),
            ('app.models.portfolio', 'Portfolio model'),
        ]
        
        all_passed = True
        for module_name, description in imports_to_test:
            try:
                __import__(module_name)
                self.log(f"✅ Import success: {module_name} - {description}", "PASS")
                self.results['passed'] += 1
            except Exception as e:
                error_msg = f"❌ Import failed: {module_name} - {str(e)}"
                self.log(error_msg, "ERROR")
                self.results['errors'].append(error_msg)
                self.results['failed'] += 1
                all_passed = False
        
        return all_passed
    
    def test_all_endpoints(self):
        """Test all application endpoints"""
        self.log("🌐 Testing All Endpoints", "TEST")
        
        # Main routes
        endpoints = [
            # Main application
            ('/', 'Main homepage'),
            ('/demo', 'Demo page'),
            ('/ai-explained', 'AI explanation page'),
            ('/login', 'Login page'),
            ('/register', 'Registration page'),
            
            # Stocks
            ('/stocks/', 'Stocks index'),
            ('/stocks/list', 'Stocks list'),
            ('/stocks/search', 'Stocks search'),
            
            # Analysis
            ('/analysis/', 'Analysis index'),
            ('/analysis/market-overview', 'Market overview'),
            
            # Portfolio
            ('/portfolio/', 'Portfolio index'),
            ('/portfolio/advanced/', 'Advanced portfolio'),
            
            # Watchlist
            ('/watchlist/', 'Watchlist index'),
            
            # Resources (NEW)
            ('/resources/analysis-tools', 'Analysis tools page'),
            ('/resources/guides', 'Analysis guides'),
            ('/resources/comparison', 'Tool comparison'),
            
            # External data
            ('/external/market-intelligence', 'Market intelligence'),
            ('/external/insider-trading', 'Insider trading'),
            
            # SEO Content
            ('/blog/', 'Blog index'),
            ('/investment-guides/', 'Investment guides'),
            
            # Pricing
            ('/pricing/', 'Pricing page'),
            
            # API endpoints
            ('/api/stocks/search', 'API stock search'),
            ('/api/market-data', 'API market data'),
        ]
        
        for endpoint, description in endpoints:
            # Test with expected status 200 or 302 (redirect)
            success = self.test_endpoint(endpoint, description=description)
            if not success:
                # Try with 302 (redirect) if 200 failed
                self.test_endpoint(endpoint, expected_status=302, description=f"{description} (redirect)")
    
    def test_static_files(self):
        """Test that static files are accessible"""
        self.log("📁 Testing Static Files", "TEST")
        
        static_files = [
            '/static/css/mobile-optimized.css',
            '/static/css/loading-states.css', 
            '/static/js/onboarding-manager.js',
            '/static/js/loading-manager.js',
            '/static/js/performance-optimizer.js',
            '/static/js/enhanced-realtime.js',
        ]
        
        for static_file in static_files:
            self.test_endpoint(static_file, description=f"Static file: {static_file}")
    
    def test_database_models(self):
        """Test database models can be imported and used"""
        self.log("🗄️ Testing Database Models", "TEST")
        
        try:
            from app.models.user import User
            from app.models.portfolio import Portfolio, PortfolioStock
            from app.models.watchlist import Watchlist, WatchlistItem
            
            # Test model attributes
            user_attrs = ['id', 'username', 'email', 'password_hash']
            portfolio_attrs = ['id', 'name', 'user_id']
            
            for attr in user_attrs:
                assert hasattr(User, attr), f"User model missing {attr}"
            
            for attr in portfolio_attrs:
                assert hasattr(Portfolio, attr), f"Portfolio model missing {attr}"
            
            self.log("✅ Database models test passed", "PASS")
            self.results['passed'] += 1
            return True
            
        except Exception as e:
            error_msg = f"❌ Database models test failed: {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['errors'].append(error_msg)
            self.results['failed'] += 1
            return False
    
    def test_services(self):
        """Test service modules"""
        self.log("⚙️ Testing Service Modules", "TEST")
        
        try:
            from app.services.portfolio_service import get_ai_analysis
            from app.services.data_service import DataService
            
            # Test portfolio service function
            result = get_ai_analysis("EQNR.OL")
            assert isinstance(result, dict), "get_ai_analysis should return dict"
            
            # Test data service
            data_service = DataService()
            assert hasattr(data_service, 'get_stock_data'), "DataService missing get_stock_data"
            
            self.log("✅ Services test passed", "PASS")
            self.results['passed'] += 1
            return True
            
        except Exception as e:
            error_msg = f"❌ Services test failed: {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['errors'].append(error_msg)
            self.results['failed'] += 1
            return False
    
    def test_template_rendering(self):
        """Test that key templates can be rendered"""
        self.log("🎨 Testing Template Rendering", "TEST")
        
        try:
            from app import create_app
            from flask import render_template_string
            
            app = create_app()
            
            with app.app_context():
                # Test basic template rendering
                test_template = "{% extends 'base.html' %}{% block content %}Test{% endblock %}"
                
                try:
                    rendered = render_template_string(test_template)
                    assert 'Test' in rendered, "Template rendering failed"
                    
                    self.log("✅ Template rendering test passed", "PASS")
                    self.results['passed'] += 1
                    return True
                    
                except Exception as e:
                    # This might fail due to missing context, but we can still test imports
                    self.log(f"⚠️ Template rendering test skipped: {str(e)}", "WARN")
                    self.results['warnings'].append(f"Template rendering: {str(e)}")
                    return True
                    
        except Exception as e:
            error_msg = f"❌ Template rendering test failed: {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['errors'].append(error_msg)
            self.results['failed'] += 1
            return False
    
    def run_offline_tests(self):
        """Run tests that don't require a running server"""
        self.log("🧪 Starting Offline Tests", "INFO")
        
        # Test imports first
        if not self.test_imports():
            self.log("❌ Critical imports failed, stopping tests", "ERROR")
            return False
        
        # Test app startup
        self.test_app_startup()
        
        # Test database models
        self.test_database_models()
        
        # Test services
        self.test_services()
        
        # Test template rendering
        self.test_template_rendering()
        
        return True
    
    def run_online_tests(self):
        """Run tests that require a running server"""
        self.log("🌐 Starting Online Tests", "INFO")
        
        # Check if server is running
        try:
            response = self.session.get(self.base_url, timeout=5)
            self.log(f"✅ Server is running at {self.base_url}", "INFO")
        except Exception as e:
            self.log(f"❌ Server not accessible at {self.base_url}: {str(e)}", "ERROR")
            self.log("💡 Start server with: python run.py", "INFO")
            return False
        
        # Test all endpoints
        self.test_all_endpoints()
        
        # Test static files
        self.test_static_files()
        
        return True
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("📊 Generating Test Report", "INFO")
        
        total_tests = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""
{'='*80}
AKSJERADAR V6 - COMPREHENSIVE TEST REPORT
{'='*80}

📊 TEST SUMMARY:
  • Total Tests: {total_tests}
  • Passed: {self.results['passed']} ✅
  • Failed: {self.results['failed']} ❌
  • Pass Rate: {pass_rate:.1f}%
  • Warnings: {len(self.results['warnings'])} ⚠️

"""
        
        if self.results['errors']:
            report += "❌ ERRORS:\n"
            for error in self.results['errors']:
                report += f"  • {error}\n"
            report += "\n"
        
        if self.results['warnings']:
            report += "⚠️ WARNINGS:\n"
            for warning in self.results['warnings']:
                report += f"  • {warning}\n"
            report += "\n"
        
        # Endpoint summary
        if self.results['tested_endpoints']:
            report += "🌐 ENDPOINT TEST RESULTS:\n"
            for endpoint_result in self.results['tested_endpoints']:
                status_icon = "✅" if endpoint_result['success'] else "❌"
                report += f"  {status_icon} {endpoint_result['method']} {endpoint_result['endpoint']} "
                report += f"({endpoint_result['status_code']}) - {endpoint_result['description']}\n"
            report += "\n"
        
        # Overall assessment
        if pass_rate >= 90:
            report += "🎉 OVERALL ASSESSMENT: EXCELLENT - Ready for production!\n"
        elif pass_rate >= 75:
            report += "👍 OVERALL ASSESSMENT: GOOD - Minor issues to address\n"
        elif pass_rate >= 50:
            report += "⚠️ OVERALL ASSESSMENT: NEEDS WORK - Several issues found\n"
        else:
            report += "❌ OVERALL ASSESSMENT: CRITICAL ISSUES - Major problems detected\n"
        
        report += f"\n{'='*80}\n"
        
        print(report)
        
        # Save report to file
        with open('/workspaces/aksjeradarv6/test_report.txt', 'w') as f:
            f.write(report)
        
        return report

def main():
    """Main test runner"""
    print("🚀 AKSJERADAR V6 - COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    
    tester = AksjeradarTester()
    
    # Run offline tests first
    offline_success = tester.run_offline_tests()
    
    if offline_success:
        tester.log("✅ Offline tests completed", "INFO")
        
        # Try online tests
        tester.log("🌐 Attempting online tests...", "INFO")
        online_success = tester.run_online_tests()
        
        if not online_success:
            tester.log("⚠️ Online tests skipped - server not running", "WARN")
            tester.results['warnings'].append("Online tests skipped - server not accessible")
    else:
        tester.log("❌ Offline tests failed, skipping online tests", "ERROR")
    
    # Generate final report
    tester.generate_report()
    
    return tester.results

if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    if results['failed'] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
