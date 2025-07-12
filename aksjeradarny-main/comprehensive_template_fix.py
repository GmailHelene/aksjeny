#!/usr/bin/env python3
"""
Comprehensive template fixer - removes all orphaned endblocks systematically
"""
import os
import re
from pathlib import Path

def fix_all_templates():
    """Fix all templates by removing orphaned endblocks"""
    template_dir = Path("app/templates")
    if not template_dir.exists():
        print("Template directory not found")
        return
    
    html_files = list(template_dir.rglob("*.html"))
    fixed_count = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix orphaned endblocks
        lines = content.split('\n')
        fixed_lines = []
        block_stack = []
        changes_made = False
        
        for i, line in enumerate(lines):
            # Check for extends at the beginning
            if line.strip().startswith('{% extends'):
                fixed_lines.append(line)
                continue
            
            # Check for block start
            block_match = re.search(r'{% block (\w+)', line)
            if block_match:
                block_stack.append(block_match.group(1))
                fixed_lines.append(line)
                continue
            
            # Check for endblock
            if '{% endblock %}' in line or '{% endblock' in line:
                if block_stack:
                    # This endblock matches a proper block
                    block_stack.pop()
                    fixed_lines.append(line)
                else:
                    # This is an orphaned endblock - remove it
                    changes_made = True
                    print(f"Removing orphaned endblock from {html_file.relative_to(template_dir)} at line {i+1}")
                    continue
            else:
                fixed_lines.append(line)
        
        # Write fixed content if changes were made
        if changes_made:
            fixed_content = '\n'.join(fixed_lines)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            fixed_count += 1
    
    print(f"Fixed {fixed_count} template files")
    return fixed_count

def main():
    print("Comprehensive Template Fixer")
    print("=" * 40)
    
    # Fix all templates
    fixed_count = fix_all_templates()
    
    print(f"\nFixed {fixed_count} templates")
    print("Run simple_template_check.py to verify fixes")

if __name__ == "__main__":
    main()
