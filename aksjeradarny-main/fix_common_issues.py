#!/usr/bin/env python3
"""
Fix common issues in Aksjeradar codebase
"""

import os
import re
import sys

def fix_duplicate_functions():
    """Fix duplicate function definitions in main.py"""
    file_path = "app/routes/main.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find duplicate function definitions
    function_pattern = r'^def\s+(\w+)\s*\('
    functions = {}
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        match = re.match(function_pattern, line)
        if match:
            func_name = match.group(1)
            if func_name in functions:
                print(f"⚠️  Duplicate function found: {func_name} at lines {functions[func_name]+1} and {i+1}")
            else:
                functions[func_name] = i
                
def fix_missing_imports():
    """Add missing imports to files"""
    files_to_check = [
        ("app/__init__.py", ["flask", "app.extensions", "app.models"]),
        ("app/routes/main.py", ["flask", "flask_login", "app.extensions"]),
        ("app/utils/access_control.py", ["flask", "flask_login", "functools"])
    ]
    
    for file_path, required_imports in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ {file_path} not found")
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for imp in required_imports:
            if f"import {imp}" not in content and f"from {imp}" not in content:
                print(f"⚠️  Missing import in {file_path}: {imp}")

def fix_template_errors():
    """Check and fix common template errors"""
    template_dir = "app/templates"
    
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        print(f"✅ Created {template_dir}")
        
    # Check for base template
    base_template = os.path.join(template_dir, "base.html")
    if not os.path.exists(base_template):
        print(f"⚠️  Missing base.html template")
        # Create minimal base template
        with open(base_template, 'w') as f:
            f.write('''<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Aksjeradar{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav>
        <!-- Navigation here -->
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>''')
        print(f"✅ Created base.html template")

def fix_static_files():
    """Ensure static file structure exists"""
    static_dirs = [
        "app/static",
        "app/static/css",
        "app/static/js",
        "app/static/images",
        "app/static/icons"
    ]
    
    for dir_path in static_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ Created {dir_path}")
            
    # Create minimal CSS if missing
    css_file = "app/static/css/style.css"
    if not os.path.exists(css_file):
        with open(css_file, 'w') as f:
            f.write('''/* Aksjeradar Main Styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}''')
        print(f"✅ Created {css_file}")
        
    # Create minimal JS if missing
    js_file = "app/static/js/main.js"
    if not os.path.exists(js_file):
        with open(js_file, 'w') as f:
            f.write('''// Aksjeradar Main JavaScript
console.log('Aksjeradar loaded');''')
        print(f"✅ Created {js_file}")

def main():
    """Run all fixes"""
    print("🔧 FIXING COMMON ISSUES")
    print("="*50)
    
    fix_duplicate_functions()
    fix_missing_imports()
    fix_template_errors()
    fix_static_files()
    
    print("\n✅ Common issues check complete!")

if __name__ == "__main__":
    main()
