#!/usr/bin/env python3
"""
PC Navigation Test - Verify that main navigation links work correctly
"""
import requests
import time

def test_pc_navigation():
    base_url = 'http://localhost:5001'
    
    print("🖥️  PC NAVIGATION TEST")
    print("=" * 50)
    
    # Test main navigation direct links
    main_nav_links = {
        'Aksjer': '/stocks/',
        'Analyser': '/analysis/', 
        'Portefølje': '/portfolio/',
        'Nyheter': '/news/',
        'Priser': '/pricing/pricing'
    }
    
    print("📋 Testing main navigation direct links...")
    all_passed = True
    
    for name, url in main_nav_links.items():
        try:
            response = requests.get(base_url + url, timeout=5)
            if response.status_code in [200, 302]:
                print(f"✅ {name} ({url}): {response.status_code}")
            else:
                print(f"❌ {name} ({url}): {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name} ({url}): Error - {str(e)}")
            all_passed = False
    
    # Test dropdown sub-links
    print(f"\n📋 Testing dropdown sub-links...")
    dropdown_links = {
        'Oslo Børs': '/stocks/list/oslo',
        'Globale aksjer': '/stocks/list/global',
        'Teknisk analyse': '/analysis/technical',
        'Aksje screener': '/analysis/screener-view',
        'Markedsoversikt': '/analysis/market-overview',
        'Portefølje oversikt': '/portfolio/overview',
        'Aksjenyheter': '/news/category/aksjer'
    }
    
    for name, url in dropdown_links.items():
        try:
            response = requests.get(base_url + url, timeout=5)
            if response.status_code in [200, 302]:
                print(f"✅ {name} ({url}): {response.status_code}")
            else:
                print(f"❌ {name} ({url}): {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name} ({url}): Error - {str(e)}")
            all_passed = False
    
    print(f"\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL NAVIGATION TESTS PASSED!")
        print("✅ Main navigation links work correctly")
        print("✅ Dropdown sub-links work correctly") 
        print("✅ PC users can now navigate properly")
    else:
        print("⚠️  Some navigation tests failed")
    
    return all_passed

if __name__ == "__main__":
    test_pc_navigation()
