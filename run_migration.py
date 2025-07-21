import os
import subprocess
import sys

def main():
    # Set the Railway database URL
    database_url = "postgresql://postgres:PsOJBeRqPAAcXyOXYCJvidJqMOpSzhqN@crossover.proxy.rlwy.net:17830/railway"
    
    # Set environment variable
    os.environ['DATABASE_URL'] = database_url
    
    print("🔗 Database URL configured")
    print("🚀 Running migration...")
    
    # Run the migration script
    try:
        result = subprocess.run([sys.executable, 'fix_production_railway.py'], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
