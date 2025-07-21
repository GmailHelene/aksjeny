import os
import psycopg2
import sys

def check_database():
    """Check database connection and existing tables"""
    database_url = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Database connection successful!")
        
        # Check if users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        
        users_table_exists = cursor.fetchone()[0]
        
        if users_table_exists:
            print("✅ Users table exists")
            
            # Check existing columns in users table
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("\n📋 Existing columns in users table:")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")
            
            # Check if reset_token columns already exist
            existing_cols = [col[0] for col in columns]
            if 'reset_token' in existing_cols:
                print("⚠️ reset_token column already exists")
            if 'reset_token_expires' in existing_cols:
                print("⚠️ reset_token_expires column already exists")
        else:
            print("❌ Users table does not exist!")
            print("You may need to create the users table first")
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 All tables in database ({len(tables)} total):")
        for table in tables:
            print(f"  - {table[0]}")
            
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Checking database status...")
    check_database()
