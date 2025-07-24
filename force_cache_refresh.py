#!/usr/bin/env python3
"""
Force cache refresh for production deployment
"""
import requests
import time

def force_cache_refresh():
    """Force cache refresh on production"""
    production_url = "https://aksjeradar.trade"
    
    print("🔄 FORCING PRODUCTION CACHE REFRESH")
    print("=" * 50)
    
    # Try to access cache management endpoint
    try:
        # First try accessing homepage to warm up
        print("1. Warming up production server...")
        response = requests.get(f"{production_url}/", 
                              headers={'Cache-Control': 'no-cache'}, 
                              timeout=30)
        print(f"   Homepage status: {response.status_code}")
        
        # Try cache bust endpoint
        print("2. Attempting cache bust...")
        cache_url = f"{production_url}/admin/api/cache/bust"
        response = requests.post(cache_url, 
                               headers={'Cache-Control': 'no-cache'},
                               timeout=30)
        print(f"   Cache bust status: {response.status_code}")
        
        # Access main pages to force refresh
        pages = ["/", "/demo", "/login", "/pricing/pricing"]
        print("3. Refreshing main pages...")
        
        for page in pages:
            try:
                response = requests.get(f"{production_url}{page}",
                                      headers={
                                          'Cache-Control': 'no-cache, no-store, must-revalidate',
                                          'Pragma': 'no-cache',
                                          'Expires': '0'
                                      },
                                      timeout=15)
                print(f"   {page}: {response.status_code}")
                time.sleep(1)  # Small delay between requests
            except Exception as e:
                print(f"   {page}: ERROR - {e}")
        
        print("\n✅ Cache refresh completed!")
        print("💡 Check footer copyright year now - should show 2025")
        
    except Exception as e:
        print(f"❌ Cache refresh failed: {e}")
        print("💡 Try manual browser refresh with Ctrl+F5")

if __name__ == '__main__':
    force_cache_refresh()
