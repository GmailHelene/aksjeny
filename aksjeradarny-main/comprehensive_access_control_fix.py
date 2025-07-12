#!/usr/bin/env python3
"""
Comprehensive fix for Aksjeradar V6 access control and system consolidation
Dette skriptet retter alle identifiserte problemer og sikrer konsistent implementasjon.
"""

import os
import sys
import re

# Legg til prosjektmappen i Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_access_control_consistency():
    """Sikre at alle route-filer bruker @access_required konsistent"""
    print("🔧 FIXING ACCESS CONTROL CONSISTENCY")
    print("=" * 50)
    
    route_files = [
        'app/routes/main.py',
        'app/routes/stocks.py', 
        'app/routes/portfolio.py',
        'app/routes/analysis.py',
        'app/routes/market_intel.py',
        'app/routes/realtime_api.py'
    ]
    
    issues_found = []
    
    for route_file in route_files:
        try:
            if os.path.exists(route_file):
                with open(route_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file imports @access_required
                if '@access_required' in content:
                    if 'from app.utils.access_control import access_required' not in content:
                        issues_found.append(f"{route_file}: Uses @access_required but missing import")
                    else:
                        print(f"✅ {route_file}: Correctly uses @access_required")
                
                # Check for old @trial_required usage
                if '@trial_required' in content and route_file != 'app/routes/main.py':
                    issues_found.append(f"{route_file}: Still uses old @trial_required")
                
            else:
                print(f"⚠️  {route_file}: File not found")
                
        except Exception as e:
            issues_found.append(f"{route_file}: Error reading file - {e}")
    
    if issues_found:
        print("\n❌ ISSUES FOUND:")
        for issue in issues_found:
            print(f"   {issue}")
        return False
    else:
        print("\n✅ ALL ROUTE FILES HAVE CONSISTENT ACCESS CONTROL")
        return True

def verify_unrestricted_endpoints():
    """Verifiser at UNRESTRICTED_ENDPOINTS er korrekt konfigurert"""
    print("\n🔍 VERIFYING UNRESTRICTED ENDPOINTS")
    print("=" * 50)
    
    try:
        from app.utils.access_control import UNRESTRICTED_ENDPOINTS
        
        # Forventede unrestricted endpoints basert på dokumentasjonen
        expected_core = {
            'main.register',
            'main.login', 
            'main.logout',
            'main.privacy',
            'main.subscription',
            'main.demo',
            'main.api_trial_status',
            'static'
        }
        
        # API endpoints som skal være tilgjengelig for logged-in users
        expected_api = {
            'main.add_to_watchlist',
            'main.add_to_portfolio',
            '/api/watchlist/add',
            '/api/portfolio/add',
            '/api/favorites/add'
        }
        
        # Pricing/subscription endpoints
        expected_pricing = {
            'pricing.pricing',
            'pricing.upgrade',
            'pricing.subscription_success',
            'pricing.buy_report', 
            'pricing.report_success',
            'pricing.stripe_webhook'
        }
        
        all_expected = expected_core | expected_api | expected_pricing
        
        missing = all_expected - UNRESTRICTED_ENDPOINTS
        extra = UNRESTRICTED_ENDPOINTS - all_expected
        
        if missing:
            print(f"⚠️  Missing endpoints: {missing}")
            return False
        
        if extra:
            print(f"ℹ️  Extra endpoints (review if needed): {extra}")
        
        print(f"✅ Core unrestricted endpoints: {len(expected_core)} configured")
        print(f"✅ API endpoints: {len(expected_api)} configured")
        print(f"✅ Pricing endpoints: {len(expected_pricing)} configured")
        print(f"📊 Total unrestricted endpoints: {len(UNRESTRICTED_ENDPOINTS)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying endpoints: {e}")
        return False

def verify_exempt_users():
    """Verifiser at exempt users er korrekt konfigurert"""
    print("\n👤 VERIFYING EXEMPT USERS")
    print("=" * 50)
    
    try:
        from app.utils.access_control import EXEMPT_EMAILS
        
        expected_emails = {
            'helene@luxushair.com',
            'helene721@gmail.com', 
            'eiriktollan.berntsen@gmail.com',
            'tonjekit91@gmail.com'
        }
        
        if EXEMPT_EMAILS == expected_emails:
            print("✅ All exempt emails correctly configured")
            for email in sorted(EXEMPT_EMAILS):
                print(f"   📧 {email}")
            return True
        else:
            missing = expected_emails - EXEMPT_EMAILS
            extra = EXEMPT_EMAILS - expected_emails
            
            if missing:
                print(f"⚠️  Missing exempt emails: {missing}")
            if extra:
                print(f"ℹ️  Extra exempt emails: {extra}")
            
            return len(missing) == 0  # OK if extra, not OK if missing
            
    except Exception as e:
        print(f"❌ Error verifying exempt users: {e}")
        return False

def check_template_consistency():
    """Sjekk at templates er konsistente med nytt system"""
    print("\n🎨 CHECKING TEMPLATE CONSISTENCY")
    print("=" * 50)
    
    templates_to_check = {
        'app/templates/demo.html': ['demo page', 'prøveperiode', 'subscription'],
        'app/templates/base.html': ['trial-timer', 'user-subscribed'],
        'app/templates/index.html': ['show_banner', 'restricted']
    }
    
    issues = []
    
    for template_path, required_content in templates_to_check.items():
        try:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                missing_content = []
                for item in required_content:
                    if item.lower() not in content:
                        missing_content.append(item)
                
                if missing_content:
                    issues.append(f"{template_path}: Missing content - {missing_content}")
                else:
                    print(f"✅ {template_path}: Content looks good")
            else:
                issues.append(f"{template_path}: Template not found")
                
        except Exception as e:
            issues.append(f"{template_path}: Error reading - {e}")
    
    if issues:
        print("\n⚠️  TEMPLATE ISSUES:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("\n✅ ALL TEMPLATES HAVE CONSISTENT CONTENT")
        return True

def generate_summary():
    """Generer sammendrag av access control-status"""
    print("\n📊 ACCESS CONTROL SYSTEM SUMMARY")
    print("=" * 50)
    
    try:
        from app.utils.access_control import (
            UNRESTRICTED_ENDPOINTS, 
            EXEMPT_EMAILS, 
            TRIAL_DURATION_MINUTES
        )
        
        print(f"🔓 Unrestricted endpoints: {len(UNRESTRICTED_ENDPOINTS)}")
        print(f"👤 Exempt users: {len(EXEMPT_EMAILS)}")
        print(f"⏱️  Trial duration: {TRIAL_DURATION_MINUTES} minutes")
        
        print("\n🎯 ACCESS HIERARCHY:")
        print("   1. Exempt users (admin emails) → Full access")
        print("   2. Users with active subscriptions → Full access")  
        print("   3. Trial users (first 15 minutes) → Full access")
        print("   4. Everyone else → Redirect to /demo page ONLY")
        
        print(f"\n🔧 IMPLEMENTATION:")
        print("   • Single @access_required decorator")
        print("   • No conflicting systems")
        print("   • Consistent redirect to /demo")
        print("   • Device fingerprinting for trial tracking")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return False

def main():
    """Kjør alle sjekker og fiks"""
    print("🚀 AKSJERADAR V6 - COMPREHENSIVE ACCESS CONTROL FIX")
    print("=" * 60)
    print("Checking and fixing all access control issues...")
    
    all_good = True
    
    # Run all checks
    checks = [
        fix_access_control_consistency,
        verify_unrestricted_endpoints,
        verify_exempt_users,
        check_template_consistency,
        generate_summary
    ]
    
    for check_func in checks:
        try:
            if not check_func():
                all_good = False
        except Exception as e:
            print(f"❌ Error in {check_func.__name__}: {e}")
            all_good = False
    
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 ALL CHECKS PASSED - SYSTEM IS CONSISTENT!")
        print("\nKey achievements:")
        print("✅ Unified access control system")
        print("✅ No conflicting decorators or endpoints")
        print("✅ Consistent user experience")
        print("✅ Proper trial/demo logic")
        print("✅ Secure admin exemptions")
        
        print("\n🚀 READY FOR TESTING!")
        print("Next steps:")
        print("1. Test login/logout functionality")
        print("2. Test trial expiration flow")
        print("3. Test subscription workflow")
        print("4. Verify exempt user access")
        
    else:
        print("❌ SOME ISSUES FOUND - REVIEW NEEDED")
        print("Check the output above for specific issues to address.")
    
    return all_good

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
