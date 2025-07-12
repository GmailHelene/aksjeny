#!/usr/bin/env python3
"""
Check for Jinja2 template syntax errors in all HTML files
"""
import os
import re
from pathlib import Path

def check_template_syntax(file_path):
    """Check a template file for syntax errors"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    errors = []
    
    # Check for unmatched if/elif/else/endif statements
    if_count = len(re.findall(r'{%\s*if\s+', content))
    elif_count = len(re.findall(r'{%\s*elif\s+', content))
    else_count = len(re.findall(r'{%\s*else\s*%}', content))
    endif_count = len(re.findall(r'{%\s*endif\s*%}', content))
    
    if if_count != endif_count:
        errors.append(f"Unmatched if/endif: {if_count} if statements, {endif_count} endif statements")
    
    # Check for for/endfor statements
    for_count = len(re.findall(r'{%\s*for\s+', content))
    endfor_count = len(re.findall(r'{%\s*endfor\s*%}', content))
    
    if for_count != endfor_count:
        errors.append(f"Unmatched for/endfor: {for_count} for statements, {endfor_count} endfor statements")
    
    # Check for with/endwith statements
    with_count = len(re.findall(r'{%\s*with\s+', content))
    endwith_count = len(re.findall(r'{%\s*endwith\s*%}', content))
    
    if with_count != endwith_count:
        errors.append(f"Unmatched with/endwith: {with_count} with statements, {endwith_count} endwith statements")
    
    # Check for block/endblock statements
    block_count = len(re.findall(r'{%\s*block\s+', content))
    endblock_count = len(re.findall(r'{%\s*endblock\s*%}', content))
    
    if block_count != endblock_count:
        errors.append(f"Unmatched block/endblock: {block_count} block statements, {endblock_count} endblock statements")
    
    return errors

def main():
    print("=== Template Syntax Checker ===\n")
    
    template_dir = Path("/workspaces/aksjeradarv6/app/templates")
    if not template_dir.exists():
        template_dir = Path("/workspaces/aksjeradarv6/templates")
    
    if not template_dir.exists():
        print(f"Template directory not found: {template_dir}")
        return
    
    html_files = list(template_dir.rglob("*.html"))
    print(f"Found {len(html_files)} HTML template files\n")
    
    total_errors = 0
    
    for html_file in sorted(html_files):
        relative_path = html_file.relative_to(template_dir)
        errors = check_template_syntax(html_file)
        
        if errors:
            print(f"❌ {relative_path}:")
            for error in errors:
                print(f"   - {error}")
            print()
            total_errors += len(errors)
        else:
            print(f"✅ {relative_path}")
    
    print(f"\n=== Summary ===")
    print(f"Total files checked: {len(html_files)}")
    print(f"Files with errors: {sum(1 for f in html_files if check_template_syntax(f))}")
    print(f"Total errors: {total_errors}")

if __name__ == "__main__":
    main()
