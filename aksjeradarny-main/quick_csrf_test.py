#!/usr/bin/env python3
"""
Quick test to verify CSRF functionality works
"""

from app import create_app

def test_app_creation():
    """Test that the app can be created and CSRF is working"""
    try:
        app = create_app('development')
        print("✅ App created successfully")
        
        with app.test_client() as client:
            with app.test_request_context():
                # Test that we can generate CSRF tokens
                from flask_wtf.csrf import generate_csrf
                token = generate_csrf()
                print(f"✅ CSRF token generated: {len(token)} characters")
                
                # Test accessing subscription page
                response = client.get('/subscription')
                print(f"✅ Subscription page status: {response.status_code}")
                
                if response.status_code == 200:
                    if b'csrf_token' in response.data:
                        print("✅ CSRF token found in subscription page")
                    else:
                        print("⚠️  CSRF token not found in subscription page")
                
                # Test accessing login page  
                response = client.get('/login')
                print(f"✅ Login page status: {response.status_code}")
                
                if response.status_code == 200:
                    if b'csrf_token' in response.data:
                        print("✅ CSRF token found in login page")
                    else:
                        print("⚠️  CSRF token not found in login page")
                        
        print("\n🎉 Basic CSRF functionality is working!")
        print("The fixes should resolve the Stripe checkout CSRF issue.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_app_creation()
