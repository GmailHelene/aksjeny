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
