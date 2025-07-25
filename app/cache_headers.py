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
