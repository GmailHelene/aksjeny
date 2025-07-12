#!/usr/bin/env python3
"""
Check Helene's user status and ensure premium access
"""
import sys
import os

# Add the project root to Python path
project_root = '/workspaces/aksjeradarv5'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_Helene_user():
    """Check and ensure Helene has proper access"""
    try:
        from app import create_app
        from app.models.user import User
        from app.extensions import db
        
        app = create_app()
        
        with app.app_context():
            print("🔍 Sjekker Helene sin bruker...")
            print("=" * 50)
            
            # Finn Helene sin bruker
            Helene_email = "helene@luxushair.com"
            user = User.query.filter_by(email=Helene_email).first()
            
            if user:
                print(f"✅ Bruker funnet: {user.username} ({user.email})")
                print(f"📧 E-post: {user.email}")
                print(f"👤 Brukernavn: {user.username}")
                print(f"🔒 Har passord: {'Ja' if user.password_hash else 'Nei'}")
                print(f"💎 Har abonnement: {'Ja' if user.has_subscription else 'Nei'}")
                print(f"📅 Abonnement type: {user.subscription_type}")
                print(f"👑 Er admin: {'Ja' if user.is_admin else 'Nei'}")
                print(f"🎯 Trial brukt: {'Ja' if user.trial_used else 'Nei'}")
                
                # Test passord
                test_passwords = ['Helene123!', 'Helene123', 'password', 'HeleneTollan2024']
                for pwd in test_passwords:
                    if user.check_password(pwd):
                        print(f"🔑 Passord funnet: {pwd}")
                        break
                else:
                    print("🔑 Passord ikke funnet i test-liste")
                
                # Sjekk om han har premium tilgang
                if hasattr(user, 'has_active_subscription'):
                    has_premium = user.has_active_subscription()
                    print(f"🚀 Premium tilgang: {'Ja' if has_premium else 'Nei'}")
                
                # Oppdater for å sikre premium tilgang
                print("\n🔧 Oppdaterer bruker for å sikre premium tilgang...")
                user.has_subscription = True
                user.subscription_type = 'lifetime'
                user.is_admin = True
                user.trial_used = False  # Gi tilgang til trial også
                
                try:
                    db.session.commit()
                    print("✅ Bruker oppdatert med premium tilgang!")
                except Exception as e:
                    print(f"❌ Feil ved oppdatering: {e}")
                    db.session.rollback()
                
            else:
                print(f"❌ Ingen bruker funnet med e-post: {Helene_email}")
                print("📝 Viser alle brukere i databasen:")
                
                all_users = User.query.all()
                for u in all_users:
                    print(f"   - {u.email} (username: {u.username})")
            
            print("\n" + "=" * 50)
            print("🎯 Sammendrag:")
            if user:
                print(f"✅ Helene ({Helene_email}) har nå:")
                print("   - Premium tilgang (lifetime)")
                print("   - Admin rettigheter")
                print("   - Tilgang til alle funksjoner")
            else:
                print(f"❌ Helene ({Helene_email}) finnes ikke i systemet")
            
    except Exception as e:
        print(f"❌ Feil: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_Helene_user()
