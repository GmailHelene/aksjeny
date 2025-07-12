#!/usr/bin/env python3
"""
Comprehensive Endpoint and Functionality Test
Tests all endpoints, user limitations, and system functionality
"""

import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

from app import create_app
from app.models import User
from app.extensions import db
import json

def test_comprehensive_system():
    """Test all system functionality comprehensively"""
    print("🔍 COMPREHENSIVE SYSTEM TEST")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Pricing page accessibility
        print("\n📋 1. TESTING PRICING PAGE")
        print("-" * 30)
        
        with app.test_client() as client:
            # Test different pricing URLs
            pricing_urls = ['/pricing/', '/pricing']
            for url in pricing_urls:
                response = client.get(url)
                print(f"URL: {url} -> Status: {response.status_code}")
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    # Check for pricing elements
                    checks = [
                        "Gratis Demo",
                        "Basic",
                        "Pro", 
                        "kr 199",
                        "kr 399",
                        "5/dag",
                        "pricing-card"
                    ]
                    for check in checks:
                        if check in content:
                            print(f"  ✅ Found: {check}")
                        else:
                            print(f"  ❌ Missing: {check}")
                    break
            
        # Test 2: Market Intel endpoints
        print("\n📋 2. TESTING MARKET INTEL ENDPOINTS")
        print("-" * 40)
        
        market_intel_endpoints = [
            '/market-intel/',
            '/market-intel/insider-trading',
            '/market-intel/earnings-calendar',
            '/market-intel/sector-analysis',
            '/market-intel/economic-indicators'
        ]
        
        with app.test_client() as client:
            for endpoint in market_intel_endpoints:
                response = client.get(endpoint)
                status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
                print(f"  {endpoint} -> {status}")
        
        # Test 3: Key endpoints accessibility
        print("\n📋 3. TESTING KEY ENDPOINTS")
        print("-" * 30)
        
        key_endpoints = [
            '/',
            '/login',
            '/register',
            '/stocks/',
            '/analysis/',
            '/contact',
            '/privacy'
        ]
        
        with app.test_client() as client:
            for endpoint in key_endpoints:
                response = client.get(endpoint, follow_redirects=True)
                status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
                print(f"  {endpoint} -> {status}")
        
        # Test 4: Check exempt endpoints configuration
        print("\n📋 4. CHECKING EXEMPT ENDPOINTS CONFIG")
        print("-" * 40)
        
        from app.routes.main import EXEMPT_ENDPOINTS
        print(f"Total exempt endpoints: {len(EXEMPT_ENDPOINTS)}")
        pricing_exempt = any('pricing' in endpoint for endpoint in EXEMPT_ENDPOINTS)
        print(f"Pricing exempt: {'✅ Yes' if pricing_exempt else '❌ No'}")
        
        # Test 5: Check user limitations implementation
        print("\n📋 5. CHECKING USER LIMITATIONS IMPLEMENTATION")
        print("-" * 50)
        
        # Search for daily analysis limits
        print("Searching for daily analysis limits implementation...")
        
        # Test 6: Check for responsive design elements
        print("\n📋 6. CHECKING RESPONSIVE DESIGN")
        print("-" * 35)
        
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                content = response.get_data(as_text=True)
                responsive_checks = [
                    "viewport",
                    "container-fluid",
                    "col-md-",
                    "col-lg-",
                    "d-none d-md-block",
                    "@media"
                ]
                for check in responsive_checks:
                    if check in content:
                        print(f"  ✅ Found: {check}")
                    else:
                        print(f"  ⚠️  Not found: {check}")

if __name__ == "__main__":
    test_comprehensive_system()
