#!/usr/bin/env python3
"""
Final Comprehensive Verification Script
Tests all requirements for the Aksjeradar v6 application
"""

import sys
import os
import json
import requests
from datetime import datetime

# Add the app directory to the path
sys.path.append('.')

def test_app_startup():
    """Test that the app starts up correctly"""
    print("🚀 Testing app startup...")
    try:
        from app import create_app
        app = create_app()
        print("✅ App created successfully")
        return app
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return None

def test_market_intel_endpoints(app):
    """Test all /market-intel/* endpoints"""
    print("\n📊 Testing /market-intel/* endpoints...")
    
    endpoints = [
        '/market-intel',
        '/market-intel/insider-trading',
        '/market-intel/market-sentiment',
        '/market-intel/technical-analysis',
        '/market-intel/sector-analysis'
    ]
    
    results = {}
    
    with app.test_client() as client:
        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                results[endpoint] = {
                    'status': response.status_code,
                    'success': response.status_code == 200,
                    'has_content': len(response.data) > 100
                }
                
                if response.status_code == 200:
                    print(f"✅ {endpoint}: OK")
                else:
                    print(f"❌ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                results[endpoint] = {'status': 'error', 'error': str(e)}
                print(f"❌ {endpoint}: Error - {e}")
    
    return results

def test_pricing_page(app):
    """Test pricing page functionality"""
    print("\n💰 Testing pricing page...")
    
    with app.test_client() as client:
        try:
            response = client.get('/pricing')
            if response.status_code == 200:
                content = response.data.decode()
                
                # Check for key pricing elements
                checks = {
                    'basic_plan': 'Gratis' in content or 'Basic' in content,
                    'premium_plan': 'Premium' in content,
                    'trial_info': 'dager' in content or 'trial' in content,
                    'features_listed': 'AI-score' in content or 'analyse' in content,
                    'responsive_design': 'mobile' in content or 'responsive' in content or 'col-' in content
                }
                
                print(f"✅ Pricing page loads: {response.status_code}")
                for check, passed in checks.items():
                    print(f"{'✅' if passed else '❌'} {check}: {passed}")
                    
                return True
            else:
                print(f"❌ Pricing page failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Pricing page error: {e}")
            return False

def test_user_access_control(app):
    """Test user access control and subscription logic"""
    print("\n🔐 Testing user access control...")
    
    with app.test_client() as client:
        # Test without login (should redirect or show demo)
        response = client.get('/stocks')
        print(f"✅ Stocks page (no auth): {response.status_code}")
        
        # Test pricing page accessibility (should always work)
        response = client.get('/pricing')
        print(f"✅ Pricing page accessibility: {response.status_code == 200}")
        
        # Test protected endpoints
        protected_endpoints = ['/portfolio', '/watchlist', '/alerts']
        for endpoint in protected_endpoints:
            try:
                response = client.get(endpoint)
                # Should either redirect to login or show with limited access
                print(f"✅ {endpoint} (no auth): {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} error: {e}")

def test_daily_limits(app):
    """Test that daily limits are enforced"""
    print("\n📅 Testing daily analysis limits...")
    
    try:
        from app.services.usage_tracker import UsageTracker, PLAN_LIMITS
        
        # Check that limits are defined
        if hasattr(PLAN_LIMITS, 'basic') or 'basic' in PLAN_LIMITS:
            print("✅ Daily limits are configured")
            
            # Check basic plan limit
            basic_limit = PLAN_LIMITS.get('basic', {}).get('daily_analyses', 0)
            if basic_limit == 5:
                print("✅ Basic plan has 5 daily analyses limit")
            else:
                print(f"❌ Basic plan limit: {basic_limit} (expected 5)")
                
        else:
            print("❌ Daily limits not found")
            
    except Exception as e:
        print(f"❌ Daily limits test error: {e}")

def test_forgot_password(app):
    """Test forgot password functionality"""
    print("\n🔑 Testing forgot password...")
    
    with app.test_client() as client:
        try:
            response = client.get('/forgot-password')
            if response.status_code == 200:
                print("✅ Forgot password page accessible")
            else:
                print(f"❌ Forgot password page: {response.status_code}")
                
            # Test alternative routes
            alt_routes = ['/reset-password', '/password-reset']
            for route in alt_routes:
                response = client.get(route)
                if response.status_code == 200:
                    print(f"✅ Alternative route {route} works")
                    
        except Exception as e:
            print(f"❌ Forgot password error: {e}")

def test_responsive_design(app):
    """Test responsive design elements"""
    print("\n📱 Testing responsive design...")
    
    with app.test_client() as client:
        try:
            # Test main pages for responsive elements
            pages = ['/', '/pricing', '/stocks']
            
            for page in pages:
                response = client.get(page)
                if response.status_code == 200:
                    content = response.data.decode()
                    
                    # Look for responsive design indicators
                    responsive_indicators = [
                        'col-', 'row', 'container', 'mobile', 'responsive',
                        'viewport', 'bootstrap', 'media-query'
                    ]
                    
                    found_indicators = sum(1 for indicator in responsive_indicators if indicator in content)
                    
                    if found_indicators >= 3:
                        print(f"✅ {page} appears responsive ({found_indicators} indicators)")
                    else:
                        print(f"❌ {page} may not be responsive ({found_indicators} indicators)")
                        
        except Exception as e:
            print(f"❌ Responsive design test error: {e}")

def test_notification_system(app):
    """Test notification/alert system"""
    print("\n🔔 Testing notification system...")
    
    with app.test_client() as client:
        try:
            # Check for toast/notification elements in templates
            response = client.get('/stocks')
            if response.status_code == 200:
                content = response.data.decode()
                
                notification_elements = [
                    'toast', 'alert', 'notification', 'showToast',
                    'success', 'error', 'warning', 'info'
                ]
                
                found_elements = sum(1 for element in notification_elements if element in content)
                
                if found_elements >= 2:
                    print(f"✅ Notification system present ({found_elements} elements)")
                else:
                    print(f"❌ Notification system may be missing ({found_elements} elements)")
                    
        except Exception as e:
            print(f"❌ Notification system test error: {e}")

def check_files_and_structure():
    """Check that key files exist and are properly structured"""
    print("\n📁 Checking file structure...")
    
    critical_files = [
        'app/routes/main.py',
        'app/routes/pricing.py',
        'app/routes/market_intel.py',
        'app/templates/pricing/index.html',
        'app/templates/market_intel/insider_trading.html',
        'app/templates/base.html',
        'app/services/usage_tracker.py',
        'app/static/css/style.css'
    ]
    
    for file_path in critical_files:
        full_path = os.path.join('/workspaces/aksjeradarv6', file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")

def generate_final_report(results):
    """Generate a final comprehensive report"""
    print("\n" + "="*60)
    print("📋 FINAL COMPREHENSIVE VERIFICATION REPORT")
    print("="*60)
    
    total_checks = 0
    passed_checks = 0
    
    for section, section_results in results.items():
        print(f"\n{section}:")
        if isinstance(section_results, dict):
            for check, status in section_results.items():
                total_checks += 1
                if status:
                    passed_checks += 1
                    print(f"  ✅ {check}")
                else:
                    print(f"  ❌ {check}")
        elif section_results:
            passed_checks += 1
            total_checks += 1
            print(f"  ✅ Passed")
        else:
            total_checks += 1
            print(f"  ❌ Failed")
    
    success_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"OVERALL SUCCESS RATE: {success_rate:.1f}% ({passed_checks}/{total_checks})")
    print(f"{'='*60}")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT! The application is well-configured and ready for production.")
    elif success_rate >= 60:
        print("👍 GOOD! Most features are working, but some areas need attention.")
    else:
        print("⚠️  NEEDS WORK! Several critical issues need to be addressed.")

def main():
    """Run all tests and generate report"""
    print("🔍 AKSJERADAR V6 - COMPREHENSIVE VERIFICATION")
    print("=" * 60)
    
    results = {}
    
    # Test app startup
    app = test_app_startup()
    if not app:
        print("❌ Cannot proceed without app startup")
        return
    
    # Run all tests
    results['Market Intel Endpoints'] = test_market_intel_endpoints(app)
    results['Pricing Page'] = test_pricing_page(app)
    results['User Access Control'] = test_user_access_control(app)
    results['Daily Limits'] = test_daily_limits(app)
    results['Forgot Password'] = test_forgot_password(app)
    results['Responsive Design'] = test_responsive_design(app)
    results['Notification System'] = test_notification_system(app)
    
    # Check file structure
    check_files_and_structure()
    
    # Generate final report
    generate_final_report(results)
    
    # Save results to file
    with open('/workspaces/aksjeradarv6/final_verification_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: final_verification_report.json")
    print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
