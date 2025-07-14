#!/usr/bin/env python3
"""
Aksjeradar Health Check and Repair Tool
This script checks for common issues and attempts to fix them where possible.
It focuses on:
1. Verifying application structure
2. Checking route registration
3. Validating form CSRF protection
4. Testing database connectivity
5. Checking for required dependencies
"""
import os
import sys
import importlib
import subprocess
import json
from pathlib import Path
from datetime import datetime

class Color:
    """Terminal color codes for pretty output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a formatted header"""
    print(f"\n{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{message.center(80)}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}\n")

def print_section(message):
    """Print a formatted section header"""
    print(f"\n{Color.BLUE}{Color.BOLD}{'-' * 80}{Color.ENDC}")
    print(f"{Color.BLUE}{Color.BOLD}{message}{Color.ENDC}")
    print(f"{Color.BLUE}{Color.BOLD}{'-' * 80}{Color.ENDC}\n")

def print_result(check_name, success, message=""):
    """Print check result with appropriate color"""
    if success:
        result = f"{Color.GREEN}✓ PASS{Color.ENDC}"
    else:
        result = f"{Color.RED}✗ FAIL{Color.ENDC}"
        
    print(f"{result} - {check_name}")
    if message:
        print(f"     {message}")
    return success

def run_command(command):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), -1

class AksjeradarHealthCheck:
    """Health check and repair tool for Aksjeradar"""
    
    def __init__(self, app_dir):
        self.app_dir = Path(app_dir)
        self.issues = []
        self.fixes = []
    
    def check_app_structure(self):
        """Check the basic application structure"""
        print_section("Checking Application Structure")
        
        # Check for essential directories
        essential_dirs = [
            "",  # app root
            "templates",
            "static",
            "models",
            "routes",
            "services",
            "utils"
        ]
        
        missing_dirs = []
        for d in essential_dirs:
            dir_path = self.app_dir / d
            exists = dir_path.exists() and dir_path.is_dir()
            print_result(f"Directory: {d or 'app root'}", exists)
            if not exists:
                missing_dirs.append(d)
                self.issues.append(f"Missing directory: {d or 'app root'}")
        
        # Check for essential files
        essential_files = [
            "__init__.py",
            "app.py",
            "config.py",
            "extensions.py",
            "models/__init__.py",
            "routes/__init__.py",
            "utils/__init__.py"
        ]
        
        missing_files = []
        for f in essential_files:
            file_path = self.app_dir / f
            exists = file_path.exists() and file_path.is_file()
            print_result(f"File: {f}", exists)
            if not exists:
                missing_files.append(f)
                self.issues.append(f"Missing file: {f}")
        
        # Create missing directories
        if missing_dirs:
            print_section("Creating Missing Directories")
            for d in missing_dirs:
                dir_path = self.app_dir / d
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print_result(f"Created directory: {d or 'app root'}", True)
                    self.fixes.append(f"Created directory: {d or 'app root'}")
                except Exception as e:
                    print_result(f"Create directory: {d or 'app root'}", False, str(e))
        
        # Create missing files
        if missing_files:
            print_section("Creating Missing Files")
            for f in missing_files:
                file_path = self.app_dir / f
                try:
                    # Make sure parent directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create an empty file or a basic template based on the file
                    if f == "__init__.py":
                        content = "# This file makes the directory a Python package\n"
                    elif f == "app.py":
                        content = """from flask import Flask
from flask_login import LoginManager

from .extensions import db, migrate, csrf
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    # Register blueprints
    from .routes.main import main
    app.register_blueprint(main)
    
    from .routes.auth import auth
    app.register_blueprint(auth)
    
    # Other blueprints would be registered here
    
    return app
"""
                    elif f == "config.py":
                        content = """import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""
                    elif f == "extensions.py":
                        content = """from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Database
db = SQLAlchemy()

# Migrations
migrate = Migrate()

