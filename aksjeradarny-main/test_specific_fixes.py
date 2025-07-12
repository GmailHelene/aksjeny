#!/usr/bin/env python3
"""
Test specific fixes for the Aksjeradar app
Check if the reported issues are resolved
"""

import requests
import sys
from datetime import datetime

class SpecificFixesTester:
    def __init__(self, base_url='http://localhost:5001'):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def log(self, message, status=None):
        prefix = ""
        if status == "PASS":
            prefix = "✅ "
        elif status == "FAIL":
            prefix = "❌ "
        elif status == "WARN":
            prefix = "⚠️ "
        else:
            prefix = "ℹ️ "
        print(f"{prefix}{message}")
        
    def test_result(self, test_name, status, details=""):
        result = f"{test_name}: {status}"
        if details:
            result += f" - {details}"
        self.results.append((test_name, status, details))
        self.log(result, status)
        
    def test_subscription_endpoint(self):
        """Test if /subscription endpoint returns 500 error"""
        self.log("Testing /subscription endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/subscription")
            if response.status_code == 200:
                self.test_result('/subscription', 'PASS', 'Loads without 500 error')
            elif response.status_code == 500:
                self.test_result('/subscription', 'FAIL', 'Still returns 500 error')
            else:
                self.test_result('/subscription', 'WARN', f'Returns {response.status_code}')
        except Exception as e:
            self.test_result('/subscription', 'FAIL', f'Exception: {str(e)}')
            
    def test_premium_endpoints_redirect(self):
        """Test if premium endpoints properly redirect unauthorized users"""
        self.log("Testing premium endpoint redirects...")
        
        premium_endpoints = [
            '/stocks/details/EQNR.OL',
            '/analysis/market-overview', 
            '/portfolio',
            '/stocks/list',
            '/analysis/technical/EQNR.OL'
        ]
        
        for endpoint in premium_endpoints:
            try:
                # Test without authentication
                response = self.session.get(f"{self.base_url}{endpoint}", allow_redirects=False)
                if response.status_code == 302:
                    redirect_location = response.headers.get('Location', '')
                    if 'login' in redirect_location or 'register' in redirect_location or 'restricted' in redirect_location:
                        self.test_result(f'{endpoint} redirect', 'PASS', f'Redirects to {redirect_location}')
                    else:
                        self.test_result(f'{endpoint} redirect', 'WARN', f'Redirects to {redirect_location}')
                elif response.status_code == 200:
                    # Could be that trial is still active or endpoint allows access
                    self.test_result(f'{endpoint} access', 'WARN', 'Allows access (trial may be active)')
                else:
                    self.test_result(f'{endpoint} response', 'FAIL', f'Returns {response.status_code}')
            except Exception as e:
                self.test_result(f'{endpoint} error', 'FAIL', f'Exception: {str(e)}')
                
    def test_trial_expiration(self):
        """Test trial expiration logic"""
        self.log("Testing trial expiration...")
        
        try:
            # Create a new session to simulate fresh visitor
            fresh_session = requests.Session()
            
            # Visit homepage first
            response = fresh_session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.test_result('Homepage access', 'PASS', 'Can access homepage')
            
            # Try to access a premium feature immediately (should work during trial)
            response = fresh_session.get(f"{self.base_url}/stocks/details/EQNR.OL")
            if response.status_code == 200:
                self.test_result('Premium access (trial)', 'PASS', 'Can access during trial')
            elif response.status_code == 302:
                self.test_result('Premium access (trial)', 'WARN', 'Redirected immediately (no trial?)')
            else:
                self.test_result('Premium access (trial)', 'FAIL', f'Returns {response.status_code}')
                
        except Exception as e:
            self.test_result('Trial test', 'FAIL', f'Exception: {str(e)}')
            
    def test_app_connectivity(self):
        """Test basic app connectivity"""
        self.log("Testing app connectivity...")
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.test_result('App connectivity', 'PASS', 'App is running and responding')
                return True
            else:
                self.test_result('App connectivity', 'FAIL', f'Returns {response.status_code}')
                return False
        except requests.exceptions.ConnectionError:
            self.test_result('App connectivity', 'FAIL', 'Cannot connect to app - Flask may not be running')
            self.log("Please start Flask with: python run.py")
            return False
        except Exception as e:
            self.test_result('App connectivity', 'FAIL', f'Exception: {str(e)}')
            return False
            
    def run_all_tests(self):
        """Run all specific fix tests"""
        self.log("=" * 50)
        self.log("SPECIFIC FIXES VERIFICATION")
        self.log("=" * 50)
        
        # Test basic connectivity first
        if not self.test_app_connectivity():
            self.log("❌ Cannot connect to app. Please ensure Flask is running on port 5001")
            return False
            
        self.test_subscription_endpoint()
        self.test_premium_endpoints_redirect()
        self.test_trial_expiration()
        
        # Summary
        self.log("=" * 50)
        self.log("TEST SUMMARY")
        self.log("=" * 50)
        
        passed = sum(1 for _, status, _ in self.results if status == 'PASS')
        failed = sum(1 for _, status, _ in self.results if status == 'FAIL')
        warned = sum(1 for _, status, _ in self.results if status == 'WARN')
        
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Warnings: {warned}")
        
        if failed == 0:
            self.log("🎉 All tests passed or have warnings only!")
        else:
            self.log("💡 Some issues need attention")
            
        return failed == 0

if __name__ == "__main__":
    tester = SpecificFixesTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
