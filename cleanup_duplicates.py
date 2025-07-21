"""
Script to identify and clean up duplicate/unused templates and files
"""
import os
import shutil
from pathlib import Path

def find_template_duplicates():
    """Find duplicate templates that should be consolidated"""
    templates_dir = Path('/workspaces/aksjeny/app/templates')
    
    # Known duplicates to consolidate
    duplicates_to_remove = [
        # Warren Buffett analysis duplicates
        'analysis/warren-buffet.html',  # Keep warren_buffett.html
        
        # Stock details duplicates  
        'stocks/details.html',  # Keep detail.html
        
        # Investment guide duplicates
        'seo/investment_gudie.html',  # Typo - keep investment_guides.html
        
        # Portfolio duplicates
        'portfolio/Advanced.html',  # Keep lowercase advanced.html
        
        # Analysis duplicates
        'analysis/Advanced.html',   # Keep lowercase advanced.html
        'analysis/technical_html',  # Should be technical.html
        'analysis/ai_html',         # Should be ai.html
        
        # Feature duplicates
        'features/ai_predicitons.html',  # Typo - should be predictions
        
        # Pro duplicates  
        'pro/portfoluo_anayzer.html',   # Typo - should be portfolio_analyzer
    ]
    
    removed_count = 0
    for duplicate in duplicates_to_remove:
        file_path = templates_dir / duplicate
        if file_path.exists():
            print(f"Removing duplicate: {duplicate}")
            file_path.unlink()
            removed_count += 1
    
    return removed_count

def consolidate_templates():
    """Consolidate similar templates"""
    templates_dir = Path('/workspaces/aksjeny/app/templates')
    
    # Templates to consolidate
    consolidations = {
        # Compare templates - use one unified compare.html
        'stocks/compare_form.html': 'stocks/compare.html',
        
        # Blog templates - consolidate to one structure
        'seo/blog_index.html': 'news/index.html',
        'seo/blog_post.html': 'news/article.html',
    }
    
    for old_template, new_template in consolidations.items():
        old_path = templates_dir / old_template
        new_path = templates_dir / new_template
        
        if old_path.exists() and new_path.exists():
            print(f"Removing redundant template: {old_template} (using {new_template})")
            old_path.unlink()

def create_missing_templates():
    """Create missing critical templates"""
    templates_dir = Path('/workspaces/aksjeny/app/templates')
    
    # Create missing template structure
    missing_templates = [
        'dashboard/financial.html',
        'insider_trading/index.html', 
        'analysis/technical.html',
        'portfolio/create.html',
        'portfolio/view.html',
        'pro/screener.html',
    ]
    
    for template in missing_templates:
        template_path = templates_dir / template
        if not template_path.exists():
            # Create directory if it doesn't exist
            template_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Need to create: {template}")

if __name__ == "__main__":
    print("Starting template cleanup...")
    
    removed = find_template_duplicates()
    print(f"Removed {removed} duplicate templates")
    
    consolidate_templates()
    print("Consolidated redundant templates")
    
    create_missing_templates()
    print("Identified missing templates")
    
    print("Cleanup complete!")
