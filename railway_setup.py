import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*50}")
    print(f"🚀 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        
        if result.returncode != 0:
            print(f"❌ {script_name} failed with return code {result.returncode}")
            return False
        
        print(f"✅ {script_name} completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    print("🔧 Setting up Railway production environment...")
    
    scripts = [
        ("install_dependencies.py", "Installing dependencies"),
        ("check_database.py", "Checking database connection"),
        ("run_migration.py", "Running database migration")
    ]
    
    for script, description in scripts:
        if os.path.exists(script):
            if not run_script(script, description):
                print(f"\n❌ Setup failed at: {script}")
                sys.exit(1)
        else:
            print(f"⚠️ Script not found: {script}")
    
    print("\n🎉 Setup completed successfully!")
    print("Your Railway production database should now be ready!")

if __name__ == "__main__":
    main()
