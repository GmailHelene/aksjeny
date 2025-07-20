#!/usr/bin/env python3

import sqlite3
import os

def check_database_structure():
    """Sjekk struktur på users-tabellen"""
    db_path = 'instance/app.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database {db_path} finnes ikke")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Sjekk alle tabeller
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Tabeller i databasen: {[t[0] for t in tables]}")
        
        if 'users' in [t[0] for t in tables]:
            # Sjekk users-tabellstruktur  
            cursor.execute("PRAGMA table_info(users);")
            columns = cursor.fetchall()
            
            print("\n👤 Users-tabellstruktur:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
                
            # Test login med eksisterende bruker
            cursor.execute("SELECT id, username, email FROM users LIMIT 5;")
            users = cursor.fetchall()
            
            if users:
                print(f"\n👥 Eksisterende brukere:")
                for user in users:
                    print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
            else:
                print("\n❌ Ingen brukere funnet")
        else:
            print("\n❌ Users-tabellen finnes ikke")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Feil ved sjekking av database: {e}")

if __name__ == "__main__":
    check_database_structure()
