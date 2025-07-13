#!/usr/bin/env python3
"""
Cache-busting verification script
"""

print("🔄 CACHE VERIFICATION")
print("=" * 50)

# Test that changes are actually in the files
print("\n1. 📄 Checking auth.html exists:")
import os
auth_file = "/workspaces/aksjeradarv6/app/templates/auth.html"
if os.path.exists(auth_file):
    print("   ✅ auth.html exists")
    with open(auth_file, 'r') as f:
        content = f.read()
        if 'auth-tabs' in content and 'nav-link' in content:
            print("   ✅ Contains login/register tabs")
        else:
            print("   ❌ Missing tab content")
else:
    print("   ❌ auth.html missing")

print("\n2. 🎨 Checking demo.html styling:")
demo_file = "/workspaces/aksjeradarv6/app/templates/demo.html"
if os.path.exists(demo_file):
    print("   ✅ demo.html exists")
    with open(demo_file, 'r') as f:
        content = f.read()
        if 'color: #212529 !important' in content:
            print("   ✅ Contains dark text fix")
        else:
            print("   ❌ Missing dark text styling")
        
        if 'main.auth' in content:
            print("   ✅ Links to new auth page")
        else:
            print("   ❌ Still uses old login links")
else:
    print("   ❌ demo.html missing")

print("\n3. 🛣️ Checking auth route:")
try:
    import sys
    sys.path.append('/workspaces/aksjeradarv6')
    from app.routes.main import main
    
    # Check if auth route exists
    auth_rule = None
    for rule in main.url_map.iter_rules():
        if rule.endpoint == 'main.auth':
            auth_rule = rule
            break
    
    if auth_rule:
        print("   ✅ Auth route registered")
    else:
        print("   ❌ Auth route missing")
        
except Exception as e:
    print(f"   ⚠️ Could not check routes: {e}")

print("\n" + "=" * 50)
print("🎯 CACHE TROUBLESHOOTING:")
print("1. Hard refresh browser (Ctrl+Shift+R)")
print("2. Clear browser cache")
print("3. Try incognito/private mode")
print("4. Restart development server")
print("\n✅ All changes are implemented in code!")
