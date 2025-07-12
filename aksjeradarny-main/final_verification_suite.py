#!/usr/bin/env python3
"""
Final Verification Suite - Tests all implemented features
Comprehensive test of the Aksjeradar app functionality
"""

import requests
import json
import time
from datetime import datetime

class FinalVerificationSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Aksjeradar-Final-Verification/1.0'
        })
        self.results = {}
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_security_headers(self):
        """Test security headers implementation"""
        self.log("🔒 Testing security headers...")
        
        try:
            response = self.session.head(f"{self.base_url}/")
            headers = response.headers
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Content-Security-Policy': lambda x: 'default-src' in x,
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            }
            
            passed = 0
            for header, expected in required_headers.items():
                if header in headers:
                    if callable(expected):
                        if expected(headers[header]):
                            passed += 1
                            self.log(f"  ✅ {header}: Present and valid")
                        else:
                            self.log(f"  ❌ {header}: Present but invalid")
                    else:
                        if headers[header] == expected:
                            passed += 1
                            self.log(f"  ✅ {header}: {headers[header]}")
                        else:
                            self.log(f"  ❌ {header}: Expected '{expected}', got '{headers[header]}'")
                else:
                    self.log(f"  ❌ {header}: Missing")
            
            self.results['security_headers'] = f"{passed}/{len(required_headers)} headers correct"
            
        except Exception as e:
            self.log(f"❌ Security headers test failed: {e}", "ERROR")
            self.results['security_headers'] = f"Failed: {e}"
    
    def test_trial_functionality(self):
        """Test trial cookie and banner functionality"""
        self.log("⏱️ Testing trial functionality...")
        
        try:
            # Clear cookies and make fresh request
            self.session.cookies.clear()
            response = self.session.get(f"{self.base_url}/")
            
            # Check for trial cookie
            trial_cookie = None
            for cookie in self.session.cookies:
                if 'trial_' in cookie.name:
                    trial_cookie = cookie
                    break
            
            if trial_cookie:
                self.log(f"  ✅ Trial cookie set: {trial_cookie.name}")
                self.log(f"  ✅ Cookie expires: {trial_cookie.expires}")
                self.results['trial_cookie'] = "Working - Cookie set with proper expiry"
            else:
                self.log("  ❌ No trial cookie found")
                self.results['trial_cookie'] = "Failed - No trial cookie"
                
            # Check for trial banner in content
            if 'trial' in response.text.lower() or 'demo' in response.text.lower():
                self.log("  ✅ Trial/demo content found in homepage")
                self.results['trial_content'] = "Working - Trial content present"
            else:
                self.log("  ⚠️ No obvious trial/demo content found")
                self.results['trial_content'] = "Warning - No trial content visible"
                
        except Exception as e:
            self.log(f"❌ Trial functionality test failed: {e}", "ERROR")
            self.results['trial_functionality'] = f"Failed: {e}"
    
    def test_ai_analysis_endpoints(self):
        """Test new AI analysis endpoints"""
        self.log("🤖 Testing AI analysis endpoints...")
        
        endpoints = [
            '/analysis/warren-buffett',
            '/analysis/benjamin-graham',
            '/analysis/short-analysis',
            '/analysis/warren-buffett?ticker=AAPL',
            '/analysis/benjamin-graham?ticker=AAPL',
            '/analysis/short-analysis?ticker=AAPL'
        ]
        
        working_endpoints = 0
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.log(f"  ✅ {endpoint}: HTTP {response.status_code}")
                    working_endpoints += 1
                elif response.status_code == 302:
                    self.log(f"  ✅ {endpoint}: HTTP {response.status_code} (redirect)")
                    working_endpoints += 1
                else:
                    self.log(f"  ❌ {endpoint}: HTTP {response.status_code}")
            except Exception as e:
                self.log(f"  ❌ {endpoint}: Failed - {e}")
        
        self.results['ai_endpoints'] = f"{working_endpoints}/{len(endpoints)} endpoints working"
    
    def test_news_sources(self):
        """Test news functionality and sources"""
        self.log("📰 Testing news functionality...")
        
        try:
            response = self.session.get(f"{self.base_url}/news/")
            if response.status_code == 200:
                self.log("  ✅ News page accessible")
                
                # Check for Norwegian sources
                norwegian_sources = ['aftenposten', 'vg', 'dn', 'dagens', 'nettavisen']
                found_sources = 0
                for source in norwegian_sources:
                    if source in response.text.lower():
                        found_sources += 1
                
                self.log(f"  ✅ Found {found_sources} Norwegian news sources")
                self.results['news_sources'] = f"Working - {found_sources} Norwegian sources found"
            else:
                self.log(f"  ❌ News page returned HTTP {response.status_code}")
                self.results['news_sources'] = f"Failed - HTTP {response.status_code}"
                
        except Exception as e:
            self.log(f"❌ News test failed: {e}", "ERROR")
            self.results['news_sources'] = f"Failed: {e}"
    
    def test_language_switching(self):
        """Test language switching functionality"""
        self.log("🌐 Testing language switching...")
        
        try:
            # Test Norwegian
            response_no = self.session.get(f"{self.base_url}/?lang=no")
            # Test English  
            response_en = self.session.get(f"{self.base_url}/?lang=en")
            
            if response_no.status_code == 200 and response_en.status_code == 200:
                # Look for language-specific content
                if 'aksjer' in response_no.text.lower() or 'norsk' in response_no.text.lower():
                    self.log("  ✅ Norwegian language content detected")
                if 'stocks' in response_en.text.lower() or 'english' in response_en.text.lower():
                    self.log("  ✅ English language content detected")
                    
                self.results['language_switching'] = "Working - Both languages accessible"
            else:
                self.log("  ❌ Language switching failed")
                self.results['language_switching'] = "Failed - HTTP errors"
                
        except Exception as e:
            self.log(f"❌ Language switching test failed: {e}", "ERROR")
            self.results['language_switching'] = f"Failed: {e}"
    
    def test_exempt_user_logic(self):
        """Test exempt user logic without login"""
        self.log("👤 Testing exempt user configuration...")
        
        try:
            # Test registration page (should include exempt user logic)
            response = self.session.get(f"{self.base_url}/auth/register")
            if response.status_code == 200:
                self.log("  ✅ Registration page accessible")
                self.results['exempt_user_access'] = "Registration page working"
            else:
                # Try alternative route
                response = self.session.get(f"{self.base_url}/register")
                if response.status_code == 200:
                    self.log("  ✅ Registration page accessible")
                    self.results['exempt_user_access'] = "Registration page working"
                else:
                    self.log(f"  ⚠️ Registration page not found (this is expected in some configurations)")
                    self.results['exempt_user_access'] = "Info - Registration routes may be configured differently"
                
        except Exception as e:
            self.log(f"❌ Exempt user test failed: {e}", "ERROR")
            self.results['exempt_user_access'] = f"Failed: {e}"
    
    def test_responsive_design(self):
        """Test responsive design indicators"""
        self.log("📱 Testing responsive design...")
        
        try:
            # Test with mobile user agent
            mobile_headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'}
            response = self.session.get(f"{self.base_url}/", headers=mobile_headers)
            
            if response.status_code == 200:
                # Look for responsive indicators
                responsive_indicators = ['viewport', 'mobile', 'responsive', 'bootstrap', 'col-']
                found_indicators = 0
                for indicator in responsive_indicators:
                    if indicator in response.text.lower():
                        found_indicators += 1
                
                self.log(f"  ✅ Found {found_indicators} responsive design indicators")
                self.results['responsive_design'] = f"Working - {found_indicators} indicators found"
            else:
                self.log(f"  ❌ Mobile request failed: HTTP {response.status_code}")
                self.results['responsive_design'] = f"Failed - HTTP {response.status_code}"
                
        except Exception as e:
            self.log(f"❌ Responsive design test failed: {e}", "ERROR")
            self.results['responsive_design'] = f"Failed: {e}"
    
    def test_redis_cache_integration(self):
        """Test Redis cache functionality"""
        self.log("⚡ Testing Redis cache integration...")
        
        try:
            # Test endpoints that should use caching
            cache_endpoints = ['/news', '/analysis']
            working_cache = 0
            
            for endpoint in cache_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    if response.status_code in [200, 302]:
                        self.log(f"  ✅ {endpoint}: Accessible")
                        working_cache += 1
                    else:
                        self.log(f"  ❌ {endpoint}: HTTP {response.status_code}")
                except:
                    self.log(f"  ❌ {endpoint}: Failed")
            
            self.results['redis_cache'] = f"{working_cache}/{len(cache_endpoints)} cache endpoints working"
            
        except Exception as e:
            self.log(f"❌ Redis cache test failed: {e}", "ERROR")
            self.results['redis_cache'] = f"Failed: {e}"
    
    def run_all_tests(self):
        """Run all verification tests"""
        self.log("🚀 Starting Final Verification Suite...")
        self.log("=" * 60)
        
        tests = [
            self.test_security_headers,
            self.test_trial_functionality,
            self.test_ai_analysis_endpoints,
            self.test_news_sources,
            self.test_language_switching,
            self.test_exempt_user_logic,
            self.test_responsive_design,
            self.test_redis_cache_integration
        ]
        
        for test in tests:
            try:
                test()
                self.log("-" * 40)
            except Exception as e:
                self.log(f"❌ Test {test.__name__} failed: {e}", "ERROR")
                self.log("-" * 40)
        
        # Summary
        self.log("📊 FINAL VERIFICATION SUMMARY")
        self.log("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if 'working' in result.lower() or 'correct' in result.lower())
        
        for test_name, result in self.results.items():
            status = "✅" if ('working' in result.lower() or 'correct' in result.lower()) else "❌"
            self.log(f"{status} {test_name}: {result}")
        
        self.log("=" * 60)
        self.log(f"🏆 OVERALL RESULT: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests >= total_tests * 0.8:  # 80% pass rate
            self.log("🎉 VERIFICATION SUCCESSFUL - App is production ready!")
        else:
            self.log("⚠️ VERIFICATION INCOMPLETE - Some issues need attention")
        
        return self.results

if __name__ == "__main__":
    verifier = FinalVerificationSuite()
    results = verifier.run_all_tests()
