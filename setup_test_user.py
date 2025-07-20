#!/usr/bin/env python3

import sqlite3
import hashlib
from werkzeug.security import generate_password_hash
import os

def test_login():
    """Test innlogging med eksisterende bruker"""
    db_path = 'instance/app.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Sjekk eksisterende brukere og passord-hasher
        cursor.execute("SELECT id, username, email, password_hash FROM users LIMIT 5;")
        users = cursor.fetchall()
        
        print("👥 Eksisterende brukere:")
        for user in users:
            print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
            print(f"    Password hash: {user[3][:50]}..." if user[3] else "    No password hash")
        
        # Legg til test-passord for helene721 
        test_password = "test123"
        password_hash = generate_password_hash(test_password)
        
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?
            WHERE username = 'helene721'
        """, (password_hash,))
        
        conn.commit()
        print(f"\n✅ Oppdaterte passord for helene721 til: {test_password}")
        
        # Verifiser oppdatering
        cursor.execute("SELECT username, password_hash FROM users WHERE username = 'helene721'")
        result = cursor.fetchone()
        if result:
            print(f"✅ Passord hash oppdatert: {result[1][:50]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Feil: {e}")

if __name__ == "__main__":
    test_login()
