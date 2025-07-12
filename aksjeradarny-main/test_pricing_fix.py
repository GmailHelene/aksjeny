#!/usr/bin/env python3
"""
Test script to verify the pricing page displays correct pricing tiers
"""

import requests
import re
import subprocess
import time
import signal
import os
from bs4 import BeautifulSoup

def start_flask_app():
    """Start Flask app in background"""
    print("Starting Flask app...")
    process = subprocess.Popen(
        ['python', 'app.py'],
        cwd='/workspaces/aksjeradarv6',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(3)
    
    return process

def test_pricing_page():
    """Test the pricing page for correct pricing display"""
    try:
        print("\n=== Testing Pricing Page ===")
        
        # Test pricing page
        response = requests.get('http://localhost:5000/pricing')
        print(f"Pricing page status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for pricing elements
            pricing_cards = soup.find_all('div', class_='pricing-card')
            print(f"Found {len(pricing_cards)} pricing cards")
            
            for i, card in enumerate(pricing_cards):
                tier_name = card.find('div', class_='tier-name')
                tier_price = card.find('div', class_='tier-price')
                
                if tier_name and tier_price:
                    name = tier_name.get_text(strip=True)
                    price_text = tier_price.get_text(strip=True)
                    
                    print(f"Card {i+1}: {name} - {price_text}")
                    
                    # Check if the specific prices we expect are shown
                    if 'kr199' in price_text.replace(' ', '') or 'kr 199' in price_text:
                        print("✅ Found kr 199 pricing tier")
                    elif 'kr399' in price_text.replace(' ', '') or 'kr 399' in price_text:
                        print("✅ Found kr 399 pricing tier")
                    elif 'kr0' in price_text.replace(' ', '') or 'kr 0' in price_text:
                        print("✅ Found kr 0 (free) pricing tier")
            
            # Check if we can find the expected pricing values in the raw HTML
            html_content = response.text
            if 'kr</span>199' in html_content or 'kr 199' in html_content:
                print("✅ Raw HTML contains kr 199")
            else:
                print("❌ Raw HTML does not contain kr 199")
                
            if 'kr</span>399' in html_content or 'kr 399' in html_content:
                print("✅ Raw HTML contains kr 399")
            else:
                print("❌ Raw HTML does not contain kr 399")
                
            if 'kr</span>0' in html_content or 'kr 0' in html_content:
                print("✅ Raw HTML contains kr 0")
            else:
                print("❌ Raw HTML does not contain kr 0")
            
            return True
        else:
            print(f"❌ Failed to load pricing page: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing pricing page: {e}")
        return False

def main():
    """Main test function"""
    process = None
    try:
        # Start Flask app
        process = start_flask_app()
        
        # Test pricing page
        success = test_pricing_page()
        
        if success:
            print("\n✅ Pricing test completed")
        else:
            print("\n❌ Pricing test failed")
            
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        # Clean up
        if process:
            print("\nStopping Flask app...")
            process.terminate()
            process.wait()

if __name__ == "__main__":
    main()