# CSRF Protection
csrf = CSRFProtect()
"""
                    else:
                        content = "# Auto-generated file\n"
                    
                    with open(file_path, 'w') as file:
                        file.write(content)
                    
                    print_result(f"Created file: {f}", True)
                    self.fixes.append(f"Created file: {f}")
                except Exception as e:
                    print_result(f"Create file: {f}", False, str(e))
        
        return not (missing_dirs or missing_files)
    
    def check_route_registration(self):
        """Check route registration in the application"""
        print_section("Checking Route Registration")
        
        # Look for blueprint files
        blueprint_files = list(self.app_dir.glob("routes/*.py"))
        if not blueprint_files:
            print_result("Blueprint Files", False, "No blueprint files found in routes directory")
            self.issues.append("No blueprint files found in routes directory")
            return False
        
        print_result("Blueprint Files", True, f"Found {len(blueprint_files)} blueprint files")
        
        # Check if blueprints are registered in app.py
        app_py_path = self.app_dir / "app.py"
        if not app_py_path.exists():
            print_result("app.py File", False, "app.py file not found")
            self.issues.append("app.py file not found")
            return False
        
        with open(app_py_path, 'r') as f:
            app_py_content = f.read()
        
        # Extract blueprint module names
        blueprint_modules = []
        for file in blueprint_files:
            module_name = file.stem
            if module_name != "__init__" and module_name != "__pycache__":
                blueprint_modules.append(module_name)
        
        # Check if each blueprint is imported and registered
        missing_imports = []
        missing_registrations = []
        for module in blueprint_modules:
            import_pattern = f"from .routes.{module} import"
            register_pattern = f"app.register_blueprint"
            
            if import_pattern not in app_py_content:
                missing_imports.append(module)
                self.issues.append(f"Blueprint {module} is not imported in app.py")
            
            # This is a simple check, might not catch all cases
            if register_pattern not in app_py_content:
                missing_registrations.append(module)
                self.issues.append(f"Blueprint {module} might not be registered in app.py")
        
        if missing_imports or missing_registrations:
            print_result("Blueprint Registration", False, 
                         f"Missing imports: {', '.join(missing_imports) if missing_imports else 'None'}, "
                         f"Missing registrations: {', '.join(missing_registrations) if missing_registrations else 'None'}")
            
            # Generate a fix for app.py
            if missing_imports or missing_registrations:
                print_section("Fixing Blueprint Registration")
                
                # Read current app.py
                with open(app_py_path, 'r') as f:
                    lines = f.readlines()
                
                # Find where to insert import statements
                import_idx = -1
                for i, line in enumerate(lines):
                    if "from .routes." in line:
                        import_idx = i
                        while i + 1 < len(lines) and "from .routes." in lines[i + 1]:
                            i += 1
                        import_idx = i + 1
                        break
                
                # Find where to insert register statements
                register_idx = -1
                for i, line in enumerate(lines):
                    if "app.register_blueprint" in line:
                        register_idx = i
                        while i + 1 < len(lines) and "app.register_blueprint" in lines[i + 1]:
                            i += 1
                        register_idx = i + 1
                        break
                
                # Add missing imports
                new_lines = lines.copy()
                if import_idx >= 0 and missing_imports:
                    for module in missing_imports:
                        new_lines.insert(import_idx, f"    from .routes.{module} import {module}\n")
                        import_idx += 1
                        register_idx += 1  # Adjust register_idx after inserting imports
                
                # Add missing registrations
                if register_idx >= 0 and missing_registrations:
                    for module in missing_registrations:
                        new_lines.insert(register_idx, f"    app.register_blueprint({module})\n")
                        register_idx += 1
                
                # Write updated app.py
                if new_lines != lines:
                    with open(app_py_path, 'w') as f:
                        f.writelines(new_lines)
                    
                    print_result("Fix Blueprint Registration", True, "Updated app.py with missing blueprint imports and registrations")
                    self.fixes.append("Updated app.py with missing blueprint imports and registrations")
                else:
                    print_result("Fix Blueprint Registration", False, "Could not update app.py automatically")
            
            return False
        
        print_result("Blueprint Registration", True, "All blueprints appear to be properly registered")
        return True
    
    def check_csrf_protection(self):
        """Check CSRF protection in templates"""
        print_section("Checking CSRF Protection")
        
        # Find all templates with forms
        form_templates = []
        for ext in ('*.html', '*.j2', '*.jinja', '*.jinja2'):
            form_templates.extend(self.app_dir.glob(f"templates/**/{ext}"))
        
        if not form_templates:
            print_result("Form Templates", False, "No templates found")
            self.issues.append("No templates found")
            return False
        
        print_result("Form Templates", True, f"Found {len(form_templates)} templates")
        
        # Check each template for forms and CSRF tokens
        templates_missing_csrf = []
        for template in form_templates:
            with open(template, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Simple check for forms
            if "<form" in content:
                # Check for CSRF token
                if "csrf_token" not in content and "{{ form.hidden_tag() }}" not in content:
                    templates_missing_csrf.append(template.relative_to(self.app_dir))
                    self.issues.append(f"Template missing CSRF protection: {template.relative_to(self.app_dir)}")
        
        if templates_missing_csrf:
            print_result("CSRF Protection", False, f"{len(templates_missing_csrf)} templates missing CSRF protection")
            
            # Generate fixes for templates
            print_section("Fixing CSRF Protection")
            
            for template_path in templates_missing_csrf:
                full_path = self.app_dir / template_path
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Simple replacement strategy - add CSRF token to forms
                # This is a basic approach and might need manual review
                if "<form" in content and "</form>" in content:
                    lines = content.split('\n')
                    new_lines = []
                    in_form = False
                    csrf_added = False
                    
                    for line in lines:
                        if "<form" in line and not in_form:
                            in_form = True
                            new_lines.append(line)
                        elif in_form and not csrf_added and not "</form>" in line:
                            # Add CSRF token after form opening but before form closing
                            if "<input" in line or "<button" in line or "<textarea" in line or "<select" in line:
                                # Add before the first input element
                                new_lines.append("    <input type=\"hidden\" name=\"csrf_token\" value=\"{{ csrf_token() }}\">")
                                new_lines.append(line)
                                csrf_added = True
                            else:
                                new_lines.append(line)
                        elif "</form>" in line and in_form:
                            if not csrf_added:
                                # Last resort: add right before form closing
                                new_lines.append("    <input type=\"hidden\" name=\"csrf_token\" value=\"{{ csrf_token() }}\">")
                                csrf_added = True
                            new_lines.append(line)
                            in_form = False
                            csrf_added = False
                        else:
                            new_lines.append(line)
                    
                    # Write updated template
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(new_lines))
                    
                    print_result(f"Fix CSRF in {template_path}", True)
                    self.fixes.append(f"Added CSRF token to {template_path}")
                else:
                    print_result(f"Fix CSRF in {template_path}", False, "Could not locate form tags properly")
            
            return False
        
        print_result("CSRF Protection", True, "All templates with forms include CSRF protection")
        return True
    
    def check_database_config(self):
        """Check database configuration"""
        print_section("Checking Database Configuration")
        
        # Check config.py for database configuration
        config_py_path = self.app_dir / "config.py"
        if not config_py_path.exists():
            print_result("config.py File", False, "config.py file not found")
            self.issues.append("config.py file not found")
            return False
        
        with open(config_py_path, 'r') as f:
            config_content = f.read()
        
        # Check for database URI configuration
        if "SQLALCHEMY_DATABASE_URI" in config_content:
            print_result("Database URI Configuration", True)
        else:
            print_result("Database URI Configuration", False, "SQLALCHEMY_DATABASE_URI not found in config.py")
            self.issues.append("SQLALCHEMY_DATABASE_URI not found in config.py")
            
            # Generate fix for config.py
            print_section("Fixing Database Configuration")
            
            if "class Config" in config_content:
                # Add database URI to existing Config class
                lines = config_content.split('\n')
                config_class_idx = -1
                
                for i, line in enumerate(lines):
                    if "class Config" in line:
                        config_class_idx = i
                        break
                
                if config_class_idx >= 0:
                    # Find where to insert the database URI
                    insert_idx = config_class_idx + 1
                    while insert_idx < len(lines) and not lines[insert_idx].strip().startswith('def ') and not lines[insert_idx].strip().startswith('class '):
                        insert_idx += 1
                    
                    # Insert database URI
                    lines.insert(insert_idx, "    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'")
                    lines.insert(insert_idx + 1, "    SQLALCHEMY_TRACK_MODIFICATIONS = False")
                    
                    # Write updated config.py
                    with open(config_py_path, 'w') as f:
                        f.write('\n'.join(lines))
                    
                    print_result("Fix Database Configuration", True, "Added database URI configuration to config.py")
                    self.fixes.append("Added database URI configuration to config.py")
                else:
                    print_result("Fix Database Configuration", False, "Could not locate Config class in config.py")
            else:
                # Create a new Config class
                if "import os" not in config_content:
                    config_content = "import os\n\n" + config_content
                
                config_content += "\n\nclass Config:\n"
                config_content += "    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'\n"
                config_content += "    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'\n"
                config_content += "    SQLALCHEMY_TRACK_MODIFICATIONS = False\n"
                
                # Write updated config.py
                with open(config_py_path, 'w') as f:
                    f.write(config_content)
                
                print_result("Fix Database Configuration", True, "Created Config class with database URI in config.py")
                self.fixes.append("Created Config class with database URI in config.py")
            
            return False
        
        # Check for database file
        db_file = self.app_dir.parent / "app.db"  # Assuming db file is in parent directory
        if db_file.exists():
            print_result("Database File", True, f"Found database file: {db_file}")
        else:
            print_result("Database File", False, f"Database file not found at expected location: {db_file}")
            self.issues.append(f"Database file not found at expected location: {db_file}")
            
            # Attempt to initialize database
            print_section("Initializing Database")
            
            # Create a simple script to initialize the database
            init_db_script = """
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized successfully")
"""
            
            init_db_path = self.app_dir.parent / "init_db.py"
            with open(init_db_path, 'w') as f:
                f.write(init_db_script)
            
            # Run the script
            stdout, stderr, returncode = run_command(f"cd {self.app_dir.parent} && python init_db.py")
            
            if returncode == 0:
                print_result("Initialize Database", True, stdout.strip())
                self.fixes.append("Initialized database")
            else:
                print_result("Initialize Database", False, f"Error: {stderr}")
                self.issues.append(f"Failed to initialize database: {stderr}")
            
            return False
        
        return True
    
    def check_dependencies(self):
        """Check for required dependencies"""
        print_section("Checking Dependencies")
        
        # Define essential packages
        essential_packages = [
            "flask",
            "flask-login",
            "flask-sqlalchemy",
            "flask-migrate",
            "flask-wtf",
            "werkzeug",
            "jinja2",
            "sqlalchemy",
            "wtforms",
            "email-validator",
            "python-dotenv",
            "requests"
        ]
        
        # Check each package
        missing_packages = []
        for package in essential_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
                print_result(f"Package: {package}", True)
            except ImportError:
                print_result(f"Package: {package}", False, "Not installed")
                missing_packages.append(package)
                self.issues.append(f"Missing dependency: {package}")
        
        # Install missing packages
        if missing_packages:
            print_section("Installing Missing Dependencies")
            
            packages_str = " ".join(missing_packages)
            stdout, stderr, returncode = run_command(f"pip install {packages_str}")
            
            if returncode == 0:
                print_result("Install Dependencies", True, f"Installed missing packages: {packages_str}")
                self.fixes.append(f"Installed missing packages: {packages_str}")
            else:
                print_result("Install Dependencies", False, f"Error: {stderr}")
                self.issues.append(f"Failed to install dependencies: {stderr}")
            
            return False
        
        return True
    
    def generate_report(self):
        """Generate a detailed report of issues and fixes"""
        print_section("Generating Report")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": len(self.issues),
            "fixes_applied": len(self.fixes),
            "issues": self.issues,
            "fixes": self.fixes
        }
        
        report_file = self.app_dir.parent / "health_check_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to: {report_file}")
        
        # Generate a markdown summary
        summary = f"""# Aksjeradar Health Check Report

