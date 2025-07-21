#!/usr/bin/env python3
"""
Test database fix endpoint
"""

import requests

def test_database_fix():
    """Test the database fix endpoint"""
    print("🔧 Testing database fix endpoint...")
    
    try:
        # Call the fix endpoint
        response = requests.get('http://localhost:5000/admin/fix-database', timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Database fix successful!")
                print("\nResults:")
                for res in result.get('results', []):
                    print(f"  {res}")
                
                print("\nLogin credentials:")
                for info in result.get('login_info', []):
                    print(f"  {info}")
                    
                return True
            else:
                print(f"❌ Database fix failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_login_user(username):
    """Test if specific user can be found"""
    print(f"\n🔍 Testing user: {username}")
    
    try:
        response = requests.get(f'http://localhost:5000/admin/test-login/{username}', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                user = result.get('user', {})
                print(f"✅ User found: {user.get('username')} ({user.get('email')})")
                return True
            else:
                print(f"❌ User not found: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database fix and test...")
    
    # First fix the database
    if test_database_fix():
        print("\n" + "="*50)
        print("Testing user access...")
        
        # Test the created users
        test_login_user('helene721')
        test_login_user('eirik')
        test_login_user('admin')
        
        print("\n🎉 Database fix completed! You can now try logging in at:")
        print("   http://localhost:5000/login")
    else:
        print("\n❌ Database fix failed!")
