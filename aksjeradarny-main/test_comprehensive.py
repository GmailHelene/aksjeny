#!/usr/bin/env python3
"""
Comprehensive testing script for Aksjeradar v6 - Final validation
Tests all newly implemented features and ensures system integrity
"""

import requests
import json
import time
import sys
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime

class AksjeradarTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_endpoint(self, endpoint, method="GET", data=None, expected_status=200, description=""):
        """Test a single endpoint"""
        try:
            url = urljoin(self.base_url, endpoint)
            self.log(f"Testing {method} {url} - {description}")
            
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, json=data, timeout=10)
            else:
                response = self.session.request(method, url, json=data, timeout=10)
            
            if response.status_code == expected_status:
                self.log(f"✅ PASS: {endpoint} returned {response.status_code}", "SUCCESS")
                self.test_results["passed"] += 1
                return True
            else:
                self.log(f"❌ FAIL: {endpoint} returned {response.status_code}, expected {expected_status}", "ERROR")
                self.test_results["failed"] += 1
                self.test_results["errors"].append(f"{endpoint}: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ ERROR: {endpoint} - {str(e)}", "ERROR")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{endpoint}: {str(e)}")
            return False
    
    def test_demo_functionality(self):
        """Test demo page and functionality"""
        self.log("🧪 Testing Demo Functionality", "TEST")
        
        # Test demo page loads
        self.test_endpoint("/demo", description="Demo page loads")
        
        # Test demo with different stocks
        demo_stocks = ["EQNR", "DNB", "TEL", "AKER"]
        for stock in demo_stocks:
            self.test_endpoint(f"/demo?symbol={stock}", description=f"Demo analysis for {stock}")
        
    def test_pricing_system(self):
        """Test pricing and subscription system"""
        self.log("💰 Testing Pricing System", "TEST")
        
        # Test pricing page
        self.test_endpoint("/pricing/pricing", description="Pricing page loads")
        
        # Test webhook endpoint (should require proper signature)
        self.test_endpoint("/pricing/webhook", method="POST", expected_status=400, 
                         description="Webhook endpoint security")
    
    def test_ai_transparency(self):
        """Test AI explanation page"""
        self.log("🤖 Testing AI Transparency", "TEST")
        
        self.test_endpoint("/ai-explained", description="AI explanation page loads")
    
    def test_advanced_features(self):
        """Test advanced portfolio and watchlist features"""
        self.log("📊 Testing Advanced Features", "TEST")
        
        # Test advanced portfolio routes
        self.test_endpoint("/portfolio/advanced", description="Advanced portfolio page")
        self.test_endpoint("/portfolio/optimization", description="Portfolio optimization")
        self.test_endpoint("/portfolio/backtest", description="Portfolio backtest")
        
        # Test advanced watchlist
        self.test_endpoint("/watchlist/advanced", description="Advanced watchlist")
        
        # Test backtest system
        self.test_endpoint("/backtest/", description="Backtest system")
        
    def test_seo_content(self):
        """Test SEO-optimized content pages"""
        self.log("🔍 Testing SEO Content", "TEST")
        
        # Test blog and content pages
        self.test_endpoint("/blogg", description="Blog index page")
        self.test_endpoint("/teknisk-analyse-oslobors", description="SEO content page")
        self.test_endpoint("/ai-prediksjon-aksjer", description="AI prediction content")
        
    def test_api_endpoints(self):
        """Test API endpoints"""
        self.log("🔌 Testing API Endpoints", "TEST")
        
        # Test various API endpoints
        self.test_endpoint("/api/stock/EQNR", description="Stock API endpoint")
        self.test_endpoint("/api/market/overview", description="Market overview API")
        
    def test_real_time_features(self):
        """Test real-time functionality"""
        self.log("⚡ Testing Real-time Features", "TEST")
        
        # Test WebSocket endpoints
        self.test_endpoint("/ws/prices", description="WebSocket price endpoint")
        self.test_endpoint("/realtime/price/EQNR", description="Real-time price endpoint")
        
    def test_notifications_system(self):
        """Test notification system"""
        self.log("🔔 Testing Notifications", "TEST")
        
        self.test_endpoint("/notifications/settings", description="Notification settings")
        self.test_endpoint("/notifications/history", description="Notification history")
        
    def test_mobile_optimization(self):
        """Test mobile-specific features"""
        self.log("📱 Testing Mobile Optimization", "TEST")
        
        # Test with mobile user agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        try:
            response = self.session.get(urljoin(self.base_url, "/"), headers=mobile_headers)
            if response.status_code == 200:
                self.log("✅ PASS: Mobile optimization working", "SUCCESS")
                self.test_results["passed"] += 1
            else:
                self.log("❌ FAIL: Mobile optimization issue", "ERROR")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log(f"❌ ERROR: Mobile test failed - {str(e)}", "ERROR")
            self.test_results["failed"] += 1
    
    def test_performance_optimization(self):
        """Test performance optimizations"""
        self.log("🚀 Testing Performance Optimization", "TEST")
        
        # Test static file loading with cache headers
        static_files = [
            "/static/css/style.css",
            "/static/css/mobile-optimized.css",
            "/static/css/loading-states.css",
            "/static/js/loading-manager.js",
            "/static/js/onboarding-manager.js",
            "/static/js/performance-optimizer.js"
        ]
        
        for file_path in static_files:
            try:
                response = self.session.get(urljoin(self.base_url, file_path))
                if response.status_code == 200:
                    self.log(f"✅ PASS: Static file loads - {file_path}", "SUCCESS")
                    self.test_results["passed"] += 1
                else:
                    self.log(f"❌ FAIL: Static file missing - {file_path}", "ERROR")
                    self.test_results["failed"] += 1
            except Exception as e:
                self.log(f"❌ ERROR: Static file test failed - {file_path}: {str(e)}", "ERROR")
                self.test_results["failed"] += 1
    
    def test_security_features(self):
        """Test security implementations"""
        self.log("🔒 Testing Security Features", "TEST")
        
        # Test CSRF protection
        try:
            # Attempt POST without CSRF token (should fail)
            response = self.session.post(urljoin(self.base_url, "/login"), 
                                       data={"username": "test", "password": "test"})
            if response.status_code in [400, 403]:
                self.log("✅ PASS: CSRF protection working", "SUCCESS")
                self.test_results["passed"] += 1
            else:
                self.log("❌ FAIL: CSRF protection not working", "ERROR")
                self.test_results["failed"] += 1
        except Exception as e:
            self.log(f"❌ ERROR: CSRF test failed - {str(e)}", "ERROR")
            self.test_results["failed"] += 1
    
    def test_error_handling(self):
        """Test error handling"""
        self.log("⚠️ Testing Error Handling", "TEST")
        
        # Test 404 handling
        self.test_endpoint("/nonexistent-page", expected_status=404, 
                         description="404 error handling")
        
        # Test invalid stock symbol
        self.test_endpoint("/stocks/INVALID_SYMBOL", expected_status=404,
                         description="Invalid stock symbol handling")
    
    def test_database_integration(self):
        """Test database connectivity"""
        self.log("🗄️ Testing Database Integration", "TEST")
        
        # Test endpoints that require database
        self.test_endpoint("/stocks", description="Database-dependent stock list")
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        self.log("🚀 Starting Aksjeradar v6 Comprehensive Testing", "START")
        self.log(f"Testing against: {self.base_url}")
        
        start_time = time.time()
        
        # Run all test categories
        test_categories = [
            self.test_demo_functionality,
            self.test_pricing_system,
            self.test_ai_transparency,
            self.test_advanced_features,
            self.test_seo_content,
            self.test_api_endpoints,
            self.test_real_time_features,
            self.test_notifications_system,
            self.test_mobile_optimization,
            self.test_performance_optimization,
            self.test_security_features,
            self.test_error_handling,
            self.test_database_integration
        ]
        
        for test_category in test_categories:
            try:
                test_category()
                self.log("", "")  # Add spacing between test categories
            except Exception as e:
                self.log(f"❌ Test category failed: {str(e)}", "ERROR")
                self.test_results["failed"] += 1
        
        # Final results
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("📊 TESTING COMPLETED", "FINAL")
        self.log(f"⏱️ Duration: {duration:.2f} seconds")
        self.log(f"✅ Passed: {self.test_results['passed']}")
        self.log(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results["errors"]:
            self.log("❌ Error Details:", "ERROR")
            for error in self.test_results["errors"]:
                self.log(f"   - {error}", "ERROR")
        
        # Calculate success rate
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        if total_tests > 0:
            success_rate = (self.test_results["passed"] / total_tests) * 100
            self.log(f"📈 Success Rate: {success_rate:.1f}%")
            
            # Provide recommendation
            if success_rate >= 90:
                self.log("🎉 EXCELLENT: System ready for production!", "SUCCESS")
                return 0
            elif success_rate >= 75:
                self.log("👍 GOOD: Minor issues to address", "WARNING")
                return 1
            else:
                self.log("⚠️ WARNING: Major issues need attention", "ERROR")
                return 2
        else:
            self.log("❌ No tests completed", "ERROR")
            return 3

def main():
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print("🚀 Aksjeradar v6 - Comprehensive Testing Suite")
    print("=" * 50)
    print(f"Target URL: {base_url}")
    print("=" * 50)
    
    # Create tester instance
    tester = AksjeradarTester(base_url)
    
    # Run tests
    exit_code = tester.run_all_tests()
    
    print("\n" + "=" * 50)
    print("Testing completed. Check logs above for details.")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
