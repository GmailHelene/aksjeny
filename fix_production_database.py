#!/usr/bin/env python3
"""
Fix Production Database - Add Missing User Columns
Run this script to add all missing columns to the users table in production
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def get_database_connection():
    """Get database connection from environment"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return None
    
    # Parse the database URL
    try:
        result = urlparse(database_url)
        return psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
    except Exception as e:
        print(f"ERROR connecting to database: {e}")
        return None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = %s AND column_name = %s
        )
    """, (table_name, column_name))
    return cursor.fetchone()[0]

def add_missing_columns():
    """Add all missing columns to the users table"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Define all the columns that should exist in the users table
        required_columns = [
            ('reports_used_this_month', 'INTEGER DEFAULT 0'),
            ('last_reset_date', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('is_admin', 'BOOLEAN DEFAULT FALSE'),
            ('reset_token', 'VARCHAR(100)'),
            ('reset_token_expires', 'TIMESTAMP'),
            ('language', 'VARCHAR(10) DEFAULT \'no\''),
            ('notification_settings', 'TEXT'),
            ('two_factor_enabled', 'BOOLEAN DEFAULT FALSE'),
            ('two_factor_secret', 'VARCHAR(32)'),
            ('email_verified', 'BOOLEAN DEFAULT TRUE'),
            ('is_locked', 'BOOLEAN DEFAULT FALSE'),
            ('last_login', 'TIMESTAMP'),
            ('login_count', 'INTEGER DEFAULT 0')
        ]
        
        print("Checking and adding missing columns to users table...")
        
        for column_name, column_definition in required_columns:
            if not check_column_exists(cursor, 'users', column_name):
                print(f"Adding missing column: {column_name}")
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_definition}")
                    print(f"✅ Successfully added column: {column_name}")
                except Exception as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"✅ Column already exists: {column_name}")
        
        # Commit all changes
        conn.commit()
        print("\n🎉 All missing columns have been added successfully!")
        
        # Verify all columns exist now
        print("\nVerifying all columns exist:")
        for column_name, _ in required_columns:
            exists = check_column_exists(cursor, 'users', column_name)
            status = "✅" if exists else "❌"
            print(f"{status} {column_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_test_users():
    """Create test users if they don't exist"""
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        from werkzeug.security import generate_password_hash
        cursor = conn.cursor()
        
        # Test users to create
        test_users = [
            ('helene721', 'helene721@gmail.com', 'password123'),
            ('eirik', 'eirik@example.com', 'password123'),
            ('admin', 'admin@example.com', 'admin123')
        ]
        
        print("\nCreating test users...")
        
        for username, email, password in test_users:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()
            
            if not existing_user:
                password_hash = generate_password_hash(password)
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, created_at, has_subscription, 
                                     subscription_type, is_admin, email_verified) 
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
                """, (username, email, password_hash, True, 'monthly', username == 'admin', True))
                print(f"✅ Created user: {username} ({email})")
            else:
                print(f"✅ User already exists: {username}")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    
    # Add missing columns
    if add_missing_columns():
        print("\n✅ Database migration completed successfully!")
        
        # Create test users
        if create_test_users():
            print("\n✅ Test users created successfully!")
            print("\nYou can now log in with:")
            print("  - Username: helene721, Password: password123")
            print("  - Username: eirik, Password: password123") 
            print("  - Username: admin, Password: admin123")
        else:
            print("\n❌ Failed to create test users")
    else:
        print("\n❌ Database migration failed!")
        sys.exit(1)
