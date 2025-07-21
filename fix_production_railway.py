import os
import psycopg2
import sys
import importlib.util

# Hardcoded Railway database URL for production
RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def get_database_url():
    """Get database URL from environment variables or use hardcoded Railway URL"""
    # Try environment variables first
    db_url = (os.getenv('DATABASE_URL') or 
              os.getenv('POSTGRES_URL') or 
              os.getenv('DATABASE_PRIVATE_URL') or
              os.getenv('RAILWAY_DATABASE_URL'))
    
    # If no environment variable, use hardcoded Railway URL
    if not db_url:
        print("⚠️ No DATABASE_URL environment variable found")
        print("🔧 Using hardcoded Railway database URL...")
        db_url = RAILWAY_DATABASE_URL
    else:
        print("✅ Using DATABASE_URL from environment")
    
    return db_url

def run_migrations():
    """Run the database migrations"""
    db_url = get_database_url()
    
    # SQL migrations - FIX the missing columns including password and username
    migrations = [
        # Essential columns for authentication
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();",
        
        # Reset token columns
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token_expires TIMESTAMP;",
        
        # Additional feature columns
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'no';",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS notification_settings TEXT;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS two_factor_secret VARCHAR(32);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT TRUE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_locked BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;"
    ]
    
    try:
        # Connect to the database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("✅ Connected to Railway database successfully")
        
        # Execute each migration
        for i, migration in enumerate(migrations, 1):
            print(f"Running migration {i}: {migration.split()[3:6]}")
            cursor.execute(migration)
            print(f"✓ Migration {i} completed")
        
        # Commit the changes
        conn.commit()
        print("\n🎉 All migrations completed successfully!")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("Database connection closed")

if __name__ == "__main__":
    print("🚀 Starting Railway production database migration...")
    print("🔧 Adding missing password, username, reset_token and other columns...")
    run_migrations()
