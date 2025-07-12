#!/usr/bin/env python3
"""
Comprehensive Access Control Test for Aksjeradar V6

This script tests the strict access control implementation:
1. Expired trial users can ONLY access: /demo, /login, /register, /logout, /subscription, /privacy
2. All other pages redirect to /demo
3. Demo page shows trial expiration info and CTAs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from flask import url_for
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

class AccessControlTester:
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.base_url = "http://localhost:5000"
        
        # Endpoints that should be accessible for expired trial users
        self.unrestricted_endpoints = [
            '/demo',
            '/login', 
            '/register',
            '/logout',
            '/subscription',
            '/privacy',
            '/privacy-policy',
            '/api/trial-status',
            '/manifest.json',
            '/service-worker.js',
            '/version'
        ]
        
        # Endpoints that should redirect expired users to /demo
        self.restricted_endpoints = [
            '/',
            '/ai-explained',
            '/search',
            '/stocks',
            '/analysis',
            '/portfolio',
            '/market-intel',
            '/features/notifications',
            '/features/alerts',
            '/resources'
        ]
        
    def simulate_expired_trial(self):
        """Simulate an expired trial by setting old trial cookie"""
        with self.client.session_transaction() as sess:
            # Set trial start time to more than 15 minutes ago
            expired_time = '2024-01-01T10:00:00'
            device_fingerprint = 'test_device_12345'
            trial_key = f"trial_{device_fingerprint}"
            sess[trial_key] = expired_time
            # Clear any user authentication
            sess.pop('_user_id', None)
        
        # Also set cookie for consistency
        self.client.set_cookie('localhost', f'trial_{device_fingerprint}', expired_time)
    
    def test_unrestricted_access(self):
        """Test that unrestricted endpoints are accessible for expired users"""
        print("🔍 Testing unrestricted endpoint access...")
        results = []
        
        for endpoint in self.unrestricted_endpoints:
            try:
                response = self.client.get(endpoint)
                status = response.status_code
                
                if status == 200:
                    result = f"✅ {endpoint} - Accessible (200)"
                elif status in [301, 302]:
                    location = response.headers.get('Location', '')
                    result = f"⚠️  {endpoint} - Redirect ({status}) to {location}"
                else:
                    result = f"❌ {endpoint} - Error ({status})"
                
                results.append(result)
                print(f"   {result}")
                
            except Exception as e:
                result = f"❌ {endpoint} - Exception: {str(e)}"
                results.append(result)
                print(f"   {result}")
        
        return results
    
    def test_restricted_access(self):
        """Test that restricted endpoints redirect expired users to /demo"""
        print("\n🔒 Testing restricted endpoint access (should redirect to /demo)...")
        results = []
        
        for endpoint in self.restricted_endpoints:
            try:
                response = self.client.get(endpoint, follow_redirects=False)
                status = response.status_code
                location = response.headers.get('Location', '')
                
                if status in [301, 302, 303] and '/demo' in location:
                    result = f"✅ {endpoint} - Correctly redirects to {location}"
                elif status == 200:
                    result = f"❌ {endpoint} - Should redirect but returned 200"
                else:
                    result = f"⚠️  {endpoint} - Unexpected response ({status}) {location}"
                
                results.append(result)
                print(f"   {result}")
                
            except Exception as e:
                result = f"❌ {endpoint} - Exception: {str(e)}"
                results.append(result)
                print(f"   {result}")
        
        return results
    
    def test_demo_page_content(self):
        """Test that demo page contains required CTAs and messaging"""
        print("\n📄 Testing demo page content...")
        
        try:
            response = self.client.get('/demo')
            content = response.get_data(as_text=True)
            
            checks = [
                ('trial expiration message', any(phrase in content.lower() for phrase in [
                    'prøveperiode', 'prøveperioden', 'utløpt', 'expired'
                ])),
                ('registration CTA', 'registrer' in content.lower() and 'url_for(\'main.register\')' in content),
                ('login CTA', 'logg inn' in content.lower() and 'url_for(\'main.login\')' in content),
                ('subscription CTA', any(phrase in content.lower() for phrase in [
                    'abonnement', 'subscription', 'priser'
                ]) and 'url_for(\'main.subscription\')' in content),
                ('demo explanation', 'demo' in content.lower()),
                ('feature limitations', any(phrase in content.lower() for phrase in [
                    'begrenset', 'ikke får', 'ikke tilgang'
                ]))
            ]
            
            results = []
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                result = f"{status} {check_name}: {'FOUND' if passed else 'MISSING'}"
                results.append(result)
                print(f"   {result}")
            
            return results
            
        except Exception as e:
            error_result = f"❌ Demo page test failed: {str(e)}"
            print(f"   {error_result}")
            return [error_result]
    
    def test_ajax_access_control(self):
        """Test that AJAX requests are properly handled"""
        print("\n🔄 Testing AJAX access control...")
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
        
        try:
            response = self.client.get('/', headers=headers, follow_redirects=False)
            
            if response.status_code == 403:
                try:
                    json_data = response.get_json()
                    if json_data and 'error' in json_data and 'redirect' in json_data:
                        result = "✅ AJAX requests return proper JSON error with redirect"
                    else:
                        result = "⚠️  AJAX requests return 403 but missing proper JSON structure"
                except:
                    result = "⚠️  AJAX requests return 403 but not valid JSON"
            else:
                result = f"❌ AJAX requests should return 403, got {response.status_code}"
            
            print(f"   {result}")
            return [result]
            
        except Exception as e:
            error_result = f"❌ AJAX test failed: {str(e)}"
            print(f"   {error_result}")
            return [error_result]
    
    def run_full_test(self):
        """Run comprehensive access control test suite"""
        print("🧪 COMPREHENSIVE ACCESS CONTROL TEST")
        print("=" * 50)
        
        # Simulate expired trial
        self.simulate_expired_trial()
        print("🕐 Simulated expired trial (15+ minutes ago)")
        
        # Run all tests
        unrestricted_results = self.test_unrestricted_access()
        restricted_results = self.test_restricted_access()
        demo_results = self.test_demo_page_content()
        ajax_results = self.test_ajax_access_control()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        
        all_results = unrestricted_results + restricted_results + demo_results + ajax_results
        passed = len([r for r in all_results if r.startswith('✅')])
        failed = len([r for r in all_results if r.startswith('❌')])
        warnings = len([r for r in all_results if r.startswith('⚠️')])
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        print(f"📊 Total: {len(all_results)}")
        
        if failed == 0:
            print("\n🎉 ALL ACCESS CONTROL TESTS PASSED!")
            print("The strict access control is working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Please review the implementation.")
        
        return {
            'passed': passed,
            'failed': failed,
            'warnings': warnings,
            'total': len(all_results),
            'results': all_results
        }

def main():
    """Main test function"""
    tester = AccessControlTester()
    results = tester.run_full_test()
    
    # Exit with error code if tests failed
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
