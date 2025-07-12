#!/usr/bin/env python3
"""
Check test user password
"""

import sys
sys.path.append('/workspaces/aksjeradarv6')

print("🔍 SJEKKER TESTBRUKER PASSORD")
print("=" * 50)

try:
    from app import create_app
    from app.models.user import User
    
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email='helene721@gmail.com').first()
        if user:
            print(f"✅ Bruker funnet: {user.email}")
            print(f"✅ Brukernavn: {user.username}")
            
            # Test forskjellige passord
            test_passwords = [
                'password123',
                'aksjeradar2024', 
                'Soda2001',
                'helene721',
                'admin',
                'password',
                '123456'
            ]
            
            print(f"\n🔐 Testing passord:")
            found_password = False
            for pwd in test_passwords:
                try:
                    if user.check_password(pwd):
                        print(f"✅ RIKTIG PASSORD: '{pwd}'")
                        found_password = True
                    else:
                        print(f"❌ Feil: '{pwd}'")
                except Exception as e:
                    print(f"⚠️ Error testing '{pwd}': {e}")
            
            if not found_password:
                print(f"\n🔧 PROBLEM: Ingen av test-passordene fungerer!")
                print(f"🔧 Må resette passordet for testbrukeren")
        else:
            print("❌ Testbruker ikke funnet!")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
