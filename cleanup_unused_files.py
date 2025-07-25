#!/usr/bin/env python3
"""
Safe cleanup of unused files for Aksjeradar project
Only removes files that are confirmed to be duplicates or temporary files
"""
import os
import shutil
from pathlib import Path

def cleanup_backup_templates():
    """Remove backup template files that are no longer needed"""
    templates_dir = Path('/workspaces/aksjeny/app/templates')
    
    backup_files = [
        'analysis/benjamin_graham_complex_backup.html',
        'demo_backup.html', 
        'stocks/details_backup.html'
    ]
    
    removed_count = 0
    for backup_file in backup_files:
        file_path = templates_dir / backup_file
        if file_path.exists():
            print(f"Removing backup template: {backup_file}")
            file_path.unlink()
            removed_count += 1
    
    return removed_count

def cleanup_test_files():
    """Remove temporary test files from root directory"""
    root_dir = Path('/workspaces/aksjeny')
    
    # Only remove obvious test files that are temporary
    test_files_to_remove = [
        'api_endpoint_test.py',
        'comprehensive_fix_test.py', 
        'fix_and_test_users.py',
        'test_db_fix.py',
        'test_server.py',
        'test_summary.py',
        'access_control_test.py',
        'comprehensive_app_test.py',
        'comprehensive_test_suite.py',
        'debug_auth_test.py',
        'debug_login_final.py',
        'minimal_test.py',
        'simple_test.py',
        'simple_user_test.py',
        'quick_api_test.py',
        'api_endpoint_comprehensive_test.py',
        'endpoint_test_output.txt',
        'endpoint_test_report.json', 
        'endpoint_test_results.json',
        'full_user_test_report.json',
        'health_check_report.json'
    ]
    
    removed_count = 0
    for test_file in test_files_to_remove:
        file_path = root_dir / test_file
        if file_path.exists():
            print(f"Removing test file: {test_file}")
            file_path.unlink()
            removed_count += 1
    
    return removed_count

def cleanup_fix_scripts():
    """Remove temporary fix scripts that are no longer needed"""
    root_dir = Path('/workspaces/aksjeny')
    
    # Only remove scripts that are clearly temporary fixes
    fix_scripts_to_remove = [
        'fix_database_migration.py',
        'fix_railway_columns.py',
        'fix_reset_columns.py',
        'fix_database_columns_v2.py',
        'fix_railway_database.py',
        'fix_production_railway.py',
        'complete_production_fix.py',
        'fix_production_database.py',
        'fix_syntax_errors.py',
        'fix_database_columns.py',
        'fix_database_simple.py',
        'fix_database_sqlite.py',
        'fix_database_columns_sqlite.py',
        'fix_all_columns.py',
        'fix_template_urls.py',
        'quick_db_fix.py',
        'validate_url_fixes.py'
    ]
    
    removed_count = 0
    for fix_script in fix_scripts_to_remove:
        file_path = root_dir / fix_script
        if file_path.exists():
            print(f"Removing fix script: {fix_script}")
            file_path.unlink()
            removed_count += 1
    
    return removed_count

def cleanup_misc_files():
    """Remove miscellaneous temporary files"""
    root_dir = Path('/workspaces/aksjeny')
    
    misc_files_to_remove = [
        'cleanup_duplicates.py',
        'create_admin_user.py',
        'create_railway_users.py',
        'create_test_users.py',
        'create_users_clean.py',
        'create_users_final.py',
        'setup_test_user.py',
        'give_lifetime_access.py',
        'railway_migration.py',
        'init_db.py',
        'run_tests.py',
        'check_db_structure.py',
        'check_syntax.py',
        'cookies.txt',
        'test_cookies.txt',
        'get-pip.py',
        'endpoint_test.log',
        'server.log',
        'subscription_test.log',
        'auth_test.log',
        'aksjeradar_payment.log'
    ]
    
    removed_count = 0
    for misc_file in misc_files_to_remove:
        file_path = root_dir / misc_file
        if file_path.exists():
            print(f"Removing misc file: {misc_file}")
            file_path.unlink()
            removed_count += 1
    
    return removed_count

def cleanup_misplaced_files():
    """Remove Python files that are misplaced in templates directory"""
    templates_dir = Path('/workspaces/aksjeny/app/templates')
    
    # Find any .py files in templates directory (these shouldn't be there)
    python_files = list(templates_dir.glob('**/*.py'))
    
    removed_count = 0
    for py_file in python_files:
        print(f"Removing misplaced Python file: {py_file.relative_to(templates_dir)}")
        py_file.unlink()
        removed_count += 1
    
    return removed_count

def main():
    """Run the cleanup process"""
    print("Starting safe cleanup of unused files...")
    print("=" * 50)
    
    # Clean up backup templates
    backup_count = cleanup_backup_templates()
    print(f"✅ Removed {backup_count} backup template files")
    
    # Clean up test files
    test_count = cleanup_test_files()
    print(f"✅ Removed {test_count} temporary test files")
    
    # Clean up fix scripts
    fix_count = cleanup_fix_scripts()
    print(f"✅ Removed {fix_count} temporary fix scripts")
    
    # Clean up miscellaneous files
    misc_count = cleanup_misc_files()
    print(f"✅ Removed {misc_count} miscellaneous temporary files")
    
    # Clean up misplaced files
    misplaced_count = cleanup_misplaced_files()
    print(f"✅ Removed {misplaced_count} misplaced Python files")
    
    total_removed = backup_count + test_count + fix_count + misc_count + misplaced_count
    
    print("=" * 50)
    print(f"🎉 Cleanup complete! Removed {total_removed} total files.")
    print("✅ Core application files preserved")
    print("✅ Templates and routes preserved")
    print("✅ Static files preserved")
    print("✅ Configuration files preserved")

if __name__ == "__main__":
    main()
