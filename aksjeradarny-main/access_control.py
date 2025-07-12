from functools import wraps
from flask import redirect, url_for, flash, request, session, current_app, jsonify, make_response
from flask_login import current_user
from datetime import datetime, timedelta
import hashlib
import logging

# Exempt users who always get full access
EXEMPT_EMAILS = {
    'helene@luxushair.com',
    'helene721@gmail.com',
    'eiriktollan.berntsen@gmail.com',
    'tonjekit91@gmail.com'
}

# Trial duration in minutes
TRIAL_DURATION_MINUTES = 10

def access_required(f):
    """Decorator to check if user has access to the resource"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.email in EXEMPT_EMAILS:
            return f(*args, **kwargs)

        if current_user.is_authenticated and hasattr(current_user, 'has_active_subscription') and current_user.has_active_subscription():
            return f(*args, **kwargs)

        if not current_user.is_authenticated:
            trial_status = _get_trial_status_for_unauthenticated()
            
            if trial_status['active']:
                return f(*args, **kwargs)
            else:
                return _handle_no_access()

        if current_user.is_authenticated and hasattr(current_user, 'is_in_trial_period') and current_user.is_in_trial_period():
            return f(*args, **kwargs)

        return _handle_no_access()

    return decorated_function

def premium_required(f):
    """Decorator for premium-only features"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access premium features.', 'info')
            return redirect(url_for('main.login', next=request.url))
        
        if current_user.email in EXEMPT_EMAILS:
            return f(*args, **kwargs)
        
        if hasattr(current_user, 'has_active_subscription') and current_user.has_active_subscription():
            return f(*args, **kwargs)
        
        flash('This is a premium feature. Please upgrade to access.', 'warning')
        return redirect(url_for('main.subscription'))
    
    return decorated_function

def _is_exempt_user():
    """Check if current user is exempt (admin)"""
    return (current_user.is_authenticated and 
            hasattr(current_user, 'email') and 
            current_user.email in EXEMPT_EMAILS)

def _has_active_subscription():
    """Check if user has active subscription with better error handling"""
    if not current_user.is_authenticated:
        return False
        
    try:
        has_sub = False
        if hasattr(current_user, 'has_subscription') and current_user.has_subscription:
            has_sub = True
        elif hasattr(current_user, 'has_active_subscription') and callable(current_user.has_active_subscription):
            has_sub = current_user.has_active_subscription()
        elif hasattr(current_user, 'subscription_type') and current_user.subscription_type != 'free':
            has_sub = True
            
        return has_sub
    except Exception as e:
        if hasattr(current_app, 'logger'):
            current_app.logger.error(f"Error checking subscription: {e}")
        return False

def _get_trial_status_for_unauthenticated():
    """
    Check trial access status for unauthenticated users.
    This function manages the 10-minute device-based trial.
    Returns dict with 'active' (bool), 'start_time' (datetime), 'remaining_minutes' (int), 'expired' (bool).
    """
    device_fingerprint = _get_device_fingerprint()
    trial_key = f"trial_{device_fingerprint}"
    
    trial_start_str = session.get(trial_key) or request.cookies.get(trial_key)
    
    now = datetime.utcnow()
    trial_start = None

    if trial_start_str:
        try:
            trial_start = datetime.fromisoformat(trial_start_str)
        except (ValueError, TypeError):
            trial_start = None

    if not trial_start:
        trial_start = now
        session[trial_key] = trial_start.isoformat()
        session.permanent = True
        
    elapsed = now - trial_start
    trial_active = elapsed <= timedelta(minutes=TRIAL_DURATION_MINUTES)
    remaining_seconds = max(0, int(TRIAL_DURATION_MINUTES * 60 - elapsed.total_seconds()))
    remaining_minutes = int(remaining_seconds / 60)
    
    return {
        'active': trial_active,
        'start_time': trial_start,
        'remaining_minutes': remaining_minutes,
        'expired': not trial_active
    }

def _set_trial_cookie(response, start_time):
    """Set trial tracking cookie on the response object"""
    device_fingerprint = _get_device_fingerprint()
    trial_key = f"trial_{device_fingerprint}"
    response.set_cookie(
        trial_key, 
        start_time.isoformat(), 
        max_age=60*60*24*7,  # 7 days
        httponly=True,
        secure=current_app.config.get('SESSION_COOKIE_SECURE', False)
    )

def _handle_no_access():
    """Handle when user has no access (trial expired, no subscription)"""
    if _is_ajax_request():
        return jsonify({
            'error': 'Access denied',
            'message': 'Trial expired or no active subscription',
            'redirect': url_for('main.demo', source='trial_expired')
        }), 403
    
    return redirect(url_for('main.demo', source='trial_expired'))

def _get_device_fingerprint():
    """Create a simple device fingerprint"""
    fingerprint_data = f"{request.remote_addr}:{request.headers.get('User-Agent', '')}"
    return hashlib.md5(fingerprint_data.encode()).hexdigest()

def _is_ajax_request():
    """Check if request is AJAX"""
    return (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Content-Type', '').startswith('application/json') or
            request.headers.get('Accept', '').startswith('application/json'))

def get_trial_status():
    """Get current trial status for templates"""
    if _is_exempt_user() or _has_active_subscription():
        return {
            'active': True,
            'unlimited': True,
            'remaining_minutes': None,
            'expired': False
        }
    
    return _get_trial_status_for_unauthenticated()

def get_access_level():
    """Get current user's access level for templates"""
    if _is_exempt_user():
        return 'admin'
    elif _has_active_subscription():
        return 'subscriber'
    elif _get_trial_status_for_unauthenticated()['active']:
        return 'trial'
    else:
        return 'restricted'

def get_trial_time_remaining():
    """Get trial time remaining in seconds (for backward compatibility)"""
    if _is_exempt_user() or _has_active_subscription():
        return None
    
    trial_status = _get_trial_status_for_unauthenticated()
    if trial_status['active']:
        return trial_status['remaining_minutes'] * 60
    else:
        return 0

def is_demo_user():
    """Check if current user is a demo user (backward compatibility)"""
    return not _is_exempt_user() and not _has_active_subscription()

def is_trial_active():
    """Check if trial is currently active (backward compatibility)"""
    if _is_exempt_user() or _has_active_subscription():
        return True
    
    return _get_trial_status_for_unauthenticated()['active']


