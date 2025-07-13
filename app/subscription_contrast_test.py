#!/usr/bin/env python3

"""
Test script to check subscription page contrast issues
"""

import os
import re

def check_subscription_contrast():
    """Check for potential white text on white background issues in subscription page"""
    print("=== SUBSCRIPTION PAGE CONTRAST AUDIT ===\n")
    
    template_path = "/workspaces/aksjeradarny/app/templates/subscription.html"
    
    if not os.path.exists(template_path):
        print(f"❌ File not found: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Checking for potential contrast issues...\n")
    
    issues_found = []
    
    # Check for suspicious patterns
    patterns = [
        (r'text-white[^>]*>.*?<', "text-white class used"),
        (r'color:\s*white', "inline white color"),
        (r'bg-white.*text-white', "white background with white text"),
        (r'background:\s*white.*color:\s*white', "white bg and white text"),
        (r'class="[^"]*text-white[^"]*"[^>]*style="[^"]*background[^"]*white', "text-white with white background"),
    ]
    
    for pattern, description in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            context = match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0)
            issues_found.append((line_num, description, context))
    
    # Check for specific problematic sections
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        # Check for elements that might have styling conflicts
        if 'text-white' in line and ('bg-white' in line or 'background' in line.lower()):
            issues_found.append((i, "Potential white on white", line.strip()))
    
    if issues_found:
        print("⚠️  POTENTIAL CONTRAST ISSUES FOUND:\n")
        for line_num, description, context in issues_found:
            print(f"Line {line_num}: {description}")
            print(f"Context: {context}")
            print("-" * 50)
    else:
        print("✅ No obvious contrast issues found in subscription template")
    
    # Check for cards with missing background styling
    print("\n🎯 Checking card styling...")
    card_sections = re.findall(r'<div class="[^"]*pricing-card[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>', content, re.DOTALL)
    
    for i, card in enumerate(card_sections):
        if 'text-white' in card and not ('bg-' in card or 'background:' in card):
            print(f"⚠️  Card {i+1} has text-white but no background specified")
    
    print("\n🔍 Checking for duplicate content sections...")
    # Look for potential duplicate pricing sections
    yearly_sections = content.count('Pro Årlig')
    if yearly_sections > 1:
        print(f"⚠️  Found {yearly_sections} 'Pro Årlig' sections - potential duplication")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    success = check_subscription_contrast()
    print(f"\n{'✅ PASS' if success else '❌ ISSUES FOUND'}")
