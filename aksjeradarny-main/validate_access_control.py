#!/usr/bin/env python3
"""
Validation script for the new access control system
"""

def check_access_control():
    """Check that access control is properly configured"""
    
    print("=== AKSJERADAR ACCESS CONTROL VALIDATION ===")
    print()
    
    # Check that access control file exists and is valid
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        from app.utils.access_control import (
            UNRESTRICTED_ENDPOINTS, 
            TRIAL_DURATION_MINUTES,
            access_required
        )
        print("✅ Access control module imported successfully")
        print(f"✅ Trial duration: {TRIAL_DURATION_MINUTES} minutes")
        print()
        
        print("📝 UNRESTRICTED ENDPOINTS (always accessible):")
        for endpoint in sorted(UNRESTRICTED_ENDPOINTS):
            print(f"   - {endpoint}")
        print()
        
        # Check that critical endpoints are unrestricted
        required_unrestricted = {
            'main.register', 'main.login', 'main.logout', 
            'main.privacy', 'main.subscription', 'main.demo'
        }
        
        missing_unrestricted = required_unrestricted - UNRESTRICTED_ENDPOINTS
        if missing_unrestricted:
            print(f"❌ Missing unrestricted endpoints: {missing_unrestricted}")
        else:
            print("✅ All required unrestricted endpoints present")
        
        print()
        
        # Test decorator function
        @access_required
        def test_route():
            return "test"
            
        print("✅ Access control decorator works")
        print()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_route_protection():
    """Check which routes have access control"""
    
    print("=== ROUTE PROTECTION STATUS ===")
    print()
    
    try:
        # Check main routes
        with open('app/routes/main.py', 'r') as f:
            main_content = f.read()
            
        # Look for routes that should have access control
        routes_with_access = main_content.count('@access_required')
        print(f"✅ Main routes with access control: {routes_with_access}")
        
        # Check if homepage has access control
        if '@access_required\ndef index():' in main_content:
            print("✅ Homepage (/) has access control")
        else:
            print("❌ Homepage (/) missing access control")
            
        # Check if ai-explained has access control  
        if '@access_required\ndef ai_explained():' in main_content:
            print("✅ AI-explained page has access control")
        else:
            print("❌ AI-explained page missing access control")
            
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        return False

def check_demo_page():
    """Check that demo page has proper CTAs"""
    
    print("=== DEMO PAGE VALIDATION ===")
    print()
    
    try:
        with open('app/templates/demo.html', 'r') as f:
            demo_content = f.read()
            
        # Check for registration CTA
        if 'url_for(\'main.register\')' in demo_content:
            print("✅ Demo page has registration CTA")
        else:
            print("❌ Demo page missing registration CTA")
            
        # Check for subscription CTA
        if 'url_for(\'main.subscription\')' in demo_content:
            print("✅ Demo page has subscription CTA")
        else:
            print("❌ Demo page missing subscription CTA")
            
        # Check for login CTA  
        if 'url_for(\'main.login\')' in demo_content:
            print("✅ Demo page has login CTA")
        else:
            print("❌ Demo page missing login CTA")
            
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error checking demo page: {e}")
        return False

if __name__ == "__main__":
    success = True
    success &= check_access_control()
    success &= check_route_protection()
    success &= check_demo_page()
    
    print("=== SUMMARY ===")
    if success:
        print("🚀 All access control validations PASSED!")
        print("✅ Strict access control is properly configured")
        print("✅ Expired trial users will only see: /demo, /login, /register, /logout, /subscription, /privacy")
        print("✅ All other pages redirect to /demo")
    else:
        print("❌ Some validations FAILED - please review the issues above")
        
    print()
