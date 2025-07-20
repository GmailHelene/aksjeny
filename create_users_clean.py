#!/usr/bin/env python3
"""
Create test users: helene and eirik
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_users():
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        try:
            from app import db
            from app.models import User
            from werkzeug.security import generate_password_hash
            
            print("Creating test users...")
            
            # Create helene user if not exists
            helene = User.query.filter_by(username='helene').first()
            if not helene:
                helene = User(
                    username='helene',
                    email='helene721@gmail.com',
                    password_hash=generate_password_hash('password123'),
                    is_admin=True,
                    email_verified=True,
                    language='no'
                )
                db.session.add(helene)
                print("✅ Created helene user")
            else:
                # Update existing user
                helene.email = 'helene721@gmail.com'
                helene.is_admin = True
                helene.email_verified = True
                print("✅ Updated helene user")
            
            # Create eirik user if not exists  
            eirik = User.query.filter_by(username='eirik').first()
            if not eirik:
                eirik = User(
                    username='eirik',
                    email='eirik@aksjeradar.no',
                    password_hash=generate_password_hash('password123'),
                    is_admin=True,
                    email_verified=True,
                    language='no'
                )
                db.session.add(eirik)
                print("✅ Created eirik user")
            else:
                # Update existing user
                eirik.email = 'eirik@aksjeradar.no'
                eirik.is_admin = True
                eirik.email_verified = True
                print("✅ Updated eirik user")
            
            db.session.commit()
            print("✅ Test users created/updated successfully!")
            
            # Test login for both users
            print("\nTesting user authentication...")
            
            # Test helene login
            test_user = User.query.filter(
                (User.username == 'helene721@gmail.com') | 
                (User.email == 'helene721@gmail.com')
            ).first()
            if test_user:
                print(f"✅ helene721@gmail.com found: {test_user.username} ({test_user.email})")
            
            # Test eirik login
            test_user2 = User.query.filter(
                (User.username == 'eirik') | 
                (User.email == 'eirik@aksjeradar.no')
            ).first()
            if test_user2:
                print(f"✅ eirik found: {test_user2.username} ({test_user2.email})")
                
            print("\n🎉 Database is now ready for login!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_test_users()
    sys.exit(0 if success else 1)
