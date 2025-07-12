#!/usr/bin/env python3
"""
Comprehensive endpoint testing with different user states
Tests trial limits, subscription benefits, and pricing page accessibility
"""

import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

import time
import requests
from flask import session
from datetime import datetime, timedelta

def test_comprehensive_endpoints():
    """Test all endpoints with different user states"""
    print("🔍 COMPREHENSIVE ENDPOINT TESTING")
    print("=" * 50)
    
    from app import create_app
    app = create_app()
    
    # Test scenarios
    scenarios = [
        ("Anonymous user (no trial)", "anonymous"),
        ("Trial user (active)", "trial_active"),
        ("Trial user (expired)", "trial_expired"),
        ("Free user (registered)", "free_user"),
        ("Premium user", "premium_user")
    ]
    
    # Key endpoints to test
    endpoints = [
        ("/", "Home page"),
        ("/pricing", "Pricing page"),
        ("/analysis/", "Analysis index"),
        ("/analysis/technical?ticker=EQNR.OL", "Technical analysis"),
        ("/analysis/ai?ticker=EQNR.OL", "AI analysis"),
        ("/stocks/", "Stocks index"),
        ("/stocks/EQNR.OL", "Stock details"),
        ("/portfolio/", "Portfolio"),
        ("/watchlist/", "Watchlist"),
        ("/market-intel/", "Market intelligence"),
        ("/market-intel/insider-trading", "Insider trading")
    ]
    
    for scenario_name, scenario_type in scenarios:
        print(f"\n🎭 TESTING SCENARIO: {scenario_name}")
        print("-" * 40)
        
        with app.test_client() as client:
            # Set up scenario
            if scenario_type == "trial_active":
                # Simulate active trial
                with client.session_transaction() as sess:
                    sess['trial_start_time'] = datetime.utcnow().isoformat()
            
            elif scenario_type == "trial_expired":
                # Simulate expired trial
                with client.session_transaction() as sess:
                    sess['trial_start_time'] = (datetime.utcnow() - timedelta(minutes=20)).isoformat()
            
            elif scenario_type == "free_user":
                # Simulate logged in free user (would need actual login)
                pass
            
            elif scenario_type == "premium_user":
                # Simulate premium user (would need actual login)
                pass
            
            # Test each endpoint
            for endpoint, description in endpoints:
                try:
                    response = client.get(endpoint, follow_redirects=True)
                    status = response.status_code
                    
                    if status == 200:
                        content = response.get_data(as_text=True)
                        
                        # Check for specific content indicators
                        has_trial_banner = "prøvetid" in content.lower() or "trial" in content.lower()
                        has_upgrade_prompt = "oppgrader" in content.lower() or "upgrade" in content.lower()
                        has_demo_content = "demo" in content.lower()
                        has_pricing_cta = "kjøp nå" in content.lower() or "abonner" in content.lower()
                        
                        # Analysis specific checks
                        if "analysis" in endpoint:
                            has_analysis_limit = "5/dag" in content or "5 daglige" in content
                            print(f"  📊 {description}: ✅ {status} (Analysis limit shown: {'Yes' if has_analysis_limit else 'No'})")
                        elif endpoint == "/pricing":
                            has_pricing_tiers = "gratis" in content.lower() and "basic" in content.lower() and "pro" in content.lower()
                            print(f"  💰 {description}: ✅ {status} (All tiers shown: {'Yes' if has_pricing_tiers else 'No'})")
                        else:
                            indicators = []
                            if has_trial_banner: indicators.append("Trial banner")
                            if has_upgrade_prompt: indicators.append("Upgrade prompt")
                            if has_demo_content: indicators.append("Demo content")
                            if has_pricing_cta: indicators.append("Pricing CTA")
                            
                            indicator_text = ", ".join(indicators) if indicators else "None"
                            print(f"  📄 {description}: ✅ {status} (Indicators: {indicator_text})")
                    
                    elif status in [301, 302, 308]:
                        location = response.headers.get('Location', 'Unknown')
                        print(f"  🔄 {description}: REDIRECT {status} → {location}")
                    
                    else:
                        print(f"  ❌ {description}: ERROR {status}")
                
                except Exception as e:
                    print(f"  💥 {description}: EXCEPTION {str(e)}")
    
    print(f"\n🏁 COMPREHENSIVE TESTING COMPLETED")

if __name__ == "__main__":
    test_comprehensive_endpoints()
