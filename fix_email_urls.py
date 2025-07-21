import os
import requests

def find_running_server():
    """Find what port the server is actually running on"""
    ports = [5000, 8000, 3000, 4000]
    
    for port in ports:
        try:
            response = requests.get(f'http://localhost:{port}', timeout=2)
            print(f"✅ Found server running on port {port}")
            return port
        except:
            continue
    
    print("❌ No server found on common ports")
    return None

def update_app_for_correct_urls():
    """Update app.py to use the correct base URL"""
    port = find_running_server()
    
    if port:
        print(f"🔧 Server found on port {port}")
        print(f"🌐 Your app should be accessible at: http://localhost:{port}")
        return f"http://localhost:{port}"
    else:
        print("❌ No running server found")
        return None

if __name__ == "__main__":
    print("🔍 Looking for running server...")
    base_url = update_app_for_correct_urls()
    
    if base_url:
        print(f"\n🔗 Test these URLs:")
        print(f"   Home: {base_url}")
        print(f"   Forgot Password: {base_url}/forgot-password")
        print(f"   Reset Password: {base_url}/reset-password?token=YOUR_TOKEN")
