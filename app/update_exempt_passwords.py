#!/usr/bin/env python3
"""
Update password for all exempt users to 'aksjeradar2024'
"""

import sys
sys.path.append('/workspaces/aksjeradarv6')

def update_exempt_passwords():
    print("🔐 OPPDATERER PASSORD FOR EXEMPT BRUKERE")
    print("=" * 50)
    
    try:
        from app import create_app
        from app.models.user import User
        from app.extensions import db
        from werkzeug.security import generate_password_hash
        
        app = create_app()
        
        with app.app_context():
            # Get exempt users from access control
            from app.utils.access_control import EXEMPT_EMAILS
            
            new_password = "aksjeradar2024"
            hashed_password = generate_password_hash(new_password)
            
            print(f"🔑 Nytt passord: {new_password}")
            print(f"📧 Exempt emails: {list(EXEMPT_EMAILS)}")
            print()
            
            updated_count = 0
            
            for email in EXEMPT_EMAILS:
                user = User.query.filter_by(email=email).first()
                
                if user:
                    # Update password
                    user.password_hash = hashed_password
                    print(f"✅ Oppdatert passord for: {user.email} (bruker: {user.username})")
                    updated_count += 1
                else:
                    print(f"❌ Bruker ikke funnet: {email}")
            
            # Commit changes
            db.session.commit()
            
            print()
            print("=" * 50)
            print(f"🎯 RESULTAT:")
            print(f"✅ Oppdaterte {updated_count} brukere")
            print(f"🔑 Nytt passord for alle: {new_password}")
            print()
            print("📋 LOGIN INFORMASJON:")
            
            # Show login info for each user
            for email in EXEMPT_EMAILS:
                user = User.query.filter_by(email=email).first()
                if user:
                    print(f"   👤 {user.username} / {new_password}")
                    print(f"   📧 {user.email}")
                    print()
            
            print("🚀 ALLE EXEMPT BRUKERE KAN NÅ LOGGE INN!")
            
    except Exception as e:
        print(f"❌ Feil: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_exempt_passwords()
