from flask import Blueprint, jsonify, request, make_response, current_app, render_template_string, url_for, redirect
from datetime import datetime
import os
import re
import glob
from ..services.realtime_data_service import get_real_time_service

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/api/cache/bust', methods=['POST'])
def bust_cache():
    """API endpoint to trigger cache busting with improved file updates"""
    try:
        # Generate new timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Update cache version file
        with open('app/cache_version.py', 'w') as f:
            f.write(f"CACHE_BUST_VERSION = '{timestamp}'\n")
        
        # Update base.html cache busting variables
        base_html_path = 'app/templates/base.html'
        if os.path.exists(base_html_path):
            with open(base_html_path, 'r') as f:
                content = f.read()
            
            # Update cache-bust meta tag
            content = re.sub(
                r'<meta name="cache-bust" content="[^"]*">',
                f'<meta name="cache-bust" content="{timestamp}">',
                content
            )
            
            # Update CSS version parameter
            content = re.sub(
                r'href="{{ url_for\(\'static\', filename=\'css/style\.css\'\) }}\?v=[^"]*"',
                f'href="{{ url_for(\'static\', filename=\'css/style.css\') }}?v={timestamp}"',
                content
            )
            
            # Update JS version parameters
            content = re.sub(
                r'src="{{ url_for\(\'static\', filename=\'js/main\.js\'\) }}\?v=[^"]*"',
                f'src="{{ url_for(\'static\', filename=\'js/main.js\') }}?v={timestamp}"',
                content
            )
            
            content = re.sub(
                r'src="{{ url_for\(\'static\', filename=\'js/dropdown-navigation\.js\'\) }}\?v=[^"]*"',
                f'src="{{ url_for(\'static\', filename=\'js/dropdown-navigation.js\') }}?v={timestamp}"',
                content
            )
            
            # Update cache force refresh comment
            today = datetime.now().strftime('%B %d, %Y %H:%M')
            content = re.sub(
                r'<!-- Cache FORCE refresh: [^-]* -->',
                f'<!-- Cache FORCE refresh: {today} -->',
                content
            )
            
            # Write updated content back
            with open(base_html_path, 'w') as f:
                f.write(content)
        
        # Clear any server-side caches
        if hasattr(current_app, 'cache'):
            try:
                current_app.cache.clear()
                current_app.logger.info("Application cache cleared")
            except Exception as e:
                current_app.logger.error(f"Failed to clear application cache: {str(e)}")
        
        # Clear realtime data service cache
        try:
            from ..services.realtime_data_service import get_real_time_service
            realtime_service = get_real_time_service()
            if realtime_service:
                realtime_service.clear_cache()
                current_app.logger.info("Realtime data service cache cleared")
        except Exception as e:
            current_app.logger.error(f"Failed to clear realtime data cache: {str(e)}")
        
        return jsonify({
            'success': True,
            'timestamp': timestamp,
            'message': 'Cache busted successfully with file updates'
        })
    except Exception as e:
        current_app.logger.error(f"Cache busting failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/api/cache/status')
def cache_status():
    """Check current cache version with enhanced info"""
    try:
        cache_info = {
            'timestamp': datetime.now().isoformat(),
            'files': {}
        }
        
        # Check cache_version.py
        try:
            with open('app/cache_version.py', 'r') as f:
                content = f.read()
                version = content.split("'")[1] if "'" in content else "unknown"
                cache_info['cache_version'] = version
        except:
            cache_info['cache_version'] = 'unknown'
        
        # Check base.html cache meta
        try:
            with open('app/templates/base.html', 'r') as f:
                content = f.read()
                meta_match = re.search(r'<meta name="cache-bust" content="([^"]*)?"', content)
                if meta_match:
                    cache_info['meta_version'] = meta_match.group(1)
                
                # Check CSS and JS version params
                css_match = re.search(r'css/style\.css\'\) }}\?v=([^"]*)"', content)
                if css_match:
                    cache_info['css_version'] = css_match.group(1)
                
                js_match = re.search(r'js/main\.js\'\) }}\?v=([^"]*)"', content)
                if js_match:
                    cache_info['js_version'] = js_match.group(1)
                
                # Get copyright year
                copyright_match = re.search(r'&copy; (\d{4})', content)
                if copyright_match:
                    cache_info['copyright_year'] = copyright_match.group(1)
        except Exception as e:
            cache_info['template_error'] = str(e)
        
        # App server info
        cache_info['server_info'] = {
            'python_version': os.popen('python --version').read().strip(),
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'app_mode': os.environ.get('FLASK_ENV', 'production')
        }
        
        return jsonify(cache_info)
    except Exception as e:
        current_app.logger.error(f"Cache status check failed: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@cache_bp.route('/force-refresh')
def force_refresh_page():
    """Returns an HTML page that forces browser cache refresh"""
    refresh_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <title>Refreshing Cache...</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                margin-top: 100px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .spinner {
                width: 40px;
                height: 40px;
                margin: 20px auto;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Refreshing Cache</h1>
            <div class="spinner"></div>
            <p>Please wait, clearing browser cache and redirecting...</p>
            <p><small>Timestamp: {{ timestamp }}</small></p>
        </div>
        
        <script>
            // Clear all caches
            function clearCaches() {
                // Clear localStorage
                localStorage.clear();
                
                // Clear sessionStorage
                sessionStorage.clear();
                
                // Clear application cache if available
                if (window.applicationCache) {
                    window.applicationCache.swapCache();
                }
                
                // Request service worker to clear cache if available
                if (navigator.serviceWorker) {
                    navigator.serviceWorker.getRegistrations().then(function(registrations) {
                        for(let registration of registrations) {
                            registration.update();
                        }
                    });
                }
                
                // Redirect after a short delay
                setTimeout(function() {
                    window.location.href = '/?cache_bust={{ timestamp }}';
                }, 1500);
            }
            
            // Run the cache clearing
            clearCaches();
        </script>
    </body>
    </html>
    """

@cache_bp.route('/force-refresh', methods=['GET'])
def force_refresh():
    """Force a complete cache refresh - useful for fixing stale content"""
    try:
        # Generate new timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Update cache version file
        with open('app/cache_version.py', 'w') as f:
            f.write(f"CACHE_BUST_VERSION = '{timestamp}'\n")
        
        # Update base.html cache busting variables
        base_html_path = 'app/templates/base.html'
        if os.path.exists(base_html_path):
            with open(base_html_path, 'r') as f:
                content = f.read()
            
            # Update cache-bust meta tag
            content = re.sub(
                r'<meta name="cache-bust" content="[^"]*">',
                f'<meta name="cache-bust" content="{timestamp}">',
                content
            )
            
            # Update CSS version parameter
            content = re.sub(
                r'href="{{ url_for\(\'static\', filename=\'css/style\.css\'\) }}\?v=[^"]*"',
                f'href="{{ url_for(\'static\', filename=\'css/style.css\') }}?v={timestamp}"',
                content
            )
            
            # Update JS version parameters
            content = re.sub(
                r'src="{{ url_for\(\'static\', filename=\'js/main\.js\'\) }}\?v=[^"]*"',
                f'src="{{ url_for(\'static\', filename=\'js/main.js\') }}?v={timestamp}"',
                content
            )
            
            # Update cache force refresh comment
            today = datetime.now().strftime('%B %d, %Y %H:%M')
            content = re.sub(
                r'<!-- Cache FORCE refresh: [^-]* -->',
                f'<!-- Cache FORCE refresh: {today} -->',
                content
            )
            
            # Write updated content back
            with open(base_html_path, 'w') as f:
                f.write(content)
        
        # Clear realtime data service cache
        realtime_service = get_real_time_service()
        if realtime_service:
            realtime_service.clear_cache()
        
        # Redirect to homepage with new cache parameters
        return redirect(url_for('main.index', v=timestamp))
    except Exception as e:
        current_app.logger.error(f"Error in force_refresh: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = make_response(render_template_string(refresh_html, timestamp=timestamp))
    
    # Set cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response
