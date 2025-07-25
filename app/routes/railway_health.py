@cache_bp.route('/railway-health', methods=['GET'])
def railway_health():
    """Health check endpoint specifically for Railway deployment"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('FLASK_ENV', 'production'),
        'cache_version': getattr(current_app, 'config', {}).get('CACHE_BUST_VERSION', 'unknown')
    })
