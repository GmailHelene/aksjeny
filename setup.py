from setuptools import setup, find_packages
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

setup(
    name="aksjeradar",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.3",
        "flask-sqlalchemy==3.1.1",
        "flask-migrate==4.0.5",
        "flask-login==0.6.2",
        "flask-wtf==1.1.1",
        "flask-mail==0.9.1",
        "gunicorn==21.2.0",
        "python-dotenv==1.0.0",
        "pandas==2.1.1",
        "matplotlib==3.8.0",
        "plotly==5.17.0",
        "yfinance==0.2.31",
        "requests==2.31.0",
        "Werkzeug==2.3.7",
        "openai==0.28.0",
        "fpdf2==2.7.4",
        "newsapi-python==0.2.6",
        "numpy==1.26.0",
        "itsdangerous==2.1.2",
        "pytz==2023.3",
        "stripe==6.1.0",
        "WTForms==3.0.1",
        "email-validator==2.0.0",
        "Jinja2==3.1.2",
        "MarkupSafe==2.1.3",
        "scikit-learn==1.3.0",
        "python-dateutil==2.8.2",
        "beautifulsoup4==4.12.2",
        "psycopg2-binary>=2.9.9",
        "redis==4.5.1",
        "celery==5.3.0",
        "colorama==0.4.6",
        "psutil",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "aksjeradar=main:app",
        ],
    },
)
