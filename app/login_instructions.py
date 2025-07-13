#!/usr/bin/env python3
"""
Simple manual login instructions and troubleshooting
"""

print("=== AKSJERADAR LOGIN INSTRUKSJONER ===")
print()

print("📋 STEG FOR STEG LOGIN:")
print("1. Gå til: http://localhost:5000/auth ELLER http://localhost:5000/login")
print("2. I feltet 'Brukernavn' kan du bruke ENTEN:")
print("   - E-post: helene721@gmail.com")
print("   - Brukernavn: helene721")
print("3. I feltet 'Passord' skriv: Soda2001??")
print("4. Klikk 'Logg inn'")
print()

print("🔧 HVIS LOGIN IKKE FUNGERER:")
print("1. Sjekk at du bruker riktig passord: Soda2001?? (med to spørsmålstegn)")
print("2. Prøv å navigere direkt til: http://localhost:5000/auth")
print("3. Sjekk at Flask-appen kjører på port 5000")
print()

print("🔑 GLEMT PASSORD:")
print("1. Gå til login-siden")
print("2. Klikk på 'Glemt passord?' link nederst")
print("3. Dette bør ta deg til: http://localhost:5000/forgot_password")
print("4. Skriv inn e-post: helene721@gmail.com")
print("5. Sjekk e-post for reset-link")
print()

print("⚠️  VANLIGE PROBLEMER:")
print("- Hvis du får 'Brukernavn: This field is required' - sørg for at du fyller ut brukernavn-feltet")
print("- Hvis du får CSRF-feil - refresh siden og prøv igjen")
print("- Hvis siden ikke laster - sjekk at Flask kjører: ps aux | grep python")
print()

print("💡 DEBUGGING:")
print("- Flask app starter med: cd /workspaces/aksjeradarny && python3 run.py")
print("- Sjekk app kjører: curl http://localhost:5000")
print("- Sjekk feilmeldinger i browser developer console")
print()

print("🔍 ALTERNATIVE BRUKERE (hvis helene721 ikke fungerer):")
print("Du kan også prøve disse brukerene som har ubegrenset tilgang:")
print("- E-post: helene@luxushair.com")
print("- E-post: eiriktollan.berntsen@gmail.com") 
print("- E-post: tonjekit91@gmail.com")
print("(Men vi må sjekke passordene for disse i databasen)")
