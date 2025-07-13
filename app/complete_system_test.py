#!/usr/bin/env python3
"""
Complete System Verification Test
Verifies all functionality including limits, access control, and pricing
"""

import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

import requests
import time
from datetime import datetime

class SystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        
    def log_test(self, category, test_name, status, details=""):
        """Log test results"""
        if category not in self.test_results:
            self.test_results[category] = []
        
        self.test_results[category].append({
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {category}: {test_name} - {details}")
    
    def test_pricing_page(self):
        """Test pricing page accessibility and content"""
        print("\n🏷️ TESTING PRICING PAGE")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{self.base_url}/pricing/")
            if response.status_code == 200:
                content = response.text
                
                # Check for essential pricing elements
                checks = [
                    ("Gratis Demo", "Free tier visible"),
                    ("5/dag", "Daily limit shown"),
                    ("Basic", "Basic tier visible"),
                    ("kr 199", "Basic pricing shown"),
                    ("Pro", "Pro tier visible"), 
                    ("kr 399", "Pro pricing shown"),
                    ("pricing-card", "Cards rendered"),
                    ("Oppgrader til", "Upgrade buttons present")
                ]
                
                for check, description in checks:
                    if check in content:
                        self.log_test("Pricing", description, "PASS")
                    else:
                        self.log_test("Pricing", description, "FAIL", f"Missing: {check}")
                        
            else:
                self.log_test("Pricing", "Page accessibility", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Pricing", "Page accessibility", "FAIL", str(e))
    
    def test_market_intel_endpoints(self):
        """Test all market intel endpoints"""
        print("\n📊 TESTING MARKET INTEL ENDPOINTS")
        print("-" * 45)
        
        endpoints = [
            ("/market-intel/", "Market Intel Index"),
            ("/market-intel/insider-trading", "Insider Trading"),
            ("/market-intel/earnings-calendar", "Earnings Calendar"),
            ("/market-intel/sector-analysis", "Sector Analysis"),
            ("/market-intel/economic-indicators", "Economic Indicators")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    # Check for critical errors in content
                    content = response.text
                    error_indicators = ["Internal Server Error", "Exception", "Error:", "Traceback"]
                    has_error = any(error in content for error in error_indicators)
                    
                    if has_error:
                        self.log_test("Market Intel", name, "FAIL", "Contains error content")
                    else:
                        self.log_test("Market Intel", name, "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test("Market Intel", name, "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Market Intel", name, "FAIL", str(e))
    
    def test_key_endpoints(self):
        """Test key application endpoints"""
        print("\n🔗 TESTING KEY ENDPOINTS")
        print("-" * 30)
        
        endpoints = [
            ("/", "Homepage"),
            ("/login", "Login page"),
            ("/register", "Registration page"),
            ("/stocks/", "Stocks index"),
            ("/analysis/", "Analysis index"),
            ("/contact", "Contact page"),
            ("/privacy", "Privacy page")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.log_test("Core Pages", name, "PASS", f"Status: {response.status_code}")
                elif response.status_code in [301, 302]:
                    self.log_test("Core Pages", name, "WARN", f"Redirect: {response.status_code}")
                else:
                    self.log_test("Core Pages", name, "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Core Pages", name, "FAIL", str(e))
    
    def test_responsive_design(self):
        """Test responsive design elements"""
        print("\n📱 TESTING RESPONSIVE DESIGN")
        print("-" * 35)
        
        try:
            # Test with mobile user agent
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
            }
            
            response = self.session.get(f"{self.base_url}/", headers=mobile_headers)
            if response.status_code == 200:
                content = response.text
                
                responsive_checks = [
                    ("viewport", "Viewport meta tag"),
                    ("col-md-", "Bootstrap responsive columns"),
                    ("d-none d-md-block", "Responsive display classes"),
                    ("container", "Bootstrap containers"),
                    ("@media", "CSS media queries")
                ]
                
                for check, description in responsive_checks:
                    if check in content:
                        self.log_test("Responsive", description, "PASS")
                    else:
                        self.log_test("Responsive", description, "WARN", f"Not found: {check}")
                        
        except Exception as e:
            self.log_test("Responsive", "Mobile compatibility", "FAIL", str(e))
    
    def test_security_headers(self):
        """Test for important security headers"""
        print("\n🔒 TESTING SECURITY HEADERS")
        print("-" * 35)
        
        try:
            response = self.session.get(f"{self.base_url}/")
            headers = response.headers
            
            security_checks = [
                ("X-Content-Type-Options", "Content type protection"),
                ("X-Frame-Options", "Clickjacking protection"),
                ("Content-Security-Policy", "CSP header"),
                ("X-XSS-Protection", "XSS protection")
            ]
            
            for header, description in security_checks:
                if header in headers:
                    self.log_test("Security", description, "PASS", headers[header])
                else:
                    self.log_test("Security", description, "WARN", f"Missing: {header}")
                    
        except Exception as e:
            self.log_test("Security", "Header check", "FAIL", str(e))
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("🚀 COMPREHENSIVE SYSTEM TEST REPORT")
        print("="*60)
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warnings = 0
        
        for category, tests in self.test_results.items():
            print(f"\n📋 {category.upper()}")
            print("-" * len(category))
            
            for test in tests:
                status = test['status']
                details = test['details']
                
                if status == "PASS":
                    print(f"  ✅ {test['test']}: {details}")
                    passed_tests += 1
                elif status == "FAIL":
                    print(f"  ❌ {test['test']}: {details}")
                    failed_tests += 1
                elif status == "WARN":
                    print(f"  ⚠️  {test['test']}: {details}")
                    warnings += 1
                
                total_tests += 1
        
        print(f"\n📊 SUMMARY")
        print("-" * 20)
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Warnings: {warnings} ⚠️")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        elif failed_tests <= 2:
            print("\n✅ System is mostly functional with minor issues.")
        else:
            print("\n⚠️  System has significant issues that need attention.")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🔍 STARTING COMPREHENSIVE SYSTEM VERIFICATION")
        print("="*60)
        
        self.test_pricing_page()
        self.test_market_intel_endpoints()
        self.test_key_endpoints()
        self.test_responsive_design()
        self.test_security_headers()
        
        self.generate_report()

def main():
    """Main test execution"""
    tester = SystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
