#!/usr/bin/env python3
"""
Create missing exempt users with password 'aksjeradar2024'
"""

import sys
sys.path.append('/workspaces/aksjeradarv6')

def create_missing_exempt_users():
    print("👥 OPPRETTER MANGLENDE EXEMPT BRUKERE")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.models.user import User
        from app.extensions import db
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        app = create_app()
        
        with app.app_context():
            from app.utils.access_control import EXEMPT_EMAILS
            
            password = "aksjeradar2024"
            hashed_password = generate_password_hash(password)
            
            missing_users = [
                {
                    'email': 'helene@luxushair.com',
                    'username': 'helene_luxus'
                },
                {
                    'email': 'eiriktollan.berntsen@gmail.com', 
                    'username': 'eiriktollan'
                }
            ]
            
            for user_data in missing_users:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                
                if not existing_user:
                    new_user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=hashed_password,
                        is_admin=True,
                        has_subscription=True,
                        subscription_start=datetime.utcnow(),
                        reports_used_this_month=0,
                        last_reset_date=datetime.utcnow()
                    )
                    
                    db.session.add(new_user)
                    print(f"✅ Opprettet ny bruker: {user_data['email']} (bruker: {user_data['username']})")
                else:
                    print(f"ℹ️ Bruker eksisterer allerede: {user_data['email']}")
            
            db.session.commit()
            
            print("\n" + "=" * 50)
            print("🎯 KOMPLETT LOGIN OVERSIKT:")
            print(f"🔑 Passord for alle: {password}")
            print()
            
            # Show all exempt users
            for email in EXEMPT_EMAILS:
                user = User.query.filter_by(email=email).first()
                if user:
                    print(f"👤 Bruker: {user.username}")
                    print(f"📧 Email: {user.email}")
                    print(f"🔑 Passord: {password}")
                    print(f"👑 Admin: {user.is_admin}")
                    print(f"💎 Abonnement: {user.has_subscription}")
                    print()
            
            print("🚀 ALLE 4 EXEMPT BRUKERE ER NÅ KLARE!")
            
    except Exception as e:
        print(f"❌ Feil: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_missing_exempt_users()
