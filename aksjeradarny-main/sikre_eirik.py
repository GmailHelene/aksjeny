#!/usr/bin/env python3
"""
Spesialsjekk for Helene og sikring av hans tilganger
"""
import sys
import os
sys.path.insert(0, '/workspaces/aksjeradarv6')

from app import create_app
from app.models.user import User
from app.extensions import db
from datetime import datetime

def sikre_Helene_tilgang():
    app = create_app()
    with app.app_context():
        email = "helene@luxushair.com"
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"🔍 Sjekker Helene: {email}")
            print(f"   Current username: {user.username}")
            print(f"   Has subscription: {user.has_subscription}")
            print(f"   Subscription type: {user.subscription_type}")
            print(f"   Is admin: {user.is_admin}")
            
            # Sikre at han har riktige tilganger
            user.has_subscription = True
            user.subscription_type = 'lifetime'
            user.subscription_start = datetime.utcnow()
            user.subscription_end = None
            user.is_admin = True
            
            # Sett et standard passord hvis han ikke har det
            if not user.password_hash:
                user.set_password('defaultpassword123')
                print("   ⚠️  Satt standard passord: defaultpassword123")
            
            db.session.commit()
            print("   ✅ Helene har nå lifetime premium tilgang!")
            
        else:
            print(f"❌ Helene ikke funnet! Oppretter bruker...")
            user = User(
                username='Helenetollanberntsen',
                email=email,
                has_subscription=True,
                subscription_type='lifetime',
                subscription_start=datetime.utcnow(),
                subscription_end=None,
                is_admin=True
            )
            user.set_password('defaultpassword123')
            db.session.add(user)
            db.session.commit()
            print(f"✅ Opprettet Helene med lifetime premium!")

if __name__ == '__main__':
    sikre_Helene_tilgang()
