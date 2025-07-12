#!/usr/bin/env python3
"""
Quick Access Control Validation Script
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_access_control_config():
    """Validate access control configuration"""
    print("🔍 Validating Access Control Configuration...")
    
    try:
        from app.utils.access_control import UNRESTRICTED_ENDPOINTS, access_required
        
        print("✅ Access control module loaded successfully")
        
        # Check unrestricted endpoints
        expected_unrestricted = {
            'main.register', 'main.login', 'main.logout', 
            'main.privacy', 'main.subscription', 'main.demo',
            'main.api_trial_status', 'static'
        }
        
        print(f"📋 Unrestricted endpoints: {UNRESTRICTED_ENDPOINTS}")
        
        # Verify all expected endpoints are present
        missing = expected_unrestricted - UNRESTRICTED_ENDPOINTS
        extra = UNRESTRICTED_ENDPOINTS - expected_unrestricted
        
        if missing:
            print(f"⚠️  Missing unrestricted endpoints: {missing}")
        else:
            print("✅ All expected unrestricted endpoints are configured")
            
        if extra:
            print(f"ℹ️  Extra unrestricted endpoints: {extra}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load access control: {e}")
        return False

def check_demo_page():
    """Check demo page exists and has required content"""
    print("\n📄 Checking Demo Page...")
    
    try:
        demo_path = "/workspaces/aksjeradarv6/app/templates/demo.html"
        if not os.path.exists(demo_path):
            print(f"❌ Demo template not found at {demo_path}")
            return False
            
        with open(demo_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('trial expiration message', any(phrase in content.lower() for phrase in [
                'prøveperiode', 'prøveperioden', 'utløpt'
            ])),
            ('registration link', 'url_for(\'main.register\')' in content),
            ('login link', 'url_for(\'main.login\')' in content),
            ('subscription link', 'url_for(\'main.subscription\')' in content),
            ('demo explanation', 'demo' in content.lower())
        ]
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}: {'FOUND' if passed else 'MISSING'}")
            if not passed:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error checking demo page: {e}")
        return False

def check_route_protection():
    """Check that important routes have access control"""
    print("\n🔒 Checking Route Protection...")
    
    protected_routes = [
        ("/workspaces/aksjeradarv6/app/routes/main.py", ["@access_required"]),
        ("/workspaces/aksjeradarv6/app/routes/stocks.py", ["@access_required"]),
        ("/workspaces/aksjeradarv6/app/routes/portfolio.py", ["@access_required"]),
        ("/workspaces/aksjeradarv6/app/routes/analysis.py", ["@access_required"]),
        ("/workspaces/aksjeradarv6/app/routes/market_intel.py", ["@access_required"])
    ]
    
    all_protected = True
    
    for file_path, required_decorators in protected_routes:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_decorators = []
            for decorator in required_decorators:
                if decorator in content:
                    found_decorators.append(decorator)
            
            if found_decorators:
                print(f"✅ {os.path.basename(file_path)}: Protected with {found_decorators}")
            else:
                print(f"❌ {os.path.basename(file_path)}: Missing access control decorators")
                all_protected = False
                
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")
            all_protected = False
    
    return all_protected

def main():
    """Main validation function"""
    print("🧪 QUICK ACCESS CONTROL VALIDATION")
    print("=" * 50)
    
    tests = [
        ("Access Control Configuration", validate_access_control_config),
        ("Demo Page Content", check_demo_page),
        ("Route Protection", check_route_protection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL VALIDATION CHECKS PASSED!")
        print("Access control configuration looks correct.")
    else:
        print(f"\n⚠️  {total - passed} validation checks failed.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
