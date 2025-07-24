#!/bin/bash

# Quick Cache Refresh for Aksjeradar
# Simple one-command solution for immediate cache busting

echo "🚀 Quick Cache Refresh - Aksjeradar"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Update cache version in base template
if grep -q "cache-bust" app/templates/base.html; then
    sed -i "s/cache-bust\" content=\"[^\"]*\"/cache-bust\" content=\"$TIMESTAMP\"/" app/templates/base.html
else
    # Add cache-bust meta tag if it doesn't exist
    sed -i '/<meta name="viewport"/a\    <meta name="cache-bust" content="'$TIMESTAMP'">' app/templates/base.html
fi

# Update static file versions
sed -i "s/\?v={{ g\.current_time }}/\?v=$TIMESTAMP/g" app/templates/base.html

# Quick deploy
git add app/templates/base.html
git commit -m "⚡ Quick cache refresh - $TIMESTAMP"
git push origin main

echo "✅ Cache refreshed! New version: $TIMESTAMP"
echo "🌐 Changes will be live in ~30 seconds"
echo ""
echo "💡 Test with: https://aksjeradar.trade?v=$TIMESTAMP"
