#!/bin/bash

# Aksjeradar Cache Busting Script
# This script forces a full cache refresh across the entire application

echo "🚀 Starting Aksjeradar Cache Busting..."

# Get current timestamp for cache busting
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "📅 Cache bust timestamp: $TIMESTAMP"

# Update version in config
echo "⚙️ Updating application version..."
echo "CACHE_BUST_VERSION = '$TIMESTAMP'" > app/cache_version.py

# Add cache-busting meta tag to base template
echo "🔄 Adding cache-busting meta tag..."
sed -i "s/<meta name=\"cache-bust\".*>/<meta name=\"cache-bust\" content=\"$TIMESTAMP\">/" app/templates/base.html

# If the meta tag doesn't exist, add it
if ! grep -q "cache-bust" app/templates/base.html; then
    sed -i '/<meta name="viewport"/a\    <meta name="cache-bust" content="'$TIMESTAMP'">' app/templates/base.html
fi

# Update static file versions in base template
echo "📦 Updating static file versions..."
sed -i "s/\?v={{ g\.current_time }}/\?v=$TIMESTAMP/g" app/templates/base.html

# Add cache headers to main app
echo "🌐 Configuring cache headers..."
cat > app/cache_headers.py << 'EOF'
from flask import make_response
from datetime import datetime, timedelta

def add_cache_headers(response, cache_timeout=300):
    """Add cache control headers to response"""
    if cache_timeout == 0:
        # No cache for dynamic content
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    else:
        # Cache for static content
        expires = datetime.now() + timedelta(seconds=cache_timeout)
        response.headers['Cache-Control'] = f'public, max-age={cache_timeout}'
        response.headers['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Add ETag for better caching
    response.headers['ETag'] = f'"{hash(response.get_data())}"'
    return response

def force_no_cache(response):
    """Force no cache for dynamic pages"""
    return add_cache_headers(response, 0)
EOF

# Create cache management route
echo "🔧 Creating cache management endpoint..."
cat > app/routes/cache_management.py << 'EOF'
from flask import Blueprint, jsonify, request, make_response
from datetime import datetime
import os

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/api/cache/bust', methods=['POST'])
def bust_cache():
    """API endpoint to trigger cache busting"""
    try:
        # Generate new timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Update cache version file
        with open('app/cache_version.py', 'w') as f:
            f.write(f"CACHE_BUST_VERSION = '{timestamp}'\n")
        
        return jsonify({
            'success': True,
            'timestamp': timestamp,
            'message': 'Cache busted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/api/cache/status')
def cache_status():
    """Check current cache version"""
    try:
        with open('app/cache_version.py', 'r') as f:
            content = f.read()
            version = content.split("'")[1] if "'" in content else "unknown"
        
        return jsonify({
            'cache_version': version,
            'last_updated': version
        })
    except:
        return jsonify({
            'cache_version': 'unknown',
            'last_updated': 'never'
        })
EOF

# Create JavaScript cache busting utility
echo "🎯 Creating client-side cache utilities..."
cat > app/static/js/cache-buster.js << 'EOF'
// Aksjeradar Cache Busting Utilities

class CacheBuster {
    constructor() {
        this.version = this.getCacheVersion();
    }

    getCacheVersion() {
        const meta = document.querySelector('meta[name="cache-bust"]');
        return meta ? meta.getAttribute('content') : Date.now();
    }

    // Force refresh all cached resources
    refreshStaticAssets() {
        const links = document.querySelectorAll('link[rel="stylesheet"]');
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.includes('v=')) {
                link.setAttribute('href', `${href}?v=${this.version}`);
            }
        });

        const scripts = document.querySelectorAll('script[src]');
        scripts.forEach(script => {
            if (!script.src.includes('bootstrap') && !script.src.includes('cdn')) {
                const src = script.getAttribute('src');
                if (src && !src.includes('v=')) {
                    script.setAttribute('src', `${src}?v=${this.version}`);
                }
            }
        });
    }

    // API call to trigger server-side cache bust
    async triggerServerCacheBust() {
        try {
            const response = await fetch('/api/cache/bust', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ Server cache busted:', result.timestamp);
                return result.timestamp;
            } else {
                console.error('❌ Cache bust failed:', result.error);
                return null;
            }
        } catch (error) {
            console.error('❌ Cache bust error:', error);
            return null;
        }
    }

    // Force reload page with cache bust
    hardRefresh() {
        const url = new URL(window.location);
        url.searchParams.set('v', this.version);
        url.searchParams.set('cache_bust', Date.now());
        window.location.href = url.toString();
    }

    // Clear browser storage
    clearBrowserCache() {
        // Clear localStorage
        if (typeof Storage !== "undefined") {
            localStorage.clear();
            sessionStorage.clear();
        }

        // Clear service worker cache if available
        if ('serviceWorker' in navigator && 'caches' in window) {
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => caches.delete(cacheName))
                );
            });
        }
    }

    // Complete cache refresh
    async fullCacheRefresh() {
        console.log('🚀 Starting full cache refresh...');
        
        // 1. Clear browser cache
        this.clearBrowserCache();
        
        // 2. Trigger server cache bust
        const newVersion = await this.triggerServerCacheBust();
        
        // 3. Refresh static assets
        this.refreshStaticAssets();
        
        // 4. Hard refresh page
        setTimeout(() => {
            this.hardRefresh();
        }, 1000);
        
        return newVersion;
    }
}

