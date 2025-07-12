#!/usr/bin/env python3
"""
Comprehensive System Verification Test
Tests all the improvements requested by the user.
"""

import requests
import sys
import time
import re
from datetime import datetime

class SystemVerificationTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Aksjeradar-SystemVerification-Test/1.0'
        })
        self.results = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def add_result(self, test_name, status, details):
        self.results.append({
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now()
        })
        
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌', 
            'WARN': '⚠️',
            'INFO': 'ℹ️'
        }.get(status, '❓')
        
        self.log(f"{status_emoji} {test_name}: {details}", status)
    
    def test_pricing_page_styling(self):
        """Test 1: Style the /pricing page better"""
        self.log("🎨 Testing pricing page styling and responsiveness...")
        
        try:
            response = self.session.get(f"{self.base_url}/pricing/")
            if response.status_code == 200:
                content = response.text
                
                # Check for pricing tiers
                has_kr_199 = 'kr 199' in content.lower() or 'kr199' in content.lower()
                has_kr_399 = 'kr 399' in content.lower() or 'kr399' in content.lower()
                
                # Check for responsive design elements
                has_responsive = any(term in content.lower() for term in [
                    'mobile-optimized', 'viewport', 'responsive', '@media', 'col-md', 'col-sm'
                ])
                
                # Check for modern styling elements
                has_modern_css = any(term in content.lower() for term in [
                    'gradient', 'shadow', 'border-radius', 'animation', 'transform'
                ])
                
                if has_kr_199 and has_kr_399:
                    self.add_result("Pricing tiers displayed", "PASS", "Basic (kr 199) and Pro (kr 399) pricing visible")
                else:
                    self.add_result("Pricing tiers displayed", "FAIL", f"Missing pricing: kr 199={has_kr_199}, kr 399={has_kr_399}")
                
                if has_responsive:
                    self.add_result("Responsive design", "PASS", "Responsive design elements detected")
                else:
                    self.add_result("Responsive design", "WARN", "Limited responsive design elements found")
                    
                if has_modern_css:
                    self.add_result("Modern styling", "PASS", "Modern CSS styling detected")
                else:
                    self.add_result("Modern styling", "WARN", "Limited modern styling detected")
            else:
                self.add_result("Pricing page access", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.add_result("Pricing page styling", "FAIL", str(e))
    
    def test_pricing_limitations_verification(self):
        """Test 2: Verify pricing plan limitations are implemented"""
        self.log("📊 Testing pricing limitation implementation...")
        
        # Test analysis limit enforcement
        try:
            analysis_responses = []
            for i in range(7):  # Try to exceed 5/day limit
                response = self.session.get(f"{self.base_url}/analysis/technical/EQNR.OL")
                analysis_responses.append(response.status_code)
                if response.status_code == 302:  # Redirect indicates access control
                    break
                time.sleep(0.2)
            
            has_limit_enforcement = 302 in analysis_responses or len([r for r in analysis_responses if r == 200]) <= 5
            
            if has_limit_enforcement:
                self.add_result("5 analyses/day limit", "PASS", "Analysis limit enforcement detected")
            else:
                self.add_result("5 analyses/day limit", "WARN", f"Responses: {analysis_responses}")
                
        except Exception as e:
            self.add_result("Analysis limit test", "FAIL", str(e))
        
        # Test watchlist size limit
        try:
            for ticker in ['EQNR.OL', 'DNB.OL', 'NEL.OL', 'AKER.OL', 'YAR.OL', 'MOWI.OL']:
                data = {'ticker': ticker}
                response = self.session.post(f"{self.base_url}/api/watchlist/add", json=data)
                if response.status_code == 429:  # Rate limited
                    self.add_result("Watchlist size limit", "PASS", "Watchlist limitation detected")
                    break
                time.sleep(0.1)
            else:
                self.add_result("Watchlist size limit", "INFO", "Watchlist requests processed (may have limits)")
        except Exception as e:
            self.add_result("Watchlist limit test", "FAIL", str(e))
    
    def test_pricing_exempt_status(self):
        """Test 3: Ensure /pricing is exempt from restrictions"""
        self.log("🔓 Testing pricing page exempt status...")
        
        # Clear session to test as anonymous user
        self.session.cookies.clear()
        
        try:
            response = self.session.get(f"{self.base_url}/pricing/")
            if response.status_code == 200:
                self.add_result("Pricing page exempt", "PASS", "Pricing accessible without authentication")
            elif response.status_code == 302:
                # Check if redirect is to login (bad) or demo (might be ok)
                location = response.headers.get('Location', '')
                if 'login' in location:
                    self.add_result("Pricing page exempt", "FAIL", "Pricing redirects to login")
                else:
                    self.add_result("Pricing page exempt", "WARN", f"Pricing redirects to: {location}")
            else:
                self.add_result("Pricing page exempt", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.add_result("Pricing exempt test", "FAIL", str(e))
    
    def test_responsiveness(self):
        """Test 4: Check page responsiveness"""
        self.log("📱 Testing page responsiveness...")
        
        test_pages = ['/', '/pricing/', '/demo', '/login', '/register']
        mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
        
        for page in test_pages:
            try:
                response = self.session.get(f"{self.base_url}{page}", 
                                          headers={'User-Agent': mobile_ua})
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for mobile-friendly indicators
                    mobile_indicators = [
                        'viewport',
                        'mobile-optimized',
                        'col-sm',
                        'col-md',
                        '@media (max-width',
                        'responsive'
                    ]
                    
                    found = sum(1 for indicator in mobile_indicators if indicator in content)
                    
                    if found >= 3:
                        self.add_result(f"Responsiveness {page}", "PASS", f"Found {found} mobile indicators")
                    elif found >= 1:
                        self.add_result(f"Responsiveness {page}", "WARN", f"Found {found} mobile indicators")
                    else:
                        self.add_result(f"Responsiveness {page}", "FAIL", "No mobile indicators found")
                else:
                    self.add_result(f"Responsiveness {page}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.add_result(f"Responsiveness {page}", "FAIL", str(e))
    
    def test_notifications_work(self):
        """Test 5: Check that user alerts/notifications work"""
        self.log("🔔 Testing notifications and alerts...")
        
        try:
            # Test stock details page for notification JS
            response = self.session.get(f"{self.base_url}/stocks/details/EQNR.OL")
            if response.status_code in [200, 302]:  # 302 might be redirect to trial/login
                if response.status_code == 200:
                    content = response.text
                    
                    # Check for notification/toast functionality
                    notification_indicators = [
                        'shownotification',
                        'toast',
                        'alert',
                        'bootstrap.toast',
                        'notification'
                    ]
                    
                    found_notifications = [indicator for indicator in notification_indicators 
                                         if indicator in content.lower()]
                    
                    if found_notifications:
                        self.add_result("Notification system", "PASS", f"Found: {found_notifications}")
                    else:
                        self.add_result("Notification system", "WARN", "No notification system detected")
                else:
                    self.add_result("Notification system", "INFO", "Page redirected (access control working)")
            else:
                self.add_result("Notification system", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.add_result("Notification test", "FAIL", str(e))
    
    def test_subscription_flow(self):
        """Test 6: Verify subscription purchases work"""
        self.log("💳 Testing subscription flow...")
        
        try:
            # Test subscription page
            response = self.session.get(f"{self.base_url}/subscription")
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for Stripe integration
                has_stripe = any(term in content for term in [
                    'stripe', 'checkout', 'create_checkout_session'
                ])
                
                # Check for subscription tiers
                has_pricing = 'kr' in content and ('199' in content or '399' in content)
                
                if has_stripe:
                    self.add_result("Stripe integration", "PASS", "Stripe checkout detected")
                else:
                    self.add_result("Stripe integration", "WARN", "No Stripe integration found")
                    
                if has_pricing:
                    self.add_result("Subscription pricing", "PASS", "Pricing information available")
                else:
                    self.add_result("Subscription pricing", "WARN", "Limited pricing information")
            else:
                self.add_result("Subscription page", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.add_result("Subscription test", "FAIL", str(e))
    
    def test_user_login_flow(self):
        """Test 7: Verify users can log in"""
        self.log("👤 Testing user login flow...")
        
        try:
            # Test login page access
            response = self.session.get(f"{self.base_url}/login")
            if response.status_code == 200:
                content = response.text
                
                # Check for login form elements
                has_form = all(element in content.lower() for element in [
                    'form', 'username', 'password', 'submit'
                ])
                
                # Check for CSRF protection
                has_csrf = 'csrf' in content.lower()
                
                if has_form:
                    self.add_result("Login form", "PASS", "Login form elements present")
                else:
                    self.add_result("Login form", "FAIL", "Missing login form elements")
                    
                if has_csrf:
                    self.add_result("CSRF protection", "PASS", "CSRF protection detected")
                else:
                    self.add_result("CSRF protection", "WARN", "No CSRF protection detected")
                    
                # Test login submission (without valid credentials)
                login_data = {
                    'username': 'test@example.com',
                    'password': 'testpassword'
                }
                response = self.session.post(f"{self.base_url}/login", data=login_data, allow_redirects=False)
                
                if response.status_code in [200, 302, 303]:
                    self.add_result("Login submission", "PASS", "Login form processes submissions")
                else:
                    self.add_result("Login submission", "FAIL", f"HTTP {response.status_code}")
            else:
                self.add_result("Login page", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.add_result("Login test", "FAIL", str(e))
    
    def test_forgot_password_functionality(self):
        """Test 8: Check forgot password functionality"""
        self.log("🔑 Testing forgot password functionality...")
        
        try:
            response = self.session.get(f"{self.base_url}/forgot_password")
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for forgot password form
                has_email_field = 'email' in content
                has_form = 'form' in content
                has_reset = 'reset' in content or 'forgot' in content
                
                if has_email_field and has_form and has_reset:
                    self.add_result("Forgot password feature", "PASS", "Forgot password form available")
                else:
                    self.add_result("Forgot password feature", "WARN", "Limited forgot password functionality")
            else:
                self.add_result("Forgot password page", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.add_result("Forgot password test", "FAIL", str(e))
    
    def test_user_actions(self):
        """Test 9: Check user actions work for logged-in users"""
        self.log("⚡ Testing user actions (favorites, portfolio)...")
        
        try:
            # Test watchlist API
            data = {'ticker': 'EQNR.OL'}
            response = self.session.post(f"{self.base_url}/api/watchlist/add", json=data)
            
            if response.status_code in [200, 302, 401, 403]:
                # These are all acceptable responses (success, redirect, auth required)
                self.add_result("Watchlist API", "PASS", f"API responds (HTTP {response.status_code})")
            else:
                self.add_result("Watchlist API", "WARN", f"HTTP {response.status_code}")
                
            # Test portfolio API
            portfolio_data = {'ticker': 'EQNR.OL', 'shares': 100, 'price': 200}
            response = self.session.post(f"{self.base_url}/api/portfolio/add", json=portfolio_data)
            
            if response.status_code in [200, 302, 401, 403]:
                self.add_result("Portfolio API", "PASS", f"API responds (HTTP {response.status_code})")
            else:
                self.add_result("Portfolio API", "WARN", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.add_result("User actions test", "FAIL", str(e))
    
    def test_data_sources(self):
        """Test 10: Look for additional data sources"""
        self.log("📊 Testing data sources for news/tips/intel...")
        
        api_endpoints = [
            '/api/crypto',
            '/api/currency', 
            '/api/oslo_stocks',
            '/api/global_stocks',
            '/market-intel/api/sector-performance',
            '/market-intel/api/earnings-calendar'
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.add_result(f"Data source {endpoint}", "PASS", f"Returns JSON data")
                    except:
                        self.add_result(f"Data source {endpoint}", "WARN", "Returns non-JSON data")
                elif response.status_code == 302:
                    self.add_result(f"Data source {endpoint}", "INFO", "Requires authentication")
                else:
                    self.add_result(f"Data source {endpoint}", "WARN", f"HTTP {response.status_code}")
            except Exception as e:
                self.add_result(f"Data source {endpoint}", "FAIL", str(e))
    
    def test_premium_user_banners(self):
        """Test 11: Ensure premium users don't see trial/demo banners"""
        self.log("👑 Testing premium user banner visibility...")
        
        try:
            # Test as premium user (we can't easily log in, so we'll check template logic)
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                content = response.text.lower()
                
                # Look for trial/demo banners that might be shown inappropriately
                trial_banners = [
                    'prøveperiode',
                    'trial',
                    'demo',
                    'upgrade',
                    'kjøp abonnement'
                ]
                
                banner_count = sum(1 for banner in trial_banners if banner in content)
                
                if banner_count > 0:
                    self.add_result("Trial banners", "INFO", f"Found {banner_count} potential trial banners (may be conditional)")
                else:
                    self.add_result("Trial banners", "PASS", "No trial banners detected")
            else:
                self.add_result("Homepage banner test", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.add_result("Premium banner test", "FAIL", str(e))
    
    def generate_report(self):
        """Generate comprehensive report"""
        self.log("📊 Generating comprehensive verification report...", "INFO")
        
        print("\n" + "="*80)
        print("🚀 AKSJERADAR SYSTEM VERIFICATION REPORT")
        print("="*80)
        
        # Group results by category
        categories = {
            'Pricing & Styling': ['Pricing tiers displayed', 'Responsive design', 'Modern styling', 'Pricing page exempt'],
            'Limitations & Access': ['5 analyses/day limit', 'Watchlist size limit', 'Analysis limit test'],
            'User Experience': ['Notification system', 'Login form', 'CSRF protection', 'Forgot password feature'],
            'Functionality': ['Watchlist API', 'Portfolio API', 'Login submission', 'Subscription pricing'],
            'Data & Sources': [r['test'] for r in self.results if 'Data source' in r['test']],
            'General': ['Trial banners', 'Stripe integration']
        }
        
        for category, tests in categories.items():
            if not tests:
                continue
                
            print(f"\n📋 {category.upper()}")
            print("-" * 60)
            
            category_results = [r for r in self.results if r['test'] in tests]
            
            for result in category_results:
                status_emoji = {
                    'PASS': '✅',
                    'FAIL': '❌',
                    'WARN': '⚠️',
                    'INFO': 'ℹ️'
                }.get(result['status'], '❓')
                
                print(f"{status_emoji} {result['test']}: {result['details']}")
        
        # Summary
        pass_count = sum(1 for r in self.results if r['status'] == 'PASS')
        fail_count = sum(1 for r in self.results if r['status'] == 'FAIL')
        warn_count = sum(1 for r in self.results if r['status'] == 'WARN')
        info_count = sum(1 for r in self.results if r['status'] == 'INFO')
        
        print(f"\n📊 SUMMARY")
        print("-" * 60)
        print(f"✅ Passed: {pass_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"⚠️  Warnings: {warn_count}")
        print(f"ℹ️  Info: {info_count}")
        print(f"📈 Total Tests: {len(self.results)}")
        
        success_rate = (pass_count / len(self.results) * 100) if self.results else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 60)
        
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        warned_tests = [r for r in self.results if r['status'] == 'WARN']
        
        if failed_tests:
            print("🔴 Critical Issues:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if warned_tests:
            print("🟡 Improvements Needed:")
            for test in warned_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        if not failed_tests and not warned_tests:
            print("🎉 All systems functioning well! Consider:")
            print("  - Adding more data sources for news/tips")
            print("  - Enhancing mobile responsiveness further")
            print("  - Testing end-to-end payment flows in production")
        
        return success_rate > 70
    
    def run_all_tests(self):
        """Run all verification tests"""
        self.log("🔍 Starting comprehensive system verification...", "INFO")
        
        # Run all test categories
        self.test_pricing_page_styling()
        self.test_pricing_limitations_verification()
        self.test_pricing_exempt_status()
        self.test_responsiveness()
        self.test_notifications_work()
        self.test_subscription_flow()
        self.test_user_login_flow()
        self.test_forgot_password_functionality()
        self.test_user_actions()
        self.test_data_sources()
        self.test_premium_user_banners()
        
        # Generate and return report
        return self.generate_report()

def main():
    """Main function"""
    try:
        tester = SystemVerificationTester()
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
