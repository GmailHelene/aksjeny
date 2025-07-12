#!/usr/bin/env python3
"""
Test script to validate UI fixes:
1. Pricing page styling improvements
2. Navigation menu label fix
3. Banner/CTA button text color fixes
"""

import sys
import os
import re
from pathlib import Path

def test_pricing_page_styling():
    """Test that pricing page has improved centering and responsive styling."""
    print("Testing pricing page styling...")
    
    pricing_file = Path("/workspaces/aksjeradarv6/app/templates/pricing/index.html")
    if not pricing_file.exists():
        print("❌ Pricing template file not found")
        return False
    
    content = pricing_file.read_text()
    
    # Check for improved grid layout
    if "justify-items: center;" not in content:
        print("❌ Missing justify-items: center in pricing cards grid")
        return False
    
    # Check for responsive media query
    if "@media (max-width: 768px)" not in content:
        print("❌ Missing responsive media query for mobile")
        return False
    
    # Check for better max-width (1200px instead of 1400px)
    if "max-width: 1200px;" not in content:
        print("❌ Max-width not updated to 1200px")
        return False
    
    # Check that pricing cards have proper width constraints
    if "width: 100%;" not in content:
        print("❌ Pricing cards missing width: 100% property")
        return False
    
    print("✅ Pricing page styling improvements verified")
    return True

def test_navigation_menu_label():
    """Test that nav.market_news i18n attribute is removed."""
    print("Testing navigation menu label fix...")
    
    base_file = Path("/workspaces/aksjeradarv6/app/templates/base.html")
    if not base_file.exists():
        print("❌ Base template file not found")
        return False
    
    content = base_file.read_text()
    
    # Check that data-i18n="nav.market_news" is removed
    if 'data-i18n="nav.market_news"' in content:
        print("❌ data-i18n='nav.market_news' still present in navigation")
        return False
    
    # Check that "Markedsnyheter" text is still there
    if '<span>Markedsnyheter</span>' not in content:
        print("❌ Markedsnyheter text missing from navigation")
        return False
    
    print("✅ Navigation menu label fix verified")
    return True

def test_banner_cta_text_colors():
    """Test that banner and CTA buttons have proper white text on dark backgrounds."""
    print("Testing banner and CTA text colors...")
    
    index_file = Path("/workspaces/aksjeradarv6/app/templates/index.html")
    if not index_file.exists():
        print("❌ Index template file not found")
        return False
    
    content = index_file.read_text()
    
    # Check for white text on warning button
    if 'btn-warning btn-lg me-2" style="color: white; font-weight: bold;"' not in content:
        print("❌ Warning button missing white text style")
        return False
    
    # Check for white text on outline warning button
    if 'btn-outline-warning" style="color: white; border-color: white;"' not in content:
        print("❌ Outline warning button missing white text style")
        return False
    
    # Check for white text on primary button in info banner
    if 'btn-primary btn-sm" style="color: white; font-weight: bold;"' not in content:
        print("❌ Primary button in info banner missing white text style")
        return False
    
    # Check for proper colors on hero section buttons
    if 'btn-light px-4 me-md-2" style="color: #333; font-weight: bold;"' not in content:
        print("❌ Light button missing dark text style")
        return False
    
    if 'btn-outline-light px-4" style="color: white; border-color: white; font-weight: bold;"' not in content:
        print("❌ Outline light button missing white text style")
        return False
    
    # Check for PWA install button color
    if 'color: #333;">\\n                    <i class="bi bi-download"></i> Installer' not in content:
        print("❌ PWA install button missing dark text style")
        return False
    
    print("✅ Banner and CTA text colors verified")
    return True

def main():
    """Run all UI fix tests."""
    print("🔍 Testing UI fixes...")
    print("=" * 50)
    
    tests = [
        test_pricing_page_styling,
        test_navigation_menu_label,
        test_banner_cta_text_colors,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All UI fixes verified successfully!")
        return True
    else:
        print("⚠️  Some UI fixes need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
