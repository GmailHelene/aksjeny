#!/usr/bin/env python3
"""
Quick script to identify and fix syntax errors
"""
import os
import sys

def check_python_file(filepath):
    """Check a Python file for syntax errors"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        compile(source, filepath, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def check_files():
    """Check key files for syntax errors"""
    files_to_check = [
        'app/routes/stocks.py',
        'app/routes/news.py',
        'app/routes/stripe_routes.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"Checking {file_path}...")
            is_valid, error = check_python_file(file_path)
            if is_valid:
                print(f"✅ {file_path} - OK")
            else:
                print(f"❌ {file_path} - ERROR: {error}")
        else:
            print(f"⚠️  {file_path} - File not found")

if __name__ == '__main__':
    check_files()
