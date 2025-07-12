#!/usr/bin/env python3
"""
Comprehensive Pricing Limits and User Flow Test
Tests all pricing limitations, user flows, and system functionality
"""

import sys
import os
import requests
import time
import json
from datetime import datetime

sys.path.insert(0, '/workspaces/aksjeradarv6')

class CompletePricingTest:
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
    
    def test_pricing_page_functionality(self):
        """Test comprehensive pricing page functionality"""
        print("\n💰 TESTING PRICING PAGE FUNCTIONALITY")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{self.base_url}/pricing/")
            if response.status_code == 200:
                content = response.text
                
                # Check for all pricing tiers
                pricing_checks = [
                    ("Gratis Demo", "Free tier displayed"),
                    ("5/dag", "Daily limit clearly shown"),
                    ("kr 199", "Basic pricing displayed"), 
                    ("kr 399", "Pro pricing displayed"),
                    ("Ubegrensede aksje-analyser", "Unlimited analyses mentioned"),
                    ("Begrenset watchlist (5 aksjer)", "Watchlist limit shown"),
                    ("pricing-card", "Card structure present"),
                    ("cta-button", "Call-to-action buttons present"),
                    ("Din nåværende plan", "Current plan indicator"),
                    ("Oppgrader til", "Upgrade options available")
                ]
                
                for check, description in pricing_checks:
                    if check in content:
                        self.log_test("Pricing Page", description, "PASS")
                    else:
                        self.log_test("Pricing Page", description, "FAIL", f"Missing: {check}")
                        
                # Check responsive design elements
                responsive_checks = [
                    ("viewport", "Mobile viewport tag"),
                    ("@media", "Responsive CSS"),
                    ("col-md-", "Bootstrap responsive grid")
                ]
                
                for check, description in responsive_checks:
                    if check in content:
                        self.log_test("Pricing Responsive", description, "PASS")
                    else:
                        self.log_test("Pricing Responsive", description, "WARN")
                        
            else:
                self.log_test("Pricing Page", "Page accessibility", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Pricing Page", "Error during test", "FAIL", str(e))
    
    def test_usage_tracking_endpoints(self):
        """Test endpoints that should track usage"""
        print("\n📊 TESTING USAGE TRACKING ENDPOINTS")
        print("-" * 45)
        
        # Endpoints that should track daily analysis usage
        analysis_endpoints = [
            ("/analysis/technical", "Technical Analysis"),
            ("/analysis/ai", "AI Analysis"),
            ("/analysis/recommendation", "Recommendation"),
            ("/stocks/details/EQNR.OL", "Stock Details (should track)")
        ]
        
        for endpoint, name in analysis_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Check for usage indication
                    usage_indicators = [
                        "daglige analyser",
                        "daily_analyses", 
                        "remaining",
                        "brukt opp",
                        "Oppgrader for"
                    ]
                    
                    has_usage_tracking = any(indicator in content.lower() for indicator in usage_indicators)
                    
                    if has_usage_tracking:
                        self.log_test("Usage Tracking", name, "PASS", "Usage tracking detected")
                    else:
                        self.log_test("Usage Tracking", name, "WARN", "No usage tracking detected")
                        
                elif response.status_code in [301, 302, 308]:
                    self.log_test("Usage Tracking", name, "WARN", f"Redirect: {response.status_code}")
                else:
                    self.log_test("Usage Tracking", name, "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Usage Tracking", name, "FAIL", str(e))
    
    def test_user_flow_endpoints(self):
        """Test important user flow endpoints"""
        print("\n👤 TESTING USER FLOW ENDPOINTS")
        print("-" * 40)
        
        user_endpoints = [
            ("/login", "Login Page"),
            ("/register", "Registration Page"),
            ("/contact", "Contact Page"),
            ("/privacy", "Privacy Page"),
            ("/", "Homepage"),
            ("/stocks/", "Stocks Index"),
            ("/analysis/", "Analysis Index"),
            ("/portfolio/", "Portfolio"),
            ("/watchlist/", "Watchlist")
        ]
        
        for endpoint, name in user_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Check for critical functionality
                    if endpoint == "/login":
                        has_form = '<form' in content and 'password' in content
                        self.log_test("User Flow", name, "PASS" if has_form else "FAIL", "Login form present" if has_form else "No login form")
                    elif endpoint == "/register":
                        has_form = '<form' in content and 'email' in content
                        self.log_test("User Flow", name, "PASS" if has_form else "FAIL", "Registration form present" if has_form else "No registration form")
                    else:
                        self.log_test("User Flow", name, "PASS", "Page loads successfully")
                        
                elif response.status_code in [301, 302, 308]:
                    self.log_test("User Flow", name, "WARN", f"Redirect: {response.status_code}")
                else:
                    self.log_test("User Flow", name, "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("User Flow", name, "FAIL", str(e))
    
    def test_security_features(self):
        """Test security features and headers"""
        print("\n🔒 TESTING SECURITY FEATURES")
        print("-" * 35)
        
        try:
            response = self.session.get(f"{self.base_url}/")
            headers = response.headers
            
            # Security headers to check
            security_headers = [
                ("X-Content-Type-Options", "Content type protection"),
                ("X-Frame-Options", "Clickjacking protection"),
                ("X-XSS-Protection", "XSS protection"),
                ("Strict-Transport-Security", "HTTPS enforcement"),
                ("Content-Security-Policy", "CSP header")
            ]
            
            for header, description in security_headers:
                if header in headers:
                    self.log_test("Security", description, "PASS", headers[header])
                else:
                    self.log_test("Security", description, "WARN", f"Missing: {header}")
            
            # Check for CSRF protection
            content = response.text
            if 'csrf-token' in content or 'csrf_token' in content:
                self.log_test("Security", "CSRF Protection", "PASS", "CSRF token detected")
            else:
                self.log_test("Security", "CSRF Protection", "WARN", "No CSRF token found")
                
        except Exception as e:
            self.log_test("Security", "Header check", "FAIL", str(e))
    
    def test_api_endpoints(self):
        """Test API endpoints functionality"""
        print("\n🔌 TESTING API ENDPOINTS")
        print("-" * 30)
        
        api_endpoints = [
            ("/api/market-data", "Market Data API"),
            ("/market-intel/api/insider-trading/EQNR.OL", "Insider Trading API"),
            ("/analysis/api/market-summary", "Market Summary API")
        ]
        
        for endpoint, name in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    # Try to parse as JSON
                    try:
                        data = response.json()
                        self.log_test("API", name, "PASS", f"JSON response with {len(data) if isinstance(data, (list, dict)) else 'unknown'} items")
                    except:
                        self.log_test("API", name, "WARN", "Non-JSON response")
                elif response.status_code == 404:
                    self.log_test("API", name, "WARN", "API not implemented")
                else:
                    self.log_test("API", name, "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("API", name, "FAIL", str(e))
    
    def test_notification_system(self):
        """Test notification/toast system"""
        print("\n🔔 TESTING NOTIFICATION SYSTEM")
        print("-" * 40)
        
        try:
            # Test pages that should have notifications
            pages_with_notifications = [
                ("/stocks/details/EQNR.OL", "Stock details notifications"),
                ("/portfolio/", "Portfolio notifications"),
                ("/watchlist/", "Watchlist notifications")
            ]
            
            for endpoint, description in pages_with_notifications:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    content = response.text
                    
                    # Check for notification/toast elements
                    notification_elements = [
                        "toast",
                        "alert",
                        "notification",
                        "showToast",
                        "bootstrap.Toast"
                    ]
                    
                    has_notifications = any(element in content for element in notification_elements)
                    
                    if has_notifications:
                        self.log_test("Notifications", description, "PASS", "Notification system detected")
                    else:
                        self.log_test("Notifications", description, "WARN", "No notifications detected")
                        
        except Exception as e:
            self.log_test("Notifications", "System test", "FAIL", str(e))
    
    def generate_comprehensive_report(self):
        """Generate final comprehensive report"""
        print("\n" + "="*70)
        print("🚀 COMPREHENSIVE PRICING & FUNCTIONALITY TEST REPORT")
        print("="*70)
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
        
        print(f"\n📊 FINAL SUMMARY")
        print("-" * 25)
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Warnings: {warnings} ⚠️")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        # Determine overall system health
        if failed_tests == 0 and warnings <= 3:
            print("\n🎉 EXCELLENT! System is production-ready with all core functionality working.")
        elif failed_tests <= 2 and warnings <= 6:
            print("\n✅ GOOD! System is mostly functional with minor issues to address.")
        elif failed_tests <= 5:
            print("\n⚠️  FAIR! System has some issues that should be addressed before production.")
        else:
            print("\n❌ POOR! System has significant issues that need immediate attention.")
        
        # Key recommendations
        print(f"\n💡 KEY RECOMMENDATIONS:")
        print("-" * 25)
        
        if failed_tests > 0:
            print("• Fix failed tests before production deployment")
        if warnings > 5:
            print("• Address security warnings for better protection")
        
        print("• Verify 5/day analysis limits are properly enforced")
        print("• Test user registration and subscription flows manually")
        print("• Ensure notification system works across all browsers")
        print("• Test responsive design on actual mobile devices")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warnings,
            'success_rate': success_rate
        }
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🔍 STARTING COMPREHENSIVE PRICING & FUNCTIONALITY TEST")
        print("="*65)
        
        self.test_pricing_page_functionality()
        self.test_usage_tracking_endpoints()
        self.test_user_flow_endpoints()
        self.test_security_features()
        self.test_api_endpoints()
        self.test_notification_system()
        
        return self.generate_comprehensive_report()

def main():
    """Main test execution"""
    tester = CompletePricingTest()
    results = tester.run_all_tests()
    
    # Save results to file for reference
    with open('/workspaces/aksjeradarv6/comprehensive_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': results,
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: comprehensive_test_results.json")

if __name__ == "__main__":
    main()
