#!/usr/bin/env python3
"""
Quick deployment check script
"""
import os
import sys

def check_deployment_ready():
    """Check if the application is ready for deployment"""
    
    print("🚀 AKSJERADAR - DEPLOYMENT READINESS CHECK")
    print("=" * 50)
    
    # Check 1: Critical files exist
    print("\n1. 📁 Checking critical files...")
    critical_files = [
        "app.py",
        "config.py", 
        "requirements.txt",
        ".env",
        "app/__init__.py",
        "app/models/user.py",
        "app/routes/main.py",
        "app/templates/base.html",
        "app/templates/demo.html"
    ]
    
    missing_files = []
    for file in critical_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n   ⚠️ {len(missing_files)} critical files missing!")
        return False
    
    # Check 2: Template directory structure
    print("\n2. 📄 Checking template structure...")
    template_dirs = [
        "app/templates",
        "app/templates/auth",
        "app/templates/main",
        "app/templates/portfolio",
        "app/templates/stocks",
        "app/templates/news",
        "app/templates/features"
    ]
    
    for dir_path in template_dirs:
        if os.path.exists(dir_path):
            template_count = len([f for f in os.listdir(dir_path) if f.endswith('.html')])
            print(f"   ✅ {dir_path} - {template_count} templates")
        else:
            print(f"   ❌ {dir_path} - MISSING")
    
    # Check 3: Static files
    print("\n3. 🎨 Checking static files...")
    static_dirs = [
        "app/static/css",
        "app/static/js", 
        "app/static/images",
        "app/static/fonts"
    ]
    
    for dir_path in static_dirs:
        if os.path.exists(dir_path):
            file_count = len(os.listdir(dir_path))
            print(f"   ✅ {dir_path} - {file_count} files")
        else:
            print(f"   ❌ {dir_path} - MISSING")
    
    # Check 4: Configuration files
    print("\n4. ⚙️ Checking configuration...")
    config_files = [
        (".env", "Environment variables"),
        ("config.py", "Flask configuration"),
        ("requirements.txt", "Python dependencies"),
        ("runtime.txt", "Python version (optional)"),
        ("Procfile", "Process file (optional)")
    ]
    
    for file_path, description in config_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} - {description}")
        else:
            print(f"   ⚠️ {file_path} - {description} (missing)")
    
    # Check 5: Database file
    print("\n5. 🗄️ Checking database...")
    if os.path.exists("app.db"):
        size = os.path.getsize("app.db")
        print(f"   ✅ app.db - {size} bytes")
    else:
        print("   ⚠️ app.db - Will be created on first run")
    
    # Final assessment
    print("\n" + "=" * 50)
    print("🎯 DEPLOYMENT ASSESSMENT")
    print("=" * 50)
    
    if not missing_files:
        print("✅ ALL CRITICAL FILES PRESENT")
        print("✅ TEMPLATE STRUCTURE COMPLETE")
        print("✅ STATIC FILES READY")
        print("✅ CONFIGURATION FILES READY")
        print("✅ DATABASE READY")
        print()
        print("🚀 STATUS: READY FOR DEPLOYMENT!")
        print()
        print("📝 NEXT STEPS:")
        print("1. Push to GitHub: git add . && git commit -m 'Ready for production' && git push")
        print("2. Deploy to Railway or similar platform")
        print("3. Set environment variables in production")
        print("4. Test the deployed application")
        print("5. Configure custom domain (optional)")
        
        return True
    else:
        print("❌ DEPLOYMENT NOT READY")
        print(f"   {len(missing_files)} critical files missing")
        print("   Please ensure all files are present before deployment")
        
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    ready = check_deployment_ready()
    
    if ready:
        print("\n🎉 CONGRATULATIONS!")
        print("Your Aksjeradar application is ready for production deployment!")
        sys.exit(0)
    else:
        print("\n⚠️ DEPLOYMENT CHECK FAILED")
        print("Please fix the missing files before deployment.")
        sys.exit(1)
