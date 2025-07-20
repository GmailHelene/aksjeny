import os
import re

def fix_template_urls():
    """Fix all template URL references"""
    template_dirs = [
        '/workspaces/aksjeny/app/templates',
        '/workspaces/aksjeny/app/templates/stocks',
        '/workspaces/aksjeny/app/templates/portfolio',
        '/workspaces/aksjeny/app/templates/admin',
        '/workspaces/aksjeny/app/templates/pricing'
    ]
    
    fixes_made = []
    
    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            continue
            
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        original_content = content
                        
                        # Fix auth.register -> main.register
                        content = re.sub(r"url_for\(['\"](auth\.register)['\"]", "url_for('main.register'", content)
                        
                        # Fix stocks.details ticker -> symbol
                        content = re.sub(r"url_for\(['\"](stocks\.details)['\"],\s*ticker=", "url_for('stocks.details', symbol=", content)
                        
                        # Fix auth.login -> main.login
                        content = re.sub(r"url_for\(['\"](auth\.login)['\"]", "url_for('main.login'", content)
                        
                        # Fix auth.logout -> main.logout
                        content = re.sub(r"url_for\(['\"](auth\.logout)['\"]", "url_for('main.logout'", content)
                        
                        if content != original_content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(content)
                            fixes_made.append(filepath)
                            print(f"Fixed: {filepath}")
                    
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")
    
    print(f"\nTotal files fixed: {len(fixes_made)}")
    return fixes_made

if __name__ == "__main__":
    fix_template_urls()
