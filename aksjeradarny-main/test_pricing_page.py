#!/usr/bin/env python3
"""
Test pricing page accessibility and functionality
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_pricing_page():
    app = create_app()
    
    print("🔍 Testing Pricing Page")
    print("=" * 30)
    
    with app.test_client() as client:
        # Test pricing page access
        print("\n📋 Testing: /pricing/")
        response = client.get('/pricing/')
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            
            # Check for key pricing elements
            checks = [
                ("Gratis Demo", "Free tier present"),
                ("Basic", "Basic tier present"),
                ("Pro", "Pro tier present"),
                ("kr 199", "Basic pricing shown"),
                ("kr 399", "Pro pricing shown"),
                ("Oppgrader til", "Upgrade buttons present"),
                ("features-list", "Feature lists present"),
                ("pricing-card", "Pricing cards present")
            ]
            
            print("\n🔍 Content Checks:")
            for check, description in checks:
                if check in content:
                    print(f"✅ {description}")
                else:
                    print(f"❌ {description}")
            
            # Check for common errors
            if "Error" not in content and "Exception" not in content:
                print("\n✅ No errors detected in pricing page")
            else:
                print("\n⚠️  Warning: Potential errors in content")
                
        else:
            print(f"❌ Failed to load pricing page: {response.status_code}")

if __name__ == "__main__":
    test_pricing_page()
