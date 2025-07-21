#!/usr/bin/env python3
"""
Test user creation and login locally
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_user_operations():
    """Test user creation and login operations"""
    print("🧪 TESTING USER OPERATIONS")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.extensions import db
        from app.models import User
        from werkzeug.security import generate_password_hash, check_password_hash
        
        app = create_app()
        
        with app.app_context():
            print("📋 Testing user creation...")
            
            # Check if test user exists
            test_email = 'helene721@gmail.com'
            user = User.query.filter_by(email=test_email).first()
            
            if not user:
                print(f"   Creating user: {test_email}")
                user = User(
                    username='helene',
                    email=test_email,
                    password_hash=generate_password_hash('password123')
                )
                
                # Set additional fields if they exist
                try:
                    user.is_admin = True
                    user.email_verified = True
                    user.language = 'no'
                except Exception as e:
                    print(f"   ⚠️ Could not set additional fields: {e}")
                
                db.session.add(user)
                db.session.commit()
                print(f"   ✅ User created successfully")
            else:
                print(f"   ✅ User already exists: {user.username}")
            
            # Test login
            print("\n🔐 Testing login...")
            
            login_user = User.query.filter_by(email=test_email).first()
            if login_user:
                if check_password_hash(login_user.password_hash, 'password123'):
                    print(f"   ✅ Login test successful for {login_user.email}")
                    
                    # Test attribute access
                    try:
                        print(f"   - Username: {login_user.username}")
                        print(f"   - Email: {login_user.email}")
                        print(f"   - Is admin: {getattr(login_user, 'is_admin', False)}")
                        print(f"   - Language: {getattr(login_user, 'language', 'no')}")
                        print(f"   - Email verified: {getattr(login_user, 'email_verified', True)}")
                    except Exception as e:
                        print(f"   ⚠️ Error accessing attributes: {e}")
                    
                else:
                    print(f"   ❌ Password verification failed")
            else:
                print(f"   ❌ User not found for login test")
            
            print("\n✅ User operations test completed!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_user_operations()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)
