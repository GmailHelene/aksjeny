import os
import psycopg2

RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def check_users_table_structure():
    """Check the actual structure of the users table"""
    db_url = os.getenv('DATABASE_URL') or RAILWAY_DATABASE_URL
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("✅ Users table exists")
            
            # Get all columns in users table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"\n📋 Current users table structure ({len(columns)} columns):")
            for col_name, col_type, nullable, default in columns:
                default_str = f" DEFAULT {default}" if default else ""
                print(f"  - {col_name}: {col_type} (nullable: {nullable}){default_str}")
            
            return columns
        else:
            print("❌ Users table does not exist!")
            return []
            
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Checking users table structure...")
    print("=" * 50)
    check_users_table_structure()
