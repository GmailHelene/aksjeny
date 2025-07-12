#!/usr/bin/env python3
"""
Sikre at alle exempt brukere har riktige passord og kan logge inn
"""

import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

from app import create_app
from app.extensions import db
from app.models.user import User
from datetime import datetime

def fix_exempt_users():
    """Sikre at exempt brukere har fungerende passord og full tilgang"""
    app = create_app()
    with app.app_context():
        
        # Exempt brukere med standardpassord
        exempt_users = [
            {
                'email': 'helene@luxushair.com',
                'username': 'helene',
                'password': 'aksjeradar2024'
            },
            {
                'email': 'helene721@gmail.com', 
                'username': 'helene721',
                'password': 'aksjeradar2024'
            },
            {
                'email': 'eiriktollan.berntsen@gmail.com',
                'username': 'eiriktollan',
                'password': 'aksjeradar2024'
            }
        ]
        
        print("🔧 Fikser exempt brukere...")
        print("="*50)
        
        for user_data in exempt_users:
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"📝 Oppdaterer eksisterende bruker: {email}")
                
                # Oppdater passord og tilganger
                user.set_password(user_data['password'])
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                user.subscription_start = datetime.utcnow()
                user.subscription_end = None
                user.is_admin = True
                user.trial_used = False  # Gi tilgang til trial også
                
                print(f"   ✅ Passord satt til: {user_data['password']}")
                print(f"   ✅ Lifetime subscription aktivert")
                print(f"   ✅ Admin rettigheter gitt")
                
            else:
                print(f"🆕 Oppretter ny bruker: {email}")
                
                user = User(
                    username=user_data['username'],
                    email=email,
                    has_subscription=True,
                    subscription_type='lifetime',
                    subscription_start=datetime.utcnow(),
                    subscription_end=None,
                    is_admin=True,
                    trial_used=False
                )
                user.set_password(user_data['password'])
                db.session.add(user)
                
                print(f"   ✅ Bruker opprettet med passord: {user_data['password']}")
                print(f"   ✅ Lifetime subscription aktivert")
                print(f"   ✅ Admin rettigheter gitt")
        
        try:
            db.session.commit()
            print("\n✅ ALLE EXEMPT BRUKERE OPPDATERT SUCCESSFULLY!")
            print("\n📋 INNLOGGINGSINFORMASJON:")
            print("-"*40)
            for user_data in exempt_users:
                print(f"Email: {user_data['email']}")
                print(f"Passord: {user_data['password']}")
                print("-"*40)
            
        except Exception as e:
            print(f"\n❌ Feil ved lagring: {str(e)}")
            db.session.rollback()

def test_user_login(email, password):
    """Test at en bruker kan logge inn"""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            print(f"✅ {email} kan logge inn med passord '{password}'")
            print(f"   Has subscription: {user.has_subscription}")
            print(f"   Subscription type: {user.subscription_type}")
            print(f"   Is admin: {user.is_admin}")
            return True
        else:
            print(f"❌ {email} kan IKKE logge inn med passord '{password}'")
            return False

if __name__ == '__main__':
    print("🔐 EXEMPT BRUKER SETUP")
    print("="*50)
    
    # Fiks brukerne først
    fix_exempt_users()
    
    # Test innlogging
    print("\n🧪 TESTER INNLOGGING...")
    print("="*50)
    
    test_users = [
        ('helene@luxushair.com', 'aksjeradar2024'),
        ('helene721@gmail.com', 'aksjeradar2024'),
        ('eiriktollan.berntsen@gmail.com', 'aksjeradar2024')
    ]
    
    all_working = True
    for email, password in test_users:
        if not test_user_login(email, password):
            all_working = False
    
    if all_working:
        print("\n🎉 ALLE EXEMPT BRUKERE KAN LOGGE INN!")
    else:
        print("\n❌ NOEN BRUKERE HAR PROBLEMER MED INNLOGGING")
