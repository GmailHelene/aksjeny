#!/bin/bash

# Test script to verify requirements.txt works
echo "🔍 Testing requirements.txt..."

# Check for git dependencies
echo "1. Checking for git+ dependencies..."
if grep -q "git+" requirements.txt; then
    echo "❌ Found git+ dependencies in requirements.txt"
    grep "git+" requirements.txt
    exit 1
else
    echo "✅ No git+ dependencies found"
fi

# Check finviz version
echo "2. Checking finviz version..."
finviz_line=$(grep "finviz" requirements.txt)
echo "   Found: $finviz_line"

if [[ "$finviz_line" == "finviz==1.4.4" ]]; then
    echo "✅ Correct finviz PyPI version"
else
    echo "❌ Incorrect finviz version"
    exit 1
fi

# Count lines
line_count=$(wc -l < requirements.txt)
echo "3. Requirements file has $line_count lines"

echo "✅ All checks passed! Ready for deployment."
