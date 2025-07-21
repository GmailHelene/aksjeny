#!/usr/bin/env python3
"""
Create test users for Railway production
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_test_users():
    """Create test users for Railway production"""
    print("👥 CREATING TEST USERS")
    print("=" * 30)
    
    app = create_app()
    
    with app.app_context():
        try:
            # User 1: helen721
            helen_user = User.query.filter(
                (User.username == 'helen721') | (User.email == 'helen721@gmail.com')
            ).first()
            
            if not helen_user:
                print("   Creating user: helen721...")
                helen_user = User(
                    username='helen721',
                    email='helen721@gmail.com',
                    password_hash=generate_password_hash('721'),  # Simple password
                    is_admin=True,  # Make admin
                    email_verified=True,
                    subscription_type='lifetime',  # Give lifetime access
                    has_subscription=True
                )
                db.session.add(helen_user)
                print("   ✅ helen721 created (admin, lifetime)")
            else:
                print(f"   ✅ helen721 already exists ({helen_user.email})")
            
            # User 2: eirik
            eirik_user = User.query.filter(
                (User.username == 'eirik') | (User.email == 'eirik@test.no')
            ).first()
            
            if not eirik_user:
                print("   Creating user: eirik...")
                eirik_user = User(
                    username='eirik',
                    email='eirik@test.no',
                    password_hash=generate_password_hash('test123'),  # Simple password
                    is_admin=False,
                    email_verified=True,
                    subscription_type='monthly',
                    has_subscription=True
                )
                db.session.add(eirik_user)
                print("   ✅ eirik created (monthly subscription)")
            else:
                print(f"   ✅ eirik already exists ({eirik_user.email})")
            
            # User 3: test user
            test_user = User.query.filter(
                (User.username == 'test') | (User.email == 'test@test.com')
            ).first()
            
            if not test_user:
                print("   Creating user: test...")
                test_user = User(
                    username='test',
                    email='test@test.com',
                    password_hash=generate_password_hash('test'),
                    is_admin=False,
                    email_verified=True,
                    subscription_type='free',
                    has_subscription=False
                )
                db.session.add(test_user)
                print("   ✅ test created (free user)")
            else:
                print(f"   ✅ test already exists ({test_user.email})")
            
            # Commit all changes
            db.session.commit()
            
            # Verify users were created
            print("\n📊 User Summary:")
            all_users = User.query.all()
            print(f"   Total users: {len(all_users)}")
            
            for user in all_users:
                admin_status = "👑 Admin" if user.is_admin else "👤 User"
                sub_status = f"{user.subscription_type}" if user.has_subscription else "free"
                print(f"   - {user.username} ({user.email}) - {admin_status} - {sub_status}")
            
            print("\n🎯 Login Instructions:")
            print("   Username: helen721 | Password: 721")
            print("   Username: eirik    | Password: test123") 
            print("   Username: test     | Password: test")
            
        except Exception as e:
            print(f"❌ Error creating users: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False
            
    return True

if __name__ == '__main__':
    success = create_test_users()
    if success:
        print("\n🎉 Test users created successfully!")
    else:
        print("\n💥 Failed to create test users!")
        sys.exit(1)
