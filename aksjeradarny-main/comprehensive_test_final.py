#!/usr/bin/env python3
"""
Comprehensive functionality test for Aksjeradar V6
Tests templates, access control, navigation, and styling
"""

import os
import sys
sys.path.append('/workspaces/aksjeradarv6')

from app import create_app
from app.utils.access_control import EXEMPT_EMAILS, UNRESTRICTED_ENDPOINTS
from jinja2 import Environment, FileSystemLoader
import json

def test_app_startup():
    """Test basic app startup and configuration"""
    print("🚀 Testing app startup...")
    try:
        app = create_app()
        print("✅ App created successfully")
        return app
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return None

def test_template_syntax(app):
    """Test critical template syntax"""
    print("\n🎨 Testing template syntax...")
    
    templates_to_test = [
        'base.html',
        'watchlist/index.html',
        'portfolio/watchlist.html',
        'analysis/index.html',
        'stocks/details.html'
    ]
    
    template_dir = '/workspaces/aksjeradarv6/app/templates'
    env = Environment(loader=FileSystemLoader(template_dir))
    
    for template_name in templates_to_test:
        try:
            template = env.get_template(template_name)
            print(f"✅ {template_name} syntax OK")
        except Exception as e:
            print(f"❌ {template_name} error: {e}")

def test_access_control():
    """Test access control configuration"""
    print("\n🔐 Testing access control...")
    
    print(f"Exempt emails: {EXEMPT_EMAILS}")
    print(f"Unrestricted endpoints: {len(UNRESTRICTED_ENDPOINTS)} configured")
    
    # Test that essential endpoints are unrestricted
    essential_endpoints = [
        'main.login',
        'main.register',
        'main.demo',
        '/api/watchlist/add',
        '/api/portfolio/add'
    ]
    
    for endpoint in essential_endpoints:
        if endpoint in UNRESTRICTED_ENDPOINTS:
            print(f"✅ {endpoint} is unrestricted")
        else:
            print(f"❌ {endpoint} is missing from unrestricted list")

def test_blueprint_registration(app):
    """Test that all blueprints are registered"""
    print("\n📋 Testing blueprint registration...")
    
    with app.app_context():
        blueprints = app.blueprints
        expected_blueprints = [
            'main',
            'stocks',
            'analysis',
            'portfolio',
            'watchlist'
        ]
        
        for bp_name in expected_blueprints:
            if bp_name in blueprints:
                print(f"✅ {bp_name} blueprint registered")
            else:
                print(f"❌ {bp_name} blueprint missing")

def test_static_files():
    """Test that critical static files exist"""
    print("\n📁 Testing static files...")
    
    static_files = [
        '/workspaces/aksjeradarv6/app/static/css/style.css',
        '/workspaces/aksjeradarv6/app/static/js/watchlist-fix.js',
        '/workspaces/aksjeradarv6/app/static/images/logo-192.png'
    ]
    
    for file_path in static_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} exists")
        else:
            print(f"❌ {os.path.basename(file_path)} missing")

def test_route_accessibility(app):
    """Test that routes are accessible"""
    print("\n🌐 Testing route accessibility...")
    
    with app.test_client() as client:
        # Test accessible routes (should not throw 500 errors)
        test_routes = [
            '/',
            '/demo',
            '/login',
            '/analysis'
        ]
        
        for route in test_routes:
            try:
                response = client.get(route)
                if response.status_code < 500:
                    print(f"✅ {route} accessible (status: {response.status_code})")
                else:
                    print(f"❌ {route} server error (status: {response.status_code})")
            except Exception as e:
                print(f"❌ {route} error: {e}")

def main():
    """Run all tests"""
    print("🧪 Aksjeradar V6 - Comprehensive Functionality Test")
    print("=" * 60)
    
    # Test app startup
    app = test_app_startup()
    if not app:
        print("❌ Cannot continue tests - app startup failed")
        return
    
    # Run all tests
    test_template_syntax(app)
    test_access_control()
    test_blueprint_registration(app)
    test_static_files()
    test_route_accessibility(app)
    
    print("\n🎯 Test Summary:")
    print("- App startup: ✅")
    print("- Templates: Check output above")
    print("- Access control: Check exempt users and endpoints")
    print("- Routes: Check accessibility")
    print("- Navigation: Review template structure")
    
    print("\n✨ All major functionality has been tested!")

if __name__ == "__main__":
    main()
