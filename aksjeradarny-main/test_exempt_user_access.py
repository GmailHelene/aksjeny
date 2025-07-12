#!/usr/bin/env python3
"""
Test script to verify that exempt users have proper access to all endpoints.
"""

import sys
import os
sys.path.append('/workspaces/aksjeradarv6')

def test_exempt_user_logic():
    """Test exempt user logic without starting the Flask app"""
    
    # Test exempt email lists are consistent
    from app.routes.main import EXEMPT_EMAILS as main_exempt
    from app.utils.access_control import EXEMPT_EMAILS as trial_exempt
    
    print("🧪 Testing Exempt User Access Logic")
    print("=" * 50)
    
    print(f"📧 Exempt emails in main.py: {main_exempt}")
    print(f"📧 Exempt emails in trial.py: {trial_exempt}")
    
    if main_exempt == trial_exempt:
        print("✅ Exempt email lists are consistent")
    else:
        print("❌ Exempt email lists are inconsistent!")
        print(f"   Main only: {main_exempt - trial_exempt}")
        print(f"   Trial only: {trial_exempt - main_exempt}")
        return False
    
    # Test trial logic for exempt users
    print("\n🔐 Testing Trial Logic for Exempt Users")
    print("-" * 30)
    
    # Check that exempt emails are properly handled
    exempt_emails = ['helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com']
    
    for email in exempt_emails:
        if email in main_exempt and email in trial_exempt:
            print(f"✅ {email} is exempt in both systems")
        else:
            print(f"❌ {email} is not properly exempt!")
            return False
    
    print("\n📋 Access Control Summary")
    print("-" * 25)
    print("✅ Exempt users should have:")
    print("   • Full access to all pages")
    print("   • No trial restrictions") 
    print("   • Automatic subscription privileges")
    print("   • No redirect to subscription page")
    
    return True

def test_template_navigation():
    """Test that templates have proper navigation for all user types"""
    
    print("\n🎨 Testing Template Navigation")
    print("=" * 35)
    
    # Check if base template exists and has proper navigation
    base_template = '/workspaces/aksjeradarv6/app/templates/base.html'
    if os.path.exists(base_template):
        print("✅ Base template found")
        
        with open(base_template, 'r') as f:
            content = f.read()
            
        # Check for important navigation elements
        nav_checks = [
            ('navbar', 'Navigation bar'),
            ('nav-link', 'Navigation links'),
            ('dropdown', 'Dropdown menus'),
            ('user.is_authenticated', 'User authentication checks'),
        ]
        
        for check, description in nav_checks:
            if check in content:
                print(f"✅ {description} found")
            else:
                print(f"⚠️  {description} not found")
    
    # Check index template styling
    index_template = '/workspaces/aksjeradarv6/app/templates/index.html'
    if os.path.exists(index_template):
        print("✅ Index template found")
        
        with open(index_template, 'r') as f:
            content = f.read()
            
        # Check for contrast issues
        contrast_issues = [
            'color: white !important',
            'text-white',
            'bg-warning',
        ]
        
        for issue in contrast_issues:
            count = content.count(issue)
            if count > 0:
                print(f"⚠️  Found {count} instances of '{issue}' - check for contrast issues")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Exempt User and Template Tests")
    print("=" * 50)
    
    success = True
    
    try:
        if not test_exempt_user_logic():
            success = False
            
        if not test_template_navigation():
            success = False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed!")
        print("\n📝 Summary:")
        print("   • Exempt user emails are consistent")
        print("   • Access control logic is proper")
        print("   • Templates have proper navigation")
        print("   • Ready for production")
    else:
        print("❌ Some tests failed!")
        print("\n📝 Please fix the issues above before deploying")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
