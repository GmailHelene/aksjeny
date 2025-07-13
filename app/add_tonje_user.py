#!/usr/bin/env python3
"""
Legger til ny exempt user: tonjekit91@gmail.com
"""

import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

from app import create_app
from app.extensions import db
from app.models.user import User
from datetime import datetime

def add_tonje_user():
    """Legger til tonjekit91@gmail.com som exempt user"""
    app = create_app()
    with app.app_context():
        
        email = 'tonjekit91@gmail.com'
        password = 'aksjeradar2024'
        username = 'tonjekit91'
        
        print(f"🆕 Legger til ny exempt user: {email}")
        print("="*50)
        
        # Sjekk om brukeren allerede eksisterer
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            print(f"📝 Oppdaterer eksisterende bruker: {email}")
            
            # Oppdater passord og tilganger
            existing_user.set_password(password)
            existing_user.has_subscription = True
            existing_user.subscription_type = 'lifetime'
            existing_user.subscription_start = datetime.utcnow()
            existing_user.subscription_end = None
            existing_user.is_admin = True
            existing_user.trial_used = False
            
            print(f"   ✅ Passord satt til: {password}")
            print(f"   ✅ Lifetime subscription aktivert")
            print(f"   ✅ Admin rettigheter gitt")
            
        else:
            print(f"🆕 Oppretter ny bruker: {email}")
            
            new_user = User(
                username=username,
                email=email,
                has_subscription=True,
                subscription_type='lifetime',
                subscription_start=datetime.utcnow(),
                subscription_end=None,
                is_admin=True,
                trial_used=False
            )
            new_user.set_password(password)
            db.session.add(new_user)
            
            print(f"   ✅ Bruker opprettet med passord: {password}")
            print(f"   ✅ Lifetime subscription aktivert")
            print(f"   ✅ Admin rettigheter gitt")
        
        try:
            db.session.commit()
            print("\n✅ TONJE BRUKER LAGT TIL SUCCESSFULLY!")
            print("\n📋 INNLOGGINGSINFORMASJON:")
            print("-"*40)
            print(f"Email: {email}")
            print(f"Passord: {password}")
            print("-"*40)
            print("\n🎯 ALLE EXEMPT USERS:")
            print("- helene@luxushair.com")
            print("- helene721@gmail.com") 
            print("- eiriktollan.berntsen@gmail.com")
            print(f"- {email} (NY)")
            
        except Exception as e:
            print(f"\n❌ Feil ved lagring: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    add_tonje_user()
