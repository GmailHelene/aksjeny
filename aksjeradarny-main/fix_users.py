#!/usr/bin/env python3
"""
Quick fix script to create the exempt users
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from app import create_app
    from app.extensions import db
    from app.models.user import User
    from datetime import datetime
    
    print("Starting user creation...")
    
    app = create_app()
    with app.app_context():
        print("App context created successfully")
        
        # Define exempt emails
        exempt_emails = ['helene@luxushair.com','helene@luxushair.com', 'helene721@gmail.com']
        
        for email in exempt_emails:
            try:
                # Delete existing user if exists
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    print(f"Deleting existing user: {email}")
                    db.session.delete(existing_user)
                
                # Create new user
                username = email.split('@')[0]
                user = User(
                    username=username,
                    email=email,
                    has_subscription=True,
                    subscription_type='lifetime',
                    subscription_start=datetime.utcnow(),
                    subscription_end=None,
                    is_admin=True
                )
                user.set_password('aksjeradar2024')
                db.session.add(user)
                print(f"Created user: {email} with password: aksjeradar2024")
                
            except Exception as e:
                print(f"Error creating user {email}: {str(e)}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print("SUCCESS: All exempt users created successfully!")
            print("You can now login with:")
            print("- Email: helene@luxushair.com, Password: aksjeradar2024")
            print("- Email: helene721@gmail.com, Password: aksjeradar2024")
            print("- Email: helene@luxushair.com, Password: aksjeradar2024")

        except Exception as e:
            print(f"Error committing to database: {str(e)}")
            db.session.rollback()
            
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
