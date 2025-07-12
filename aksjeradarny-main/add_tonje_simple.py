#!/usr/bin/env python3
"""
Enkel tilnærming - direkte database insert for ny exempt user
"""

import sqlite3
import hashlib
from datetime import datetime

def add_tonje_user_simple():
    """Legger til tonjekit91@gmail.com direkte i SQLite database"""
    
    email = 'tonjekit91@gmail.com'
    username = 'tonjekit91'
    password = 'aksjeradar2024'
    
    # Generer password hash (samme måte som Flask-app gjør det)
    from werkzeug.security import generate_password_hash
    password_hash = generate_password_hash(password)
    
    print(f"🆕 Legger til ny exempt user: {email}")
    print("="*50)
    
    try:
        # Koble til database
        conn = sqlite3.connect('/workspaces/aksjeradarv6/app.db')
        cursor = conn.cursor()
        
        # Sjekk om brukeren allerede eksisterer
        cursor.execute("SELECT id, email FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"📝 Oppdaterer eksisterende bruker: {email}")
            
            cursor.execute("""
                UPDATE users SET 
                    password_hash = ?,
                    has_subscription = 1,
                    subscription_type = 'lifetime',
                    subscription_start = ?,
                    subscription_end = NULL,
                    is_admin = 1,
                    trial_used = 0
                WHERE email = ?
            """, (password_hash, datetime.utcnow().isoformat(), email))
            
        else:
            print(f"🆕 Oppretter ny bruker: {email}")
            
            cursor.execute("""
                INSERT INTO users (
                    username, email, password_hash, created_at,
                    has_subscription, subscription_type, subscription_start,
                    subscription_end, trial_used, trial_start, 
                    stripe_customer_id, is_admin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                username, email, password_hash, datetime.utcnow().isoformat(),
                True, 'lifetime', datetime.utcnow().isoformat(),
                None, False, None, None, True
            ))
        
        conn.commit()
        print(f"   ✅ Bruker lagt til med passord: {password}")
        print(f"   ✅ Lifetime subscription aktivert")
        print(f"   ✅ Admin rettigheter gitt")
        
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
        
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Feil: {str(e)}")

if __name__ == '__main__':
    add_tonje_user_simple()