// Global cache buster instance
window.cacheBuster = new CacheBuster();

// Keyboard shortcut for cache refresh (Ctrl+Shift+R alternative)
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey && e.key === 'F5') {
        e.preventDefault();
        window.cacheBuster.fullCacheRefresh();
    }
});

// Expose cache busting functions globally
window.refreshCache = () => window.cacheBuster.fullCacheRefresh();
window.hardRefresh = () => window.cacheBuster.hardRefresh();
EOF

# Create admin cache management interface
echo "🎮 Creating admin cache interface..."
cat > app/templates/admin/cache_management.html << 'EOF'
{% extends "base.html" %}

{% block title %}Cache Management - Aksjeradar{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1><i class="bi bi-arrow-clockwise"></i> Cache Management</h1>
    
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5>Cache Control Panel</h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <h6>Current Cache Status</h6>
                        <div id="cache-status">
                            <span class="badge bg-secondary">Loading...</span>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2">
                        <button class="btn btn-warning" onclick="bustServerCache()">
                            <i class="bi bi-server"></i> Bust Server Cache
                        </button>
                        <button class="btn btn-info" onclick="refreshClientCache()">
                            <i class="bi bi-browser-chrome"></i> Refresh Client Cache
                        </button>
                        <button class="btn btn-danger" onclick="fullCacheRefresh()">
                            <i class="bi bi-arrow-repeat"></i> Full Cache Refresh (Server + Client)
                        </button>
                    </div>
                    
                    <div id="cache-results" class="mt-3"></div>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h6>Quick Actions</h6>
                </div>
                <div class="card-body">
                    <div class="d-grid gap-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="checkCacheStatus()">
                            Check Status
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="window.location.reload(true)">
                            Hard Reload
                        </button>
                        <button class="btn btn-sm btn-outline-dark" onclick="clearBrowserStorage()">
                            Clear Browser Storage
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="card mt-3">
                <div class="card-header">
                    <h6>Cache Info</h6>
                </div>
                <div class="card-body small">
                    <p><strong>Last Deploy:</strong> <span id="deploy-time">{{ g.current_time }}</span></p>
                    <p><strong>Cache Version:</strong> <span id="cache-version">Loading...</span></p>
                    <p><strong>Environment:</strong> Production</p>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
async function checkCacheStatus() {
    try {
        const response = await fetch('/api/cache/status');
        const data = await response.json();
        
        document.getElementById('cache-status').innerHTML = 
            `<span class="badge bg-success">${data.cache_version}</span>`;
        document.getElementById('cache-version').textContent = data.cache_version;
    } catch (error) {
        document.getElementById('cache-status').innerHTML = 
            `<span class="badge bg-danger">Error: ${error.message}</span>`;
    }
}

async function bustServerCache() {
    const resultsDiv = document.getElementById('cache-results');
    resultsDiv.innerHTML = '<div class="alert alert-info">Busting server cache...</div>';
    
    const newVersion = await window.cacheBuster.triggerServerCacheBust();
    
    if (newVersion) {
        resultsDiv.innerHTML = 
            `<div class="alert alert-success">✅ Server cache busted! New version: ${newVersion}</div>`;
        checkCacheStatus();
    } else {
        resultsDiv.innerHTML = 
            '<div class="alert alert-danger">❌ Failed to bust server cache</div>';
    }
}

async function refreshClientCache() {
    const resultsDiv = document.getElementById('cache-results');
    resultsDiv.innerHTML = '<div class="alert alert-info">Refreshing client cache...</div>';
    
    window.cacheBuster.clearBrowserCache();
    window.cacheBuster.refreshStaticAssets();
    
    resultsDiv.innerHTML = 
        '<div class="alert alert-success">✅ Client cache refreshed!</div>';
}

async function fullCacheRefresh() {
    const resultsDiv = document.getElementById('cache-results');
    resultsDiv.innerHTML = '<div class="alert alert-warning">🚀 Starting full cache refresh...</div>';
    
    await window.cacheBuster.fullCacheRefresh();
}

function clearBrowserStorage() {
    window.cacheBuster.clearBrowserCache();
    document.getElementById('cache-results').innerHTML = 
        '<div class="alert alert-success">✅ Browser storage cleared!</div>';
}

// Load cache status on page load
document.addEventListener('DOMContentLoaded', checkCacheStatus);
</script>
{% endblock %}
EOF

# Commit and deploy changes
echo "📝 Committing cache busting changes..."
git add -A
git commit -m "🚀 Add comprehensive cache busting system - timestamp: $TIMESTAMP"

echo "🚢 Pushing to production..."
git push origin main

echo ""
echo "✅ Cache busting system deployed!"
echo ""
echo "🎯 Access cache management at: https://aksjeradar.trade/admin/cache"
echo "🔧 API endpoints:"
echo "   - POST /api/cache/bust (trigger cache bust)"
echo "   - GET /api/cache/status (check cache version)"
echo ""
echo "🎮 Client-side functions:"
echo "   - refreshCache() - Full cache refresh"
echo "   - hardRefresh() - Hard page reload"
echo "   - Ctrl+Shift+F5 - Keyboard shortcut"
echo ""
echo "Cache bust version: $TIMESTAMP"
