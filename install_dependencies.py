import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🔧 Installing Python dependencies...")
    
    # Essential packages for the database migration
    essential_packages = [
        "psycopg2-binary",
        "python-dotenv"
    ]
    
    # Install essential packages first
    for package in essential_packages:
        if not install_package(package):
            print(f"❌ Critical package {package} failed to install")
            sys.exit(1)
    
    # Try to install from requirements.txt if it exists
    if os.path.exists("requirements.txt"):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ All requirements installed from requirements.txt")
        except subprocess.CalledProcessError:
            print("⚠️ Some packages from requirements.txt failed to install")
    
    print("\n🎉 Dependency installation completed!")
    print("Now you can run: python3 run_migration.py")

if __name__ == "__main__":
    main()