## Overview

Health check performed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

- **Issues found:** {len(self.issues)}
- **Fixes applied:** {len(self.fixes)}

## Issues

{"No issues found." if not self.issues else ""}

{chr(10).join([f"- {issue}" for issue in self.issues])}

## Fixes Applied

{"No fixes were needed." if not self.fixes else ""}

{chr(10).join([f"- {fix}" for fix in self.fixes])}

## Next Steps

{"The application appears to be in good health. No further action needed." if not self.issues else "Some issues were found and fixed automatically. Manual review is recommended for the remaining issues."}
"""
        
        summary_file = self.app_dir.parent / "health_check_summary.md"
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        print(f"Summary saved to: {summary_file}")
    
    def run_all_checks(self):
        """Run all health checks"""
        print_header("Aksjeradar Health Check and Repair Tool")
        print(f"Checking application at: {self.app_dir}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.check_app_structure()
        self.check_route_registration()
        self.check_csrf_protection()
        self.check_database_config()
        self.check_dependencies()
        
        print_header("Health Check Complete")
        print(f"Issues found: {len(self.issues)}")
        print(f"Fixes applied: {len(self.fixes)}")
        
        self.generate_report()


def parse_arguments():
    """Parse command line arguments"""
    import argparse
    parser = argparse.ArgumentParser(description='Aksjeradar Health Check and Repair Tool')
    parser.add_argument('--app-dir', default='/workspaces/aksjeny/app', help='Path to the application directory')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    checker = AksjeradarHealthCheck(args.app_dir)
    checker.run_all_checks()
