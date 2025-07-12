#!/usr/bin/env python3
"""
Debug template loading issues
"""

import sys
import os
sys.path.insert(0, '.')

# Test app creation and template loading
try:
    from app import create_app
    app = create_app()
    
    print("✅ App created successfully")
    print(f"📁 Template folder: {app.template_folder}")
    print(f"📁 Static folder: {app.static_folder}")
    
    # List template files
    import os
    template_dir = os.path.join(os.getcwd(), 'app', 'templates')
    print(f"📁 Template directory exists: {os.path.exists(template_dir)}")
    
    if os.path.exists(template_dir):
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    rel_path = os.path.relpath(os.path.join(root, file), template_dir)
                    print(f"  📄 {rel_path}")
    
    # Test template rendering specifically
    with app.app_context():
        from flask import render_template
        try:
            content = render_template('demo.html', title='Test Demo')
            print("✅ demo.html renders successfully")
            print(f"📝 Content length: {len(content)} characters")
        except Exception as e:
            print(f"❌ demo.html render error: {e}")
            
            # Try to find the exact template
            import jinja2
            try:
                env = app.jinja_env
                template = env.get_template('demo.html')
                print("✅ Template found in Jinja environment")
            except jinja2.TemplateNotFound as te:
                print(f"❌ Template not found in Jinja: {te}")
                print(f"📂 Jinja loader paths: {env.loader.searchpath if hasattr(env.loader, 'searchpath') else 'N/A'}")

except Exception as e:
    print(f"❌ Error creating app: {e}")
    import traceback
    traceback.print_exc()
