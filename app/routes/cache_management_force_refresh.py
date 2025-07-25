from flask import Blueprint, jsonify, request, make_response, current_app, render_template_string, url_for, redirect
from datetime import datetime
import os
import re
import glob
from ..services.realtime_data_service import get_real_time_service

# Blueprint definition
cache_bp = Blueprint('cache_management_refresh', __name__)

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
