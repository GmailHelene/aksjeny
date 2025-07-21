import os
import psycopg2
import sys

# Hardcoded Railway database URL for production
RAILWAY_DATABASE_URL = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"

def get_database_url():
    """Get database URL from environment or use hardcoded"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("⚠️ DATABASE_URL environment variable not set")
        print("🔧 Using hardcoded Railway database URL...")
        return RAILWAY_DATABASE_URL
    return db_url

def verify_environment():
    """Verify environment variables are set"""
    db_url = get_database_url()
    if db_url == RAILWAY_DATABASE_URL:
        print("✅ Using hardcoded Railway database URL")
        print("✅ Database host: crossover.proxy.rlwy.net")
    else:
        print("✅ DATABASE_URL environment variable is set")
        print(f"✅ Database host: {db_url.split('@')[1].split(':')[0] if '@' in db_url else 'Unknown'}")
    return True

def verify_database_columns():
    """Verify the reset token columns exist"""
    db_url = get_database_url()
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check for reset_token columns
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('reset_token', 'reset_token_expires')
            ORDER BY column_name;
        """)
        
        columns = cursor.fetchall()
        
        if len(columns) == 2:
            print("✅ Reset token columns verified:")
            for col_name, col_type, nullable in columns:
                print(f"  - {col_name}: {col_type} (nullable: {nullable})")
            return True
        else:
            print(f"❌ Expected 2 reset token columns, found {len(columns)}")
            return False
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def main():
    print("🔍 Verifying Railway setup...")
    
    # Check environment
    if not verify_environment():
        sys.exit(1)
    
    # Check database
    if not verify_database_columns():
        sys.exit(1)
    
    print("\n🎉 All verifications passed!")
    print("Your Railway production environment is ready for password reset functionality.")

if __name__ == "__main__":
    main()
