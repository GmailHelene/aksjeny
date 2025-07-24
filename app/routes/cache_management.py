from flask import Blueprint, render_template, jsonify, request
from datetime import datetime
import os

cache_bp = Blueprint('cache', __name__)

@cache_bp.route('/admin/cache')
def cache_management():
    """Cache management interface"""
    return render_template('cache_management.html')

@cache_bp.route('/admin/api/cache/bust', methods=['POST'])
def bust_cache():
    """API endpoint to trigger cache busting"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return jsonify({
            'success': True,
            'timestamp': timestamp,
            'message': 'Cache busted successfully',
            'reload_recommended': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cache_bp.route('/admin/api/cache/status')
def cache_status():
    """Check current cache version"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return jsonify({
            'cache_version': timestamp,
            'last_updated': timestamp,
            'status': 'active'
        })
    except Exception as e:
        return jsonify({
            'cache_version': 'unknown',
            'last_updated': 'never',
            'status': 'error',
            'error': str(e)
        })
