#!/usr/bin/env python3
"""
Validation script for the critical fixes made to Aksjeradar V6
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def validate_fixes():
    print("🔧 VALIDATING CRITICAL FIXES")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Check if notifications template exists
    total_tests += 1
    print(f"\n{total_tests}. Testing notifications template...")
    template_path = "/workspaces/aksjeradarv6/app/templates/features/notifications.html"
    if os.path.exists(template_path):
        print("   ✅ notifications.html template exists")
        success_count += 1
    else:
        print("   ❌ notifications.html template missing")
    
    # Test 2: Check for news.index references
    total_tests += 1
    print(f"\n{total_tests}. Checking for remaining news.index references...")
    found_old_refs = False
    key_files = [
        "/workspaces/aksjeradarv6/app/templates/base.html",
        "/workspaces/aksjeradarv6/app/templates/index.html",
        "/workspaces/aksjeradarv6/app/templates/pricing/index.html"
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'news.index' in content:
                    print(f"   ❌ Found news.index reference in {file_path}")
                    found_old_refs = True
    
    if not found_old_refs:
        print("   ✅ No old news.index references found")
        success_count += 1
    
    # Test 3: Test application startup
    total_tests += 1
    print(f"\n{total_tests}. Testing application startup...")
    try:
        from app import create_app
        app = create_app()
        print("   ✅ Application creates successfully")
        success_count += 1
    except Exception as e:
        print(f"   ❌ Application startup failed: {e}")
    
    # Test 4: Test route resolution
    total_tests += 1
    print(f"\n{total_tests}. Testing route resolution...")
    try:
        from app import create_app
        app = create_app()
        with app.app_context():
            from flask import url_for
            test_routes = [
                ('news.news_index', 'News index'),
                ('features.notifications', 'Notifications'),
                ('main.register', 'Register')
            ]
            
            route_success = True
            for route_name, description in test_routes:
                try:
                    url = url_for(route_name)
                    print(f"   ✅ {description}: {url}")
                except Exception as e:
                    print(f"   ❌ {description}: Failed - {e}")
                    route_success = False
            
            if route_success:
                success_count += 1
                
    except Exception as e:
        print(f"   ❌ Route testing failed: {e}")
    
    # Test 5: Check rate limiter configuration
    total_tests += 1
    print(f"\n{total_tests}. Testing rate limiter configuration...")
    try:
        from app.services.rate_limiter import RateLimiter
        limiter = RateLimiter()
        print("   ✅ Rate limiter initializes correctly")
        success_count += 1
    except Exception as e:
        print(f"   ❌ Rate limiter failed: {e}")
    
    # Test 6: Check data service improvements
    total_tests += 1
    print(f"\n{total_tests}. Testing data service fallback...")
    try:
        from app.services.data_service import DataService
        service = DataService()
        fallback_data = service.create_basic_fallback("AAPL")
        if 'price' in fallback_data and fallback_data['price'] > 0:
            print("   ✅ Fallback data generation works")
            success_count += 1
        else:
            print("   ❌ Fallback data generation failed")
    except Exception as e:
        print(f"   ❌ Data service test failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"VALIDATION SUMMARY: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL CRITICAL FIXES VALIDATED SUCCESSFULLY!")
        return True
    else:
        print("⚠️  Some issues remain - check the failed tests above")
        return False

if __name__ == "__main__":
    validate_fixes()
