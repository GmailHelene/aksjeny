# Decorators module for access control and functionality
from functools import wraps
from flask import current_app, request, jsonify, redirect, url_for
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

def access_required(f):
    """
    Decorator that checks if user has access to premium features.
    Falls back gracefully if subscription check fails.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # If user is not logged in, require login
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login'))
            
            # Check if user has premium access
            if hasattr(current_user, 'has_premium_access') and current_user.has_premium_access():
                return f(*args, **kwargs)
            
            # Check exempt emails
            exempt_emails = current_app.config.get('EXEMPT_EMAILS', [])
            if current_user.email in exempt_emails:
                return f(*args, **kwargs)
            
            # For JSON requests, return error
            if request.is_json:
                return jsonify({
                    'error': 'Premium access required',
                    'message': 'This feature requires a premium subscription'
                }), 403
            
            # For regular requests, redirect to pricing
            return redirect(url_for('main.pricing'))
            
        except Exception as e:
            logger.warning(f"Access check failed: {e}")
            # Fail open - allow access if check fails
            return f(*args, **kwargs)
    
    return decorated_function