#!/usr/bin/env python3
"""
Template fixer for Aksjeradar - fixes Jinja2 template syntax errors
"""
import os
import re
from pathlib import Path

def fix_base_template():
    """Fix the base.html template structure"""
    base_path = Path("app/templates/base.html")
    
    if not base_path.exists():
        print("❌ base.html not found")
        return False
    
    # Read current content
    with open(base_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count current issues
    orphaned_endblocks = len(re.findall(r'{% endblock %}', content))
    proper_blocks = len(re.findall(r'{% block \w+', content))
    
    print(f"Current base.html has {orphaned_endblocks} endblock tags and {proper_blocks} block tags")
    
    # Remove problematic endblocks that are not inside proper block definitions
    lines = content.split('\n')
    fixed_lines = []
    in_proper_block = False
    block_stack = []
    
    for i, line in enumerate(lines):
        # Check for block start
        block_match = re.search(r'{% block (\w+)', line)
        if block_match:
            block_stack.append(block_match.group(1))
            in_proper_block = True
            fixed_lines.append(line)
            continue
        
        # Check for endblock
        if '{% endblock %}' in line:
            if block_stack:
                # This endblock matches a proper block
                block_stack.pop()
                fixed_lines.append(line)
            else:
                # This is an orphaned endblock - remove it
                print(f"Removing orphaned endblock at line {i+1}")
                continue
        else:
            fixed_lines.append(line)
    
    # Write fixed content
    fixed_content = '\n'.join(fixed_lines)
    
    # Backup original
    backup_path = base_path.with_suffix('.html.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write fixed version
    with open(base_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed base.html (backup saved as {backup_path.name})")
    return True

def fix_child_templates():
    """Fix child templates with orphaned endblocks"""
    template_dir = Path("app/templates")
    fixed_count = 0
    
    for html_file in template_dir.rglob("*.html"):
        if html_file.name == "base.html":
            continue
            
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if this file has orphaned endblocks
        lines = content.split('\n')
        block_stack = []
        has_orphans = False
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Check for block start
            block_match = re.search(r'{% block (\w+)', line)
            if block_match:
                block_stack.append(block_match.group(1))
                fixed_lines.append(line)
                continue
            
            # Check for endblock
            if '{% endblock %}' in line:
                if block_stack:
                    # This endblock matches a proper block
                    block_stack.pop()
                    fixed_lines.append(line)
                else:
                    # This is an orphaned endblock
                    has_orphans = True
                    print(f"Removing orphaned endblock from {html_file.relative_to(template_dir)} at line {i+1}")
                    continue
            else:
                fixed_lines.append(line)
        
        if has_orphans:
            # Write fixed content
            fixed_content = '\n'.join(fixed_lines)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            fixed_count += 1
    
    print(f"✅ Fixed {fixed_count} child templates")
    return fixed_count

def fix_for_endfor_issues():
    """Fix for/endfor mismatches"""
    template_dir = Path("app/templates")
    fixed_count = 0
    
    for html_file in template_dir.rglob("*.html"):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count for/endfor statements
        for_count = len(re.findall(r'{%\s*for\s+', content))
        endfor_count = len(re.findall(r'{%\s*endfor\s*%}', content))
        
        if for_count != endfor_count:
            lines = content.split('\n')
            for_stack = []
            fixed_lines = []
            has_orphan_endfor = False
            
            for i, line in enumerate(lines):
                # Check for for start
                if re.search(r'{%\s*for\s+', line):
                    for_stack.append(i)
                    fixed_lines.append(line)
                    continue
                
                # Check for endfor
                if re.search(r'{%\s*endfor\s*%}', line):
                    if for_stack:
                        for_stack.pop()
                        fixed_lines.append(line)
                    else:
                        has_orphan_endfor = True
                        print(f"Removing orphaned endfor from {html_file.relative_to(template_dir)} at line {i+1}")
                        continue
                else:
                    fixed_lines.append(line)
            
            if has_orphan_endfor:
                fixed_content = '\n'.join(fixed_lines)
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                fixed_count += 1
    
    print(f"✅ Fixed {fixed_count} for/endfor issues")
    return fixed_count

def main():
    """Main function to fix all template issues"""
    print("🔧 TEMPLATE FIXER - Fixing Jinja2 Syntax Errors")
    print("=" * 50)
    
    # Fix base template first
    fix_base_template()
    
    # Fix child templates
    fix_child_templates()
    
    # Fix for/endfor issues
    fix_for_endfor_issues()
    
    print("\n✅ Template fixing complete!")
    print("🧪 Run local_template_check.py again to verify fixes")

if __name__ == "__main__":
    main()
