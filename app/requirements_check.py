#!/usr/bin/env python3
"""
Check and install missing requirements
"""

import subprocess
import sys

def check_requirements():
    """Check if all requirements are installed"""
    print("📦 CHECKING REQUIREMENTS")
    print("="*50)
    
    # Core requirements
    requirements = [
        "flask",
        "flask-sqlalchemy",
        "flask-login",
        "flask-wtf",
        "flask-mail",
        "pandas",
        "yfinance",
        "requests",
        "stripe",
        "redis",
        "celery",
        "gunicorn",
        "python-dotenv",
        "email-validator"
    ]
    
    missing = []
    
    for req in requirements:
        try:
            __import__(req.replace("-", "_"))
            print(f"✅ {req}: Installed")
        except ImportError:
            print(f"❌ {req}: Missing")
            missing.append(req)
            
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstalling missing packages...")
        
        for package in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                
    else:
        print("\n✅ All requirements are installed!")
        
    # Create requirements.txt if missing
    if missing or not os.path.exists("requirements.txt"):
        print("\n📝 Creating requirements.txt...")
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        print("✅ Created requirements.txt")

if __name__ == "__main__":
    import os
    check_requirements()
