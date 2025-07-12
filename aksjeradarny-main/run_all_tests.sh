#!/bin/bash

echo "🚀 AKSJERADAR COMPREHENSIVE TEST SUITE"
echo "======================================"
echo "Starting at: $(date)"
echo

# Make scripts executable
chmod +x *.py

# 1. Check requirements
echo "Step 1: Checking requirements..."
python3 requirements_check.py
echo

# 2. Fix common issues
echo "Step 2: Fixing common issues..."
python3 fix_common_issues.py
echo

# 3. Run comprehensive tests
echo "Step 3: Running comprehensive tests..."
python3 comprehensive_test_and_fix.py
echo

# 4. Final verification
echo "Step 4: Final system verification..."
python3 verify_system.py

echo
echo "======================================"
echo "Test suite completed at: $(date)"
