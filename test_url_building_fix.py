#!/usr/bin/env python3
"""
Test script to verify that the URL building error for stocks.details has been fixed
"""

import re
import os
import glob

def check_template_files():
    """Check all template files for incorrect ticker usage with stocks.details"""
    
    template_dirs = [
        'app/templates',
        'app/templates/analysis',
        'app/templates/portfolio', 
        'app/templates/stocks',
        'app/templates/market_intel',
        'app/templates/news'
    ]
    
    errors_found = []
    files_checked = 0
    
    for template_dir in template_dirs:
        if not os.path.exists(template_dir):
            continue
            
        pattern = os.path.join(template_dir, '**/*.html')
        html_files = glob.glob(pattern, recursive=True)
        
        for file_path in html_files:
            files_checked += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for problematic patterns
                bad_pattern = re.findall(r"url_for\('stocks\.details',\s*ticker=", content)
                if bad_pattern:
                    errors_found.append({
                        'file': file_path,
                        'error': 'Found url_for(stocks.details, ticker=...) - should use symbol=',
                        'count': len(bad_pattern)
                    })
                
            except Exception as e:
                print(f"⚠️  Could not read {file_path}: {e}")
    
    return errors_found, files_checked

def main():
    print("🔍 Checking template files for URL building errors...")
    print("=" * 60)
    
    errors, total_files = check_template_files()
    
    print(f"📁 Checked {total_files} template files")
    
    if errors:
        print(f"\n❌ Found {len(errors)} files with errors:")
        for error in errors:
            print(f"   📄 {error['file']}")
            print(f"      🐛 {error['error']} ({error['count']} occurrences)")
            print()
        
        print("🚨 URL building errors still exist! Need to fix these files.")
        return False
    else:
        print("\n✅ No URL building errors found!")
        print("🎉 All template files are correctly using 'symbol=' parameter for stocks.details")
        
        # Also check if the correct pattern exists
        print("\n🔍 Verifying correct usage exists...")
        good_count = 0
        for template_dir in ['app/templates']:
            if not os.path.exists(template_dir):
                continue
                
            pattern = os.path.join(template_dir, '**/*.html')
            html_files = glob.glob(pattern, recursive=True)
            
            for file_path in html_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    good_pattern = re.findall(r"url_for\('stocks\.details',\s*symbol=", content)
                    good_count += len(good_pattern)
                    
                except Exception:
                    pass
        
        print(f"✅ Found {good_count} correct usages of 'symbol=' parameter")
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
