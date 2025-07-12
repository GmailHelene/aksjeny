#!/usr/bin/env python3
"""
Test script for UI improvements:
- Dark mode toggle removal
- Expandable search icon
- Removed "Hjem" text 
- Language toggle addition
"""

import re
from app import create_app
from flask import render_template_string

def test_ui_improvements():
    """Test that the UI improvements have been implemented correctly."""
    
    app = create_app()
    
    with app.app_context():
        # Read the base template
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Test 1: Dark mode toggle should be removed
        dark_mode_patterns = [
            r'onclick="toggleDarkMode\(\)"',
            r'id="dark-mode-icon"',
            r'id="guest-dark-mode-icon"',
            r'Mørk modus',
            r'toggleDarkMode'
        ]
        
        print("🔍 Testing dark mode toggle removal...")
        for pattern in dark_mode_patterns:
            if re.search(pattern, template_content):
                print(f"❌ Found dark mode reference: {pattern}")
                return False
        print("✅ Dark mode toggle removed successfully")
        
        # Test 2: Check for expandable search implementation
        print("\n🔍 Testing expandable search...")
        search_patterns = [
            r'search-container',
            r'search-toggle',
            r'search-form',
            r'initializeSearchToggle'
        ]
        
        for pattern in search_patterns:
            if not re.search(pattern, template_content):
                print(f"❌ Missing search pattern: {pattern}")
                return False
        print("✅ Expandable search implemented successfully")
        
        # Test 3: Check that "Hjem" text is removed but house icon remains
        print("\n🔍 Testing home link changes...")
        if 'bi-house-door' in template_content and '> Hjem</a>' not in template_content:
            print("✅ 'Hjem' text removed, house icon kept")
        else:
            print("❌ Home link not updated correctly")
            return False
        
        # Test 4: Check for language toggle
        print("\n🔍 Testing language toggle...")
        language_patterns = [
            r'languageDropdown',
            r'setLanguage',
            r'current-language',
            r'Norsk',
            r'English'
        ]
        
        for pattern in language_patterns:
            if not re.search(pattern, template_content):
                print(f"❌ Missing language pattern: {pattern}")
                return False
        print("✅ Language toggle implemented successfully")
        
        # Test 5: Check that the navigation structure is still intact
        print("\n🔍 Testing navigation structure...")
        nav_patterns = [
            r'navbar-nav',
            r'Aksjer',
            r'Analyse',
            r'Portefølje',
            r'dropdown-menu'
        ]
        
        for pattern in nav_patterns:
            if not re.search(pattern, template_content):
                print(f"❌ Missing navigation pattern: {pattern}")
                return False
        print("✅ Navigation structure intact")
        
        print("\n🎉 All UI improvements implemented successfully!")
        return True

if __name__ == "__main__":
    test_ui_improvements()
