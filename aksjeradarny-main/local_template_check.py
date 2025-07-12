#!/usr/bin/env python3
"""
Template syntax checker for current directory
"""
import os
import re
from pathlib import Path

def check_template_syntax(file_path):
    """Check a template file for syntax errors"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    errors = []
    
    # Check for unmatched if/endif statements
    if_count = len(re.findall(r'{%\s*if\s+', content))
    endif_count = len(re.findall(r'{%\s*endif\s*%}', content))
    
    if if_count != endif_count:
        errors.append(f"Unmatched if/endif: {if_count} if statements, {endif_count} endif statements")
    
    # Check for for/endfor statements
    for_count = len(re.findall(r'{%\s*for\s+', content))
    endfor_count = len(re.findall(r'{%\s*endfor\s*%}', content))
    
    if for_count != endfor_count:
        errors.append(f"Unmatched for/endfor: {for_count} for statements, {endfor_count} endfor statements")
    
    # Check for block/endblock statements
    block_count = len(re.findall(r'{%\s*block\s+', content))
    endblock_count = len(re.findall(r'{%\s*endblock\s*%}', content))
    
    if block_count != endblock_count:
        errors.append(f"Unmatched block/endblock: {block_count} block statements, {endblock_count} endblock statements")
    
    # Check for duplicate endblock/endfor without matching start
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '{% endblock %}' in line:
            # Check if there's a corresponding block before this endblock
            preceding_text = '\n'.join(lines[:i])
            block_before = len(re.findall(r'{%\s*block\s+', preceding_text))
            endblock_before = len(re.findall(r'{%\s*endblock\s*%}', preceding_text))
            if endblock_before >= block_before:
                errors.append(f"Line {i+1}: Orphaned endblock - no matching block")
        
        if '{% endfor %}' in line:
            # Check if there's a corresponding for before this endfor
            preceding_text = '\n'.join(lines[:i])
            for_before = len(re.findall(r'{%\s*for\s+', preceding_text))
            endfor_before = len(re.findall(r'{%\s*endfor\s*%}', preceding_text))
            if endfor_before >= for_before:
                errors.append(f"Line {i+1}: Orphaned endfor - no matching for")
    
    return errors

def main():
    print("=== Template Syntax Checker ===\n")
    
    template_dir = Path("app/templates")
    if not template_dir.exists():
        print("Template directory not found: app/templates")
        return
    
    html_files = list(template_dir.rglob("*.html"))
    print(f"Found {len(html_files)} HTML template files\n")
    
    total_errors = 0
    problem_files = []
    
    for html_file in sorted(html_files):
        relative_path = html_file.relative_to(template_dir)
        errors = check_template_syntax(html_file)
        
        if errors:
            print(f"❌ {relative_path}:")
            for error in errors:
                print(f"   - {error}")
            print()
            total_errors += len(errors)
            problem_files.append(str(relative_path))
        else:
            print(f"✅ {relative_path}")
    
    print(f"\n=== Summary ===")
    print(f"Total files checked: {len(html_files)}")
    print(f"Files with errors: {len(problem_files)}")
    print(f"Total errors: {total_errors}")
    
    if problem_files:
        print(f"\nFiles with syntax errors:")
        for file in problem_files:
            print(f"  - {file}")

if __name__ == "__main__":
    main()
