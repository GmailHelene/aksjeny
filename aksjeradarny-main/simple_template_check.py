#!/usr/bin/env python3
"""
Simple template syntax checker without unicode characters
"""
import os
import re
from pathlib import Path

def check_template_syntax(file_path):
    """Check a template file for syntax errors"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    errors = []
    
    # Check for unmatched block/endblock statements
    block_count = len(re.findall(r'{%\s*block\s+', content))
    endblock_count = len(re.findall(r'{%\s*endblock\s*%}', content))
    
    if block_count != endblock_count:
        errors.append(f"Unmatched block/endblock: {block_count} block, {endblock_count} endblock")
    
    # Check for orphaned endblocks
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '{% endblock %}' in line:
            preceding_text = '\n'.join(lines[:i])
            block_before = len(re.findall(r'{%\s*block\s+', preceding_text))
            endblock_before = len(re.findall(r'{%\s*endblock\s*%}', preceding_text))
            if endblock_before >= block_before:
                errors.append(f"Line {i+1}: Orphaned endblock")
    
    return errors

def main():
    print("Template Syntax Check Results")
    print("=" * 40)
    
    template_dir = Path("app/templates")
    if not template_dir.exists():
        print("Template directory not found")
        return
    
    html_files = list(template_dir.rglob("*.html"))
    total_errors = 0
    problem_files = 0
    
    for html_file in sorted(html_files):
        relative_path = html_file.relative_to(template_dir)
        errors = check_template_syntax(html_file)
        
        if errors:
            problem_files += 1
            total_errors += len(errors)
        else:
            # Don't print individual OK files to reduce output
            pass
    
    print(f"Total files checked: {len(html_files)}")
    print(f"Files with errors: {problem_files}")
    print(f"Total errors: {total_errors}")
    
    if problem_files == 0:
        print("SUCCESS: All templates are now valid!")
    else:
        print(f"ISSUES: {problem_files} files still have syntax errors")

if __name__ == "__main__":
    main()
