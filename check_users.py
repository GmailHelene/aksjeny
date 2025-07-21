import os
import psycopg2
import sys

# Hardcoded Railway database URL for production
RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def get_database_url():
    """Get database URL"""
    return os.getenv('DATABASE_URL') or RAILWAY_DATABASE_URL

def check_users_table():
    """Check users table structure and content"""
    db_url = get_database_url()
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print("🔍 Checking users table...")
        
        # Check table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Users table structure ({len(columns)} columns):")
        for col_name, col_type, nullable, default in columns:
            default_str = f" DEFAULT {default}" if default else ""
            print(f"  - {col_name}: {col_type} (nullable: {nullable}){default_str}")
        
        # Check number of users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n👥 Total users in database: {user_count}")
        
        if user_count > 0:
            # Show first few users
            cursor.execute("SELECT id, email, username, created_at FROM users LIMIT 5")
            users = cursor.fetchall()
            
            print("\n📋 Sample users:")
            for user_id, email, username, created_at in users:
                print(f"  - ID: {user_id}, Email: {email}, Username: {username}, Created: {created_at}")
        else:
            print("\n⚠️ No users found in database!")
            print("You may need to register some users first.")
        
        return user_count > 0
        
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("👥 Checking users in Railway database...")
    check_users_table()
