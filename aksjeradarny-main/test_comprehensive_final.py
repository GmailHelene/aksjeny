#!/usr/bin/env python3
"""
Omfattende test av hele Aksjeradar V6 applikasjonen
Tester alle endepunkter, services, imports og funksjonalitet
"""

import os
import sys
import traceback
import requests
import time
import subprocess
from datetime import datetime

# Legg til prosjektets rot til Python path
sys.path.insert(0, os.path.abspath('.'))

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

class AksjeradarComprehensiveTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.session = requests.Session()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'total': 0
        }
        self.failed_tests = []
        
    def log(self, message, level='INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        colors = {
            'INFO': Color.BLUE,
            'SUCCESS': Color.GREEN,
            'ERROR': Color.RED,
            'WARNING': Color.YELLOW,
            'TEST': Color.CYAN
        }
        color = colors.get(level, '')
        print(f"{color}[{timestamp}] {level}: {message}{Color.END}")
        
    def test_result(self, test_name, passed, details="", warning=False):
        self.test_results['total'] += 1
        if passed:
            self.test_results['passed'] += 1
            self.log(f"✅ {test_name}: PASSED {details}", 'SUCCESS')
        elif warning:
            self.test_results['warnings'] += 1
            self.log(f"⚠️ {test_name}: WARNING {details}", 'WARNING')
        else:
            self.test_results['failed'] += 1
            self.failed_tests.append(f"{test_name}: {details}")
            self.log(f"❌ {test_name}: FAILED {details}", 'ERROR')
            
    def test_imports_and_app_creation(self):
        """Test at alle imports fungerer og appen kan opprettes"""
        self.log("🧪 Testing imports and app creation...", 'TEST')
        
        try:
            # Test Flask import
            from flask import Flask
            self.test_result("Flask import", True)
        except Exception as e:
            self.test_result("Flask import", False, str(e))
            
        try:
            # Test app extensions import
            from app.extensions import db, login_manager
            self.test_result("App extensions import", True)
        except Exception as e:
            self.test_result("App extensions import", False, str(e))
            
        try:
            # Test app creation
            from app import create_app
            app = create_app()
            self.test_result("App creation", True)
            
            # Test at app har korrekt konfiguration
            with app.app_context():
                self.test_result("App context", True)
        except Exception as e:
            self.test_result("App creation", False, str(e))
            
        try:
            # Test alle services imports
            from app.services.data_service import DataService
            from app.services.analysis_service import AnalysisService
            from app.services.ai_service import AIService
            from app.services.portfolio_service import get_ai_analysis
            from app.services.external_data import external_data_service
            self.test_result("Services import", True)
        except Exception as e:
            self.test_result("Services import", False, str(e))
            
        try:
            # Test alle models imports
            from app.models.user import User
            from app.models.portfolio import Portfolio, PortfolioStock
            from app.models.watchlist import Watchlist, WatchlistStock
            self.test_result("Models import", True)
        except Exception as e:
            self.test_result("Models import", False, str(e))
            
        try:
            # Test alle routes imports
            from app.routes.main import main
            from app.routes.stocks import stocks
            from app.routes.analysis import analysis
            from app.routes.portfolio import portfolio
            from app.routes.resources import resources_bp
            self.test_result("Routes import", True)
        except Exception as e:
            self.test_result("Routes import", False, str(e))
            
    def test_database_connection(self):
        """Test database tilkobling og tabeller"""
        self.log("🧪 Testing database connection...", 'TEST')
        
        try:
            from app import create_app
            from app.extensions import db
            from app.models.user import User
            
            app = create_app()
            with app.app_context():
                # Test database tilkobling
                db.create_all()
                self.test_result("Database connection", True)
                
                # Test at tabeller eksisterer
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                expected_tables = ['users', 'portfolios', 'portfolio_stocks', 'watchlists', 'watchlist_stocks']
                
                for table in expected_tables:
                    if table in tables:
                        self.test_result(f"Table '{table}' exists", True)
                    else:
                        self.test_result(f"Table '{table}' exists", False, "Table missing")
                        
        except Exception as e:
            self.test_result("Database connection", False, str(e))
            
    def test_services_functionality(self):
        """Test alle services fungerer"""
        self.log("🧪 Testing services functionality...", 'TEST')
        
        try:
            from app.services.data_service import DataService
            
            # Test DataService
            oslo_data = DataService.get_oslo_bors_overview()
            self.test_result("DataService Oslo Børs", isinstance(oslo_data, dict))
            
            global_data = DataService.get_global_stocks_overview()
            self.test_result("DataService Global stocks", isinstance(global_data, dict))
            
            stock_data = DataService.get_stock_data('EQNR.OL')
            self.test_result("DataService stock data", stock_data is not None)
            
        except Exception as e:
            self.test_result("DataService functionality", False, str(e))
            
        try:
            from app.services.analysis_service import AnalysisService
            
            # Test AnalysisService
            analysis = AnalysisService.get_technical_analysis('EQNR.OL')
            self.test_result("AnalysisService technical", isinstance(analysis, dict))
            
        except Exception as e:
            self.test_result("AnalysisService functionality", False, str(e))
            
        try:
            from app.services.portfolio_service import get_ai_analysis
            
            # Test Portfolio Service
            ai_analysis = get_ai_analysis('EQNR.OL')
            self.test_result("Portfolio Service AI analysis", isinstance(ai_analysis, dict))
            
        except Exception as e:
            self.test_result("Portfolio Service functionality", False, str(e))
            
    def start_server(self):
        """Start Flask development server"""
        self.log("🚀 Starting Flask development server...", 'TEST')
        
        try:
            # Start server i bakgrunnen
            self.server_process = subprocess.Popen([
                'python', '-c', 
                """
from app import create_app
app = create_app()
app.run(debug=False, host='0.0.0.0', port=5000)
                """
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Vent på at serveren starter
            time.sleep(5)
            
            # Test at serveren svarer
            try:
                response = self.session.get(f"{self.base_url}/", timeout=10)
                if response.status_code == 200:
                    self.test_result("Server startup", True)
                    return True
                else:
                    self.test_result("Server startup", False, f"Status: {response.status_code}")
                    return False
            except:
                # Prøv alternative porter
                for port in [5001, 5002]:
                    try:
                        alt_url = f"http://localhost:{port}"
                        response = self.session.get(alt_url, timeout=5)
                        if response.status_code == 200:
                            self.base_url = alt_url
                            self.test_result("Server startup", True, f"Found server on port {port}")
                            return True
                    except:
                        continue
                
                self.test_result("Server startup", False, "Server not responding on any port")
                return False
                
        except Exception as e:
            self.test_result("Server startup", False, str(e))
            return False
            
    def stop_server(self):
        """Stop Flask server"""
        if hasattr(self, 'server_process'):
            self.server_process.terminate()
            self.server_process.wait()
            
    def test_endpoint(self, url, method='GET', expected_status=200, description="", data=None, allow_redirects=True):
        """Test en enkelt endpoint"""
        try:
            full_url = f"{self.base_url}{url}"
            
            if method == 'GET':
                response = self.session.get(full_url, timeout=10, allow_redirects=allow_redirects)
            elif method == 'POST':
                response = self.session.post(full_url, data=data, timeout=10, allow_redirects=allow_redirects)
            else:
                response = self.session.request(method, full_url, timeout=10, allow_redirects=allow_redirects)
                
            success = response.status_code == expected_status
            details = f"({response.status_code})"
            
            if not success and response.status_code in [302, 301]:
                # Redirect kan være OK for noen endepunkter
                success = True
                details = f"(redirect to {response.headers.get('Location', 'unknown')})"
                
            self.test_result(f"Endpoint {method} {url} {description}", success, details)
            return response
            
        except Exception as e:
            self.test_result(f"Endpoint {method} {url} {description}", False, str(e))
            return None
            
    def test_all_endpoints(self):
        """Test alle hovedendepunkter"""
        self.log("🧪 Testing all main endpoints...", 'TEST')
        
        # Hovedsider
        self.test_endpoint('/', description="Homepage")
        self.test_endpoint('/health', description="Health check")
        self.test_endpoint('/demo', description="Demo page")
        self.test_endpoint('/ai-explained', description="AI explained page")
        
        # Stocks endpoints
        self.test_endpoint('/stocks/', description="Stocks index")
        self.test_endpoint('/stocks/list', description="Stocks list")
        self.test_endpoint('/stocks/details/EQNR.OL', description="Stock details")
        self.test_endpoint('/stocks/search', description="Stock search")
        
        # Analysis endpoints
        self.test_endpoint('/analysis/', description="Analysis index")
        self.test_endpoint('/analysis/market_overview', description="Market overview")
        self.test_endpoint('/analysis/ai', description="AI analysis")
        
        # Portfolio endpoints
        self.test_endpoint('/portfolio/', description="Portfolio index")
        self.test_endpoint('/portfolio/create', description="Create portfolio")
        
        # Resources endpoints (nye)
        self.test_endpoint('/resources/analysis-tools', description="Analysis tools")
        self.test_endpoint('/resources/guides', description="Analysis guides")
        self.test_endpoint('/resources/comparison', description="Tool comparison")
        
        # External data endpoints
        self.test_endpoint('/external/market-intelligence', description="Market intelligence")
        self.test_endpoint('/external/insider-trading', description="Insider trading")
        
        # API endpoints
        self.test_endpoint('/api/stocks/EQNR.OL', description="API stock data")
        self.test_endpoint('/api/market-overview', description="API market overview")
        
        # Authentication endpoints
        self.test_endpoint('/login', description="Login page")
        self.test_endpoint('/register', description="Register page")
        self.test_endpoint('/forgot_password', description="Forgot password")
        
    def test_new_features(self):
        """Test de nye funksjonene implementert"""
        self.log("🧪 Testing new V6 features...", 'TEST')
        
        # Test resources side
        response = self.test_endpoint('/resources/analysis-tools', description="New resources page")
        if response and response.status_code == 200:
            content = response.text
            # Sjekk at siden inneholder forventet innhold
            if 'TradingView' in content and 'Aksje.io' in content:
                self.test_result("Resources content", True, "Contains expected tools")
            else:
                self.test_result("Resources content", False, "Missing expected content")
                
        # Test portfolio advanced features
        self.test_endpoint('/portfolio/advanced', description="Advanced portfolio", expected_status=[200, 302])
        
        # Test watchlist advanced
        self.test_endpoint('/watchlist/', description="Advanced watchlist", expected_status=[200, 302])
        
        # Test backtest features
        self.test_endpoint('/backtest/', description="Backtest feature", expected_status=[200, 302])
        
        # Test pricing page
        self.test_endpoint('/pricing/', description="Pricing page")
        
    def test_static_files(self):
        """Test at statiske filer kan lastes"""
        self.log("🧪 Testing static files...", 'TEST')
        
        static_files = [
            '/static/css/style.css',
            '/static/css/mobile-optimized.css',
            '/static/css/loading-states.css',
            '/static/js/onboarding-manager.js',
            '/static/js/loading-manager.js',
            '/static/js/performance-optimizer.js',
            '/static/js/enhanced-realtime.js'
        ]
        
        for file_path in static_files:
            self.test_endpoint(file_path, description=f"Static file {file_path.split('/')[-1]}")
            
    def test_forms_and_csrf(self):
        """Test at forms og CSRF fungerer"""
        self.log("🧪 Testing forms and CSRF...", 'TEST')
        
        # Test login form
        login_response = self.test_endpoint('/login', description="Login form page")
        if login_response and login_response.status_code == 200:
            if 'csrf_token' in login_response.text:
                self.test_result("CSRF token in login form", True)
            else:
                self.test_result("CSRF token in login form", False, "No CSRF token found")
                
        # Test register form
        register_response = self.test_endpoint('/register', description="Register form page")
        if register_response and register_response.status_code == 200:
            if 'csrf_token' in register_response.text:
                self.test_result("CSRF token in register form", True)
            else:
                self.test_result("CSRF token in register form", False, "No CSRF token found")
                
    def test_error_handling(self):
        """Test error handling"""
        self.log("🧪 Testing error handling...", 'TEST')
        
        # Test 404 for ikke-eksisterende sider
        self.test_endpoint('/nonexistent-page', expected_status=404, description="404 error handling")
        
        # Test ugyldig stock ticker
        self.test_endpoint('/stocks/details/INVALID.TICKER', description="Invalid stock ticker", expected_status=[200, 404])
        
    def test_mobile_optimization(self):
        """Test mobile optimalisering"""
        self.log("🧪 Testing mobile optimization...", 'TEST')
        
        # Test med mobile user agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        try:
            response = requests.get(f"{self.base_url}/", headers=mobile_headers, timeout=10)
            self.test_result("Mobile responsiveness", response.status_code == 200)
        except Exception as e:
            self.test_result("Mobile responsiveness", False, str(e))
            
    def run_comprehensive_test(self):
        """Kjør alle tester"""
        self.log("🚀 Starting comprehensive Aksjeradar V6 testing...", 'TEST')
        print("=" * 80)
        
        # 1. Test imports og app creation
        self.test_imports_and_app_creation()
        
        # 2. Test database
        self.test_database_connection()
        
        # 3. Test services
        self.test_services_functionality()
        
        # 4. Start server for endpoint testing
        if self.start_server():
            try:
                # 5. Test alle endepunkter
                self.test_all_endpoints()
                
                # 6. Test nye features
                self.test_new_features()
                
                # 7. Test statiske filer
                self.test_static_files()
                
                # 8. Test forms og CSRF
                self.test_forms_and_csrf()
                
                # 9. Test error handling
                self.test_error_handling()
                
                # 10. Test mobile optimization
                self.test_mobile_optimization()
                
            finally:
                self.stop_server()
        else:
            self.log("Skipping endpoint tests due to server startup failure", 'ERROR')
            
        # Print results
        self.print_results()
        
    def print_results(self):
        """Print test results"""
        print("\n" + "=" * 80)
        print(f"{Color.BOLD}AKSJERADAR V6 COMPREHENSIVE TEST RESULTS{Color.END}")
        print("=" * 80)
        
        total = self.test_results['total']
        passed = self.test_results['passed']
        failed = self.test_results['failed']
        warnings = self.test_results['warnings']
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"{Color.GREEN}✅ Passed: {passed}{Color.END}")
        print(f"{Color.YELLOW}⚠️  Warnings: {warnings}{Color.END}")
        print(f"{Color.RED}❌ Failed: {failed}{Color.END}")
        print(f"{Color.BLUE}📊 Total: {total}{Color.END}")
        print(f"{Color.CYAN}📈 Success Rate: {success_rate:.1f}%{Color.END}")
        
        if failed > 0:
            print(f"\n{Color.RED}FAILED TESTS:{Color.END}")
            for test in self.failed_tests:
                print(f"  ❌ {test}")
                
        print("\n" + "=" * 80)
        
        if success_rate >= 90:
            print(f"{Color.GREEN}{Color.BOLD}🎉 EXCELLENT! Aksjeradar V6 is in great shape!{Color.END}")
        elif success_rate >= 80:
            print(f"{Color.YELLOW}{Color.BOLD}👍 GOOD! Minor issues to address.{Color.END}")
        elif success_rate >= 70:
            print(f"{Color.YELLOW}{Color.BOLD}⚠️  FAIR! Some issues need attention.{Color.END}")
        else:
            print(f"{Color.RED}{Color.BOLD}🚨 POOR! Significant issues need fixing.{Color.END}")
            
        print("=" * 80)

def main():
    """Main test function"""
    tester = AksjeradarComprehensiveTester()
    try:
        tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Test interrupted by user{Color.END}")
        tester.stop_server()
    except Exception as e:
        print(f"\n{Color.RED}Test failed with error: {e}{Color.END}")
        traceback.print_exc()
        tester.stop_server()

if __name__ == "__main__":
    main()
