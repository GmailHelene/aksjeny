#!/usr/bin/env python3
"""
Access Control and Demo Functionality Tester
Specifically tests demo access for unauthenticated users and paid features for subscribers
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

class AccessTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []

    def test_demo_access_unauthenticated(self):
        """Test that demo works for unauthenticated users"""
        print("🎮 Testing Demo Access for Unauthenticated Users")
        print("-" * 50)
        
        demo_tests = [
            ('/demo', 'Demo Landing Page'),
            ('/demo/stocks', 'Demo Stocks Page'),
            ('/demo/portfolio', 'Demo Portfolio'),
            ('/demo/analysis', 'Demo Analysis'),
            ('/api/demo/stocks', 'Demo API - Stocks'),
            ('/api/demo/market-data', 'Demo API - Market Data'),
            ('/api/demo/portfolio', 'Demo API - Portfolio'),
        ]
        
        for endpoint, name in demo_tests:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for demo content indicators
                    demo_indicators = ['demo', 'test data', 'sample', 'example']
                    has_demo_content = any(indicator in content for indicator in demo_indicators)
                    
                    # Check that it doesn't require subscription
                    requires_subscription = any(phrase in content for phrase in [
                        'subscription required', 'upgrade to pro', 'premium feature'
                    ])
                    
                    success = has_demo_content and not requires_subscription
                    status = "✅ PASS" if success else "❌ FAIL"
                    
                    print(f"{status} {name}")
                    if has_demo_content:
                        print(f"    ✓ Contains demo content")
                    if not requires_subscription:
                        print(f"    ✓ No subscription required")
                    
                else:
                    print(f"❌ FAIL {name} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ ERROR {name} - {str(e)}")

    def test_subscription_required_features(self):
        """Test that premium features require subscription"""
        print("\n💳 Testing Subscription-Required Features")
        print("-" * 50)
        
        premium_endpoints = [
            ('/portfolio', 'Portfolio Management'),
            ('/analysis/advanced', 'Advanced Analysis'),
            ('/api/realtime', 'Real-time Data'),
            ('/api/ai-recommendations', 'AI Recommendations'),
            ('/notifications', 'Notifications'),
            ('/settings', 'Settings'),
        ]
        
        for endpoint, name in premium_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                # Should redirect to login or show subscription required
                if response.status_code in [302, 401, 403]:
                    print(f"✅ PASS {name} - Properly protected (Status: {response.status_code})")
                elif response.status_code == 200:
                    content = response.text.lower()
                    requires_auth = any(phrase in content for phrase in [
                        'login required', 'please log in', 'authentication required'
                    ])
                    requires_subscription = any(phrase in content for phrase in [
                        'subscription required', 'upgrade to pro', 'premium feature'
                    ])
                    
                    if requires_auth or requires_subscription:
                        print(f"✅ PASS {name} - Shows authentication/subscription requirement")
                    else:
                        print(f"❌ FAIL {name} - Accessible without authentication")
                else:
                    print(f"⚠️  UNKNOWN {name} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ ERROR {name} - {str(e)}")

    def test_demo_limitations(self):
        """Test that demo has appropriate limitations"""
        print("\n🔒 Testing Demo Limitations")
        print("-" * 50)
        
        # Test demo API endpoints for limitations
        demo_api_tests = [
            ('/api/demo/stocks', 'Demo Stocks API'),
            ('/api/demo/market-data', 'Demo Market Data API'),
        ]
        
        for endpoint, name in demo_api_tests:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Check for demo limitations
                        limitations_found = []
                        
                        if isinstance(data, list) and len(data) <= 10:
                            limitations_found.append("Limited to 10 items or less")
                        
                        if isinstance(data, dict):
                            if 'demo' in str(data).lower():
                                limitations_found.append("Contains demo markers")
                            if 'limited' in str(data).lower():
                                limitations_found.append("Contains limitation notices")
                        
                        if limitations_found:
                            print(f"✅ PASS {name} - Has appropriate limitations:")
                            for limitation in limitations_found:
                                print(f"    • {limitation}")
                        else:
                            print(f"⚠️  WARNING {name} - No obvious limitations detected")
                    
                    except json.JSONDecodeError:
                        print(f"⚠️  WARNING {name} - Non-JSON response")
                
                else:
                    print(f"❌ FAIL {name} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ ERROR {name} - {str(e)}")

    def test_paid_user_simulation(self):
        """Simulate paid user access (without actual login)"""
        print("\n👤 Testing Paid User Feature Access")
        print("-" * 50)
        
        # Test endpoints that should be available to paid users
        # Note: This tests the endpoint existence, not actual auth
        paid_features = [
            ('/api/portfolio/create', 'Portfolio Creation API'),
            ('/api/watchlist', 'Watchlist API'),
            ('/api/notifications', 'Notifications API'),
            ('/api/analysis/advanced', 'Advanced Analysis API'),
        ]
        
        for endpoint, name in paid_features:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                # These should exist but require authentication
                if response.status_code in [401, 403]:
                    print(f"✅ PASS {name} - Endpoint exists, requires authentication")
                elif response.status_code == 302:
                    location = response.headers.get('Location', '')
                    if 'login' in location.lower():
                        print(f"✅ PASS {name} - Redirects to login")
                    else:
                        print(f"⚠️  WARNING {name} - Redirects to: {location}")
                elif response.status_code == 404:
                    print(f"❌ FAIL {name} - Endpoint not found")
                else:
                    print(f"⚠️  UNKNOWN {name} - Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ ERROR {name} - {str(e)}")

    def run_access_tests(self):
        """Run all access control tests"""
        print("🔐 AKSJERADAR ACCESS CONTROL TESTER")
        print("=" * 60)
        
        # Test server availability first
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                print("❌ Server not responding. Please start the application first.")
                return False
        except:
            print("❌ Cannot connect to server. Please start the application first.")
            return False
        
        print("✅ Server is running\n")
        
        # Run access control tests
        self.test_demo_access_unauthenticated()
        self.test_subscription_required_features()
        self.test_demo_limitations()
        self.test_paid_user_simulation()
        
        print("\n" + "=" * 60)
        print("🏁 ACCESS CONTROL TESTING COMPLETE")
        return True


if __name__ == "__main__":
    tester = AccessTester()
    tester.run_access_tests()
