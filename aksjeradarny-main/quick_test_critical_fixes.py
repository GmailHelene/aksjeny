#!/usr/bin/env python3
"""
Quick Test of Critical Fixes
Tests the fixes we just implemented
"""

import os
import sys
from pathlib import Path

def test_syntax_fix():
    """Test that access_control.py compiles without errors"""
    print("🔧 Testing access_control.py syntax fix...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'py_compile', 'app/utils/access_control.py'], 
                              capture_output=True, text=True, cwd='/workspaces/aksjeradarny')
        
        if result.returncode == 0:
            print("✅ access_control.py compiles successfully")
            return True
        else:
            print(f"❌ Compilation error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to test compilation: {e}")
        return False

def test_homepage_banner_fix():
    """Test homepage banner button contrast fix"""
    print("🎨 Testing homepage banner button contrast...")
    
    try:
        index_file = Path('/workspaces/aksjeradarny/app/templates/index.html')
        content = index_file.read_text()
        
        # Check for improved contrast styling
        if 'color: #212529 !important; background-color: #f8f9fa !important' in content:
            print("✅ Homepage banner button has improved contrast")
            return True
        else:
            print("❌ Homepage banner button contrast fix not found")
            return False
    except Exception as e:
        print(f"❌ Failed to check homepage banner: {e}")
        return False

def test_pricing_page_containers():
    """Test pricing page container improvements"""
    print("📦 Testing pricing page container improvements...")
    
    try:
        pricing_file = Path('/workspaces/aksjeradarny/app/templates/pricing/index.html')
        content = pricing_file.read_text()
        
        # Check for proper container structure
        if '<div class="container-fluid py-5">' in content and 'div class="container">' in content:
            print("✅ Pricing page has proper container structure")
            return True
        else:
            print("❌ Pricing page container improvements not found")
            return False
    except Exception as e:
        print(f"❌ Failed to check pricing page: {e}")
        return False

def test_rate_limiter_improvements():
    """Test rate limiter improvements"""
    print("⏱️ Testing rate limiter improvements...")
    
    try:
        rate_limiter_file = Path('/workspaces/aksjeradarny/app/services/rate_limiter.py')
        content = rate_limiter_file.read_text()
        
        # Check for improved settings
        if "'requests_per_minute': 5" in content and "'delay_between_calls': 6.0" in content:
            print("✅ Rate limiter has more conservative settings")
            return True
        else:
            print("❌ Rate limiter improvements not found")
            return False
    except Exception as e:
        print(f"❌ Failed to check rate limiter: {e}")
        return False

def test_flash_message_fixes():
    """Test that unwanted flash messages are disabled"""
    print("💬 Testing flash message fixes...")
    
    try:
        init_file = Path('/workspaces/aksjeradarny/app/__init__.py')
        content = init_file.read_text()
        
        # Check for commented out flash messages
        if "# flash('Security token expired. Please try again.', 'warning')" in content:
            print("✅ Security token flash message is disabled")
            return True
        else:
            print("❌ Security token flash message fix not found")
            return False
    except Exception as e:
        print(f"❌ Failed to check flash messages: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 QUICK TEST - CRITICAL FIXES")
    print("=" * 40)
    
    tests = [
        test_syntax_fix,
        test_homepage_banner_fix,
        test_pricing_page_containers,
        test_rate_limiter_improvements,
        test_flash_message_fixes
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 40)
    print("🏁 TEST SUMMARY")
    print("=" * 40)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("🎉 Critical fixes are working correctly.")
    else:
        print(f"⚠️ {passed}/{total} tests passed")
        print("🔧 Some fixes may need attention.")
        
    print("\n🔄 Next Priority Items:")
    print("  1. API endpoint protection and error handling")
    print("  2. Login and forgot password flow testing")  
    print("  3. Menu navigation improvements")
    print("  4. Trial user experience optimization")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
