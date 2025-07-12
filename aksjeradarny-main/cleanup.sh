#!/usr/bin/env bash
# cleanup.sh - Remove unused files and move legacy files to archive

echo "Cleaning up project..."
# Remove deprecated root-level test files
rm -f test_all_endpoints_access.py test_frontend_urls_access.py

# Remove old OPPRYDDING document (copied to CLEANUP.md)
rm -f OPPRYDDING.MD

# Move legacy migrations to archive
if [ -d migrations ]; then
  mkdir -p archive/migrations_old
  mv migrations/* archive/migrations_old/ || true
fi

# Ensure templates/ and static/ are untouched
# No action on templates/
# No action on static/

# This script is intended to clean up the project by removing unnecessary test files.
# The following test files will be removed:
# - All files starting with 'test_' or 'verify_'

# Remove all root-level test scripts except in tests/ directory
find . -maxdepth 1 -type f \( -name "test_*.py" -o -name "verify_*.py" \) -delete

# Remove debug and comprehensive scenario files at root-level
find . -maxdepth 1 -type f \( -iname "debug*" -o -iname "comprehensive*" \) -delete

# Remove files starting with 'final', 'check', or 'minimal' at root
find . -maxdepth 1 -type f \( -iname "final*" -o -iname "check*" -o -iname "minimal*" \) -delete

echo "Cleanup of test files complete."
echo "Cleanup complete."