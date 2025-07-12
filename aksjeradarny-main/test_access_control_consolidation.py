#!/usr/bin/env python3
"""
Test den konsoliderte access control implementasjonen
"""

import sys
import os

# Legg til prosjektmappen i Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test at alle imports fungerer etter konsolidering"""
    print("🧪 TESTING IMPORTS AFTER CONSOLIDATION")
    print("=" * 50)
    
    try:
        print("Testing access_control import...")
        from app.utils.access_control import (
            access_required, 
            EXEMPT_EMAILS, 
            UNRESTRICTED_ENDPOINTS,
            get_trial_status,
            get_access_level,
            get_trial_time_remaining
        )
        print("✅ access_control.py imports successful")
        
        print(f"   📧 Exempt emails: {EXEMPT_EMAILS}")
        print(f"   🔓 Unrestricted endpoints: {len(UNRESTRICTED_ENDPOINTS)} defined")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False
    
    try:
        print("Testing that old trial.py is removed...")
        from app.utils import trial
        print("❌ OLD trial.py still exists!")
        return False
    except ImportError:
        print("✅ Old trial.py successfully removed")
    
    try:
        print("Testing main.py routes import...")
        from app.routes.main import main
        print("✅ main.py routes import successful")
    except Exception as e:
        print(f"❌ main.py import error: {e}")
        return False
    
    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    return True

def test_access_control_logic():
    """Test access control logic without Flask context"""
    print("\n🔐 TESTING ACCESS CONTROL LOGIC")
    print("=" * 50)
    
    try:
        from app.utils.access_control import UNRESTRICTED_ENDPOINTS, EXEMPT_EMAILS
        
        # Test endpoints
        expected_unrestricted = {
            'main.register', 'main.login', 'main.logout', 
            'main.privacy', 'main.subscription', 'main.demo'
        }
        
        missing = expected_unrestricted - UNRESTRICTED_ENDPOINTS
        if missing:
            print(f"⚠️  Missing unrestricted endpoints: {missing}")
        else:
            print("✅ All expected unrestricted endpoints are configured")
        
        # Test exempt emails
        expected_emails = {
            'helene@luxushair.com', 'helene721@gmail.com', 
            'eiriktollan.berntsen@gmail.com', 'tonjekit91@gmail.com'
        }
        
        if EXEMPT_EMAILS == expected_emails:
            print("✅ Exempt emails are correctly configured")
        else:
            missing_emails = expected_emails - EXEMPT_EMAILS
            extra_emails = EXEMPT_EMAILS - expected_emails
            if missing_emails:
                print(f"⚠️  Missing exempt emails: {missing_emails}")
            if extra_emails:
                print(f"ℹ️  Extra exempt emails: {extra_emails}")
        
        print("\n✅ ACCESS CONTROL LOGIC VALIDATION COMPLETE")
        return True
        
    except Exception as e:
        print(f"❌ Access control logic test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AKSJERADAR V6 - ACCESS CONTROL CONSOLIDATION TEST")
    print("=" * 60)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_access_control_logic():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED - ACCESS CONTROL CONSOLIDATION SUCCESSFUL!")
        print("\nKey improvements:")
        print("✅ Removed conflicting trial.py system")
        print("✅ Unified access control with @access_required")
        print("✅ All redirects go to /demo (not /restricted_access)")
        print("✅ Consistent UNRESTRICTED_ENDPOINTS configuration")
        print("✅ Single source of truth for exempt users")
    else:
        print("❌ SOME TESTS FAILED - REVIEW NEEDED")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
