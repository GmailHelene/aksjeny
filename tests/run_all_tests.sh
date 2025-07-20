#!/bin/bash

# Comprehensive test runner for Aksjeradar
echo "🚀 Starting Aksjeradar comprehensive testing suite"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="${1:-http://localhost:5000}"

echo "🎯 Testing against: $BASE_URL"

# Check if server is running
echo -e "\n📡 Checking server status..."
if curl -s "$BASE_URL/api/health" > /dev/null; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${RED}❌ Server is not running${NC}"
    echo "Please start the server first:"
    echo "cd /workspaces/aksjeny/app && python run.py"
    exit 1
fi

# Create test results directory
RESULTS_DIR="test_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo -e "\n📁 Test results will be saved to: $RESULTS_DIR"

# Run comprehensive endpoint test
echo -e "\n🌐 Running comprehensive endpoint tests..."
python test_comprehensive_app.py --url "$BASE_URL" > "$RESULTS_DIR/comprehensive_test.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Comprehensive tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some comprehensive tests failed (see log)${NC}"
fi

# Run styling tests
echo -e "\n🎨 Running styling and contrast tests..."
python test_styling_issues.py --url "$BASE_URL" > "$RESULTS_DIR/styling_test.log" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ No high-severity styling issues found${NC}"
else
    echo -e "${YELLOW}⚠️  Styling issues detected (see log)${NC}"
fi

# Test as different user types
echo -e "\n👥 Testing access control..."

# Test unauthenticated access
echo "  Testing unauthenticated user access..."
curl -s "$BASE_URL/portfolio" -w "\n  Portfolio: %{http_code}\n" -o /dev/null
curl -s "$BASE_URL/analysis/ai" -w "  AI Analysis: %{http_code}\n" -o /dev/null
curl -s "$BASE_URL/admin" -w "  Admin: %{http_code}\n" -o /dev/null

# Performance test
echo -e "\n⚡ Running performance tests..."
for page in "/" "/stocks" "/analysis" "/pricing"; do
    response_time=$(curl -s -o /dev/null -w "%{time_total}" "$BASE_URL$page")
    echo "  $page: ${response_time}s"
done

# API response test
echo -e "\n🔌 Testing API endpoints..."
api_endpoints=(
    "/api/health"
    "/api/version"
    "/api/search?q=equinor"
    "/api/oslo_stocks"
)

for endpoint in "${api_endpoints[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    if [ "$status" = "200" ]; then
        echo -e "  $endpoint: ${GREEN}✅ $status${NC}"
    else
        echo -e "  $endpoint: ${RED}❌ $status${NC}"
    fi
done

# Generate summary report
echo -e "\n📊 Generating summary report..."
cat > "$RESULTS_DIR/summary.txt" << EOF
Aksjeradar Comprehensive Test Summary
====================================
Date: $(date)
Base URL: $BASE_URL

Test Results:
- Comprehensive endpoint test: Check comprehensive_test.log
- Styling issues test: Check styling_test.log
- Access control: Manual verification needed
- Performance: Check individual response times above
- API endpoints: Check status codes above

Next Steps:
1. Review any failed tests in the log files
2. Fix high-severity styling issues first
3. Ensure all protected endpoints properly redirect
4. Optimize slow-loading pages (>2s)
5. Verify all API endpoints return valid JSON

Log files location: $RESULTS_DIR/
EOF

echo -e "${GREEN}✅ Test suite completed!${NC}"
echo -e "📄 Summary saved to: $RESULTS_DIR/summary.txt"
echo -e "\n🔍 Review the detailed logs in $RESULTS_DIR/ for any issues"

# Check for critical issues
if grep -q "high_severity" "$RESULTS_DIR"/*.log 2>/dev/null; then
    echo -e "\n${RED}⚠️  CRITICAL: High severity issues found!${NC}"
    echo "Please review and fix these issues before deployment."
    exit 1
else
    echo -e "\n${GREEN}🎉 No critical issues found!${NC}"
    exit 0
fi
