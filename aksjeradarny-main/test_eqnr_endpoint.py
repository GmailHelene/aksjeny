#!/usr/bin/env python3
"""
Final test for EQNR.OL endpoint access
"""
import requests
import time

def test_eqnr_endpoint():
    """Test EQNR.OL endpoint specifically"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing EQNR.OL endpoint access...")
    print("=" * 50)
    
    try:
        # Test the stocks details endpoint for EQNR.OL
        print("\n1. Testing /stocks/details/EQNR.OL...")
        response = requests.get(f"{base_url}/stocks/details/EQNR.OL", timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Success! Status code: {response.status_code}")
            print(f"   ✅ Response length: {len(response.text)} characters")
            
            # Check if key content is present
            if "Equinor" in response.text:
                print("   ✅ Contains 'Equinor' in response")
            if "342.55" in response.text or "NOK" in response.text:
                print("   ✅ Contains price or currency information")
            if "BUY" in response.text or "SELL" in response.text:
                print("   ✅ Contains trading signal")
                
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test market overview
    try:
        print("\n2. Testing /analysis/market-overview...")
        response = requests.get(f"{base_url}/analysis/market-overview", timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Success! Status code: {response.status_code}")
            if "EQNR.OL" in response.text:
                print("   ✅ EQNR.OL found in market overview")
            else:
                print("   ⚠️ EQNR.OL not found in market overview")
        else:
            print(f"   ❌ Failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 EQNR.OL endpoint test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_eqnr_endpoint()
