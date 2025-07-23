#!/usr/bin/env python3
"""
Critical URL Building Fixes Validation Script
==============================================

This script validates that the critical URL building fixes have been applied correctly.
It checks for the most common template rendering errors that were causing 500/404 errors.

Fixes applied:
1. Fixed news.news_index (was news_bp.index)
2. Fixed all news blueprint references (news_bp.* -> news.*)
3. Fixed portfolio.index (was portfolio.portfolio_index)
4. Fixed portfolio_analytics.analytics_dashboard (was .dashboard)

"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_template_fixes():
    """Check that critical template fixes have been applied"""
    fixes_verified = []
    issues_found = []
    
    # Check base.html for correct news blueprint references
    base_html_path = os.path.join(project_root, 'app', 'templates', 'base.html')
    if os.path.exists(base_html_path):
        with open(base_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for old incorrect references
        if 'news_bp.index' in content:
            issues_found.append("❌ Found old reference: news_bp.index in base.html")
        else:
            fixes_verified.append("✅ news_bp.index fixed in base.html")
            
        if 'news.news_index' in content:
            fixes_verified.append("✅ news.news_index correctly used in base.html")
        else:
            issues_found.append("❌ Missing news.news_index in base.html")
            
        # Check for other news_bp references
        if 'news_bp.category' in content:
            issues_found.append("❌ Found old reference: news_bp.category in base.html")
        else:
            fixes_verified.append("✅ news_bp.category fixed in base.html")
            
        # Check portfolio analytics fix
        if 'portfolio_analytics.dashboard' in content:
            issues_found.append("❌ Found old reference: portfolio_analytics.dashboard in base.html")
        else:
            fixes_verified.append("✅ portfolio_analytics.dashboard fixed in base.html")
            
        if 'portfolio_analytics.analytics_dashboard' in content:
            fixes_verified.append("✅ portfolio_analytics.analytics_dashboard correctly used")
    else:
        issues_found.append("❌ base.html template not found")
    
    # Check market_intel template
    market_intel_path = os.path.join(project_root, 'app', 'templates', 'market_intel', 'insider_trading.html')
    if os.path.exists(market_intel_path):
        with open(market_intel_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'portfolio.portfolio_index' in content:
            issues_found.append("❌ Found old reference: portfolio.portfolio_index in market_intel/insider_trading.html")
        else:
            fixes_verified.append("✅ portfolio.portfolio_index fixed in market_intel/insider_trading.html")
            
        if 'portfolio.index' in content:
            fixes_verified.append("✅ portfolio.index correctly used in market_intel/insider_trading.html")
    else:
        issues_found.append("❌ market_intel/insider_trading.html template not found")
    
    return fixes_verified, issues_found

def print_results(fixes_verified, issues_found):
    """Print the validation results"""
    print("🔍 CRITICAL URL BUILDING FIXES VALIDATION")
    print("=" * 50)
    
    if fixes_verified:
        print("\n✅ FIXES VERIFIED:")
        for fix in fixes_verified:
            print(f"  {fix}")
    
    if issues_found:
        print("\n❌ ISSUES STILL PRESENT:")
        for issue in issues_found:
            print(f"  {issue}")
    else:
        print("\n🎉 ALL CRITICAL FIXES VERIFIED - NO ISSUES FOUND!")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Fixes verified: {len(fixes_verified)}")
    print(f"  Issues found: {len(issues_found)}")
    
    if issues_found:
        print("\n⚠️  RECOMMENDATION: Fix the remaining issues before deployment")
        return False
    else:
        print("\n✅ READY FOR DEPLOYMENT")
        return True

def main():
    """Main validation function"""
    print("Starting validation of critical URL building fixes...\n")
    
    fixes_verified, issues_found = check_template_fixes()
    success = print_results(fixes_verified, issues_found)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
