#!/usr/bin/env python3
"""
Test script to verify access control fixes
"""

import requests
from datetime import datetime, timedelta
import json

def test_endpoint_access(base_url, endpoint, should_require_auth=True):
    """Test if endpoint properly requires authentication"""
    print(f"\nTesting {endpoint}:")
    
    # Test without authentication
    response = requests.get(f"{base_url}{endpoint}", allow_redirects=False)
    print(f"  No auth: Status {response.status_code}")
    
    if should_require_auth:
        # Should redirect to login
        assert response.status_code in [301, 302, 303, 307, 308], f"Expected redirect, got {response.status_code}"
        location = response.headers.get('Location', '')
        assert '/login' in location or response.status_code == 308, f"Expected login redirect, got {location}"
        print("  ✓ Correctly requires authentication")
    else:
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("  ✓ Correctly allows anonymous access")
    
    # Test with expired trial cookie
    expired_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
    cookies = {'trial_start': expired_time}
    response = requests.get(f"{base_url}{endpoint}", cookies=cookies, allow_redirects=True)
    print(f"  Expired trial: Final URL {response.url}")
    
    if should_require_auth:
        assert '/login' in response.url or '/pricing' in response.url, "Expected redirect to login or pricing"
        print("  ✓ Correctly blocks expired trial")

def main():
    base_url = "http://localhost:5000"
    
    print("Testing Access Control Fixes")
    print("=" * 50)
    
    # Protected endpoints that should require auth
    protected_endpoints = [
        '/analysis',
        '/portfolio',
        '/features/analyst-recommendations',
        '/features/social-sentiment',
        '/features/ai-predictions',
        '/market-intel',
        '/profile',
        '/notifications'
    ]
    
    success_count = 0
    total_count = len(protected_endpoints)
    
    for endpoint in protected_endpoints:
        try:
            test_endpoint_access(base_url, endpoint, should_require_auth=True)
            success_count += 1
            print(f"  ✅ PASSED")
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {success_count}/{total_count} endpoints properly secured")
    
    if success_count == total_count:
        print("🎉 All access control tests passed!")
        return 0
    else:
        print("⚠️  Some endpoints still have issues")
        return 1

if __name__ == "__main__":
    exit(main())
