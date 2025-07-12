#!/usr/bin/env python3
"""
Comprehensive audit of remaining trial/banner issues for Aksjeradar app
Tests for premium user experience, trial popup visibility, and navigation layout
"""

import subprocess
import json
import os
import re
from datetime import datetime

def run_flask_command(command):
    """Run a Flask shell command and return output"""
    try:
        result = subprocess.run(
            ['python', '-c', f'''
import os
os.environ["FLASK_APP"] = "app"
from app import create_app
from app.models.user import User
from app.extensions import db
from flask_login import current_user

app = create_app()
with app.app_context():
    {command}
'''],
            cwd='/workspaces/aksjeradarv6',
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def test_premium_user_banners():
    """Test that premium users don't see trial banners"""
    print("\n=== TESTING: Premium User Trial Banner Visibility ===")
    
    # Create test premium user
    result = run_flask_command('''
# Create premium user with active subscription
user = User.query.filter_by(email='premium_test@test.com').first()
if not user:
    user = User(
        username='premium_test',
        email='premium_test@test.com',
        is_active=True
    )
    user.set_password('testpass')
    db.session.add(user)

# Set premium subscription
from datetime import datetime, timedelta
user.subscription_type = 'premium'
user.subscription_start_date = datetime.utcnow()
user.subscription_end_date = datetime.utcnow() + timedelta(days=30)
user.is_subscribed = True
db.session.commit()

print(f"Premium user created: {user.email}")
print(f"Has subscription: {user.has_active_subscription()}")
print(f"Subscription type: {user.subscription_type}")
''')
    print(f"Premium user setup: {result}")
    
    # Test access control for premium user
    result = run_flask_command('''
from app.utils.access_control import get_access_level, get_trial_status
from unittest.mock import patch

# Mock current_user as premium user
user = User.query.filter_by(email='premium_test@test.com').first()
with patch('app.utils.access_control.current_user', user):
    access_level = get_access_level()
    trial_status = get_trial_status()
    print(f"Premium user access level: {access_level}")
    print(f"Premium user trial status: {trial_status}")
''')
    print(f"Premium user access: {result}")

def test_trial_timer_navigation():
    """Test trial timer visibility in navigation"""
    print("\n=== TESTING: Trial Timer in Navigation ===")
    
    # Check if trial timer is in navigation for trial users
    base_html = '/workspaces/aksjeradarv6/app/templates/base.html'
    with open(base_html, 'r') as f:
        content = f.read()
        
    if 'trial-timer.js' in content:
        print("✓ Trial timer JS is loaded in base template")
    else:
        print("✗ Trial timer JS not found in base template")
        
    # Check trial-timer.js implementation
    timer_js = '/workspaces/aksjeradarv6/app/static/js/trial-timer.js'
    with open(timer_js, 'r') as f:
        js_content = f.read()
        
    issues = []
    
    # Check if timer respects premium users
    if 'user-subscribed' in js_content and 'return' in js_content:
        print("✓ Timer checks for premium users and returns early")
    else:
        issues.append("Timer should return early for premium users")
        
    # Check if timer respects demo page
    if '/demo' in js_content and 'return' in js_content:
        print("✓ Timer checks for demo page and returns early")  
    else:
        issues.append("Timer should return early on demo page")
        
    # Check if timer shows popup on expiration
    if 'showTrialExpiredPopup' in js_content:
        print("✓ Timer has popup functionality for expiration")
    else:
        issues.append("Timer should show popup when trial expires")
        
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Timer implementation looks correct")

def test_banner_logic():
    """Test banner logic in templates"""
    print("\n=== TESTING: Banner Logic in Templates ===")
    
    # Check index.html banner logic
    index_html = '/workspaces/aksjeradarv6/app/templates/index.html'
    with open(index_html, 'r') as f:
        content = f.read()
        
    issues = []
    
    # Check if banners are properly gated
    if 'show_banner' in content:
        print("✓ Index template uses show_banner variable")
        
        # Check if banner is properly gated for premium users
        if 'current_user.has_active_subscription()' in content:
            print("✓ Banner checks for active subscription")
        else:
            issues.append("Banner should check for active subscription")
    else:
        issues.append("Index template should use show_banner variable")
    
    # Check main.py banner logic
    main_py = '/workspaces/aksjeradarv6/app/routes/main.py'
    with open(main_py, 'r') as f:
        py_content = f.read()
        
    if "access_level == 'subscriber'" in py_content and 'show_banner = False' in py_content:
        print("✓ Main.py sets show_banner=False for subscribers")
    else:
        issues.append("Main.py should set show_banner=False for subscribers")
        
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Banner logic looks correct")

def test_navigation_layout():
    """Test navigation responsive layout"""
    print("\n=== TESTING: Navigation Layout Issues ===")
    
    style_css = '/workspaces/aksjeradarv6/app/static/css/style.css'
    with open(style_css, 'r') as f:
        css_content = f.read()
        
    issues = []
    
    # Check for responsive display classes
    if 'd-none d-md-block' in css_content or 'd-none d-lg-block' in css_content:
        print("✓ CSS contains responsive display classes")
    else:
        issues.append("CSS should contain responsive display classes")
        
    # Check for overflow fixes
    if 'overflow' in css_content and 'navbar' in css_content:
        print("✓ CSS contains overflow fixes")
    else:
        issues.append("CSS should fix navigation overflow issues")
        
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Navigation layout looks correct")

def test_user_actions():
    """Test user action endpoints"""
    print("\n=== TESTING: User Action Endpoints ===")
    
    access_control = '/workspaces/aksjeradarv6/app/utils/access_control.py'
    with open(access_control, 'r') as f:
        content = f.read()
        
    required_endpoints = [
        '/api/watchlist/add',
        '/api/portfolio/add',
        '/api/favorites/add'
    ]
    
    issues = []
    for endpoint in required_endpoints:
        if endpoint in content:
            print(f"✓ {endpoint} found in access control")
        else:
            issues.append(f"{endpoint} should be in UNRESTRICTED_ENDPOINTS")
            
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ User action endpoints look correct")

def test_language_switching():
    """Test i18n language switching"""
    print("\n=== TESTING: Language Switching (i18n) ===")
    
    base_html = '/workspaces/aksjeradarv6/app/templates/base.html'
    with open(base_html, 'r') as f:
        content = f.read()
        
    issues = []
    
    if 'i18n.js' in content:
        print("✓ i18n.js is loaded in base template")
    else:
        issues.append("i18n.js should be loaded in base template")
        
    if 'data-i18n' in content:
        print("✓ Base template contains i18n attributes")
    else:
        issues.append("Templates should contain data-i18n attributes")
        
    # Check if i18n.js exists
    i18n_js = '/workspaces/aksjeradarv6/app/static/js/i18n.js'
    if os.path.exists(i18n_js):
        print("✓ i18n.js file exists")
        with open(i18n_js, 'r') as f:
            js_content = f.read()
            if 'setLanguage' in js_content:
                print("✓ i18n.js contains setLanguage function")
            else:
                issues.append("i18n.js should contain setLanguage function")
    else:
        issues.append("i18n.js file should exist")
        
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Language switching looks correct")

def generate_remaining_issues_summary():
    """Generate summary of remaining issues to fix"""
    print("\n" + "="*60)
    print("REMAINING ISSUES TO FIX:")
    print("="*60)
    
    remaining_issues = [
        "1. CRITICAL: Remove trial banners/timer from navigation for premium users",
        "2. CRITICAL: Move timer from navigation to popup-only (remove nav timer completely)",
        "3. HIGH: Move search field to footer and stock dropdown",
        "4. HIGH: Move language selector and prices to footer",
        "5. MEDIUM: Ensure trial popup shows on ALL pages when trial expires",
        "6. MEDIUM: Fix language switching to translate all content",
        "7. MEDIUM: Add more news/intel sources",
        "8. LOW: Test all user flows and notification toasts",
        "9. LOW: Verify Stripe subscription flow"
    ]
    
    for issue in remaining_issues:
        print(f"  {issue}")
        
    print("\nNext steps:")
    print("1. Fix trial timer to be popup-only (remove from navigation)")
    print("2. Remove all trial banners for premium users")  
    print("3. Reorganize navigation layout (move elements to footer)")
    print("4. Test all user flows")

def main():
    """Run comprehensive audit"""
    print("AKSJERADAR APP - REMAINING ISSUES AUDIT")
    print("=" * 50)
    print(f"Audit started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_premium_user_banners()
        test_trial_timer_navigation()  
        test_banner_logic()
        test_navigation_layout()
        test_user_actions()
        test_language_switching()
        generate_remaining_issues_summary()
        
    except Exception as e:
        print(f"\nERROR during audit: {e}")
        
    print(f"\nAudit completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
