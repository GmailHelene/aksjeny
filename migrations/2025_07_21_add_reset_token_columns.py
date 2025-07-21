"""
Migration: Add reset token columns and other missing columns to users table
Date: 2025-01-21
"""

# SQL migrations to execute
MIGRATIONS = [
    # Add password column if it doesn't exist
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255);",
    
    # Add username column if it doesn't exist
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);",
    
    # Add created_at column if it doesn't exist
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();",
    
    # Ensure the reset_token column exists in the users table
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255);",
    
    # Ensure the reset_token_expires column exists in the users table  
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP;"
]

def up():
    """Apply the migration"""
    return MIGRATIONS

def down():
    """Rollback the migration"""
    return [
        "ALTER TABLE users DROP COLUMN IF EXISTS password;",
        "ALTER TABLE users DROP COLUMN IF EXISTS username;",
        "ALTER TABLE users DROP COLUMN IF EXISTS created_at;",
        "ALTER TABLE users DROP COLUMN IF EXISTS reset_token;",
        "ALTER TABLE users DROP COLUMN IF EXISTS reset_token_expires;"
    ]