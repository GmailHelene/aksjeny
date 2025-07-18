#!/usr/bin/env python3
"""
Check and fix syntax errors in Python files
"""
import os
import ast

def check_file_syntax(filepath):
    """Check syntax of a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Try to parse the AST
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def main():
    """Check key files for syntax errors"""
    files_to_check = [
        'app/utils/security.py',
        'app/routes/stocks.py',
        'app/routes/news.py',
        'app/templates/index.html'
    ]
    
    print("🔍 Checking files for syntax errors...")
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            if filepath.endswith('.py'):
                is_valid, error = check_file_syntax(filepath)
                if is_valid:
                    print(f"✅ {filepath} - OK")
                else:
                    print(f"❌ {filepath} - ERROR: {error}")
            else:
                print(f"⚠️  {filepath} - Skipped (not Python)")
        else:
            print(f"⚠️  {filepath} - Not found")

if __name__ == '__main__':
    main()
