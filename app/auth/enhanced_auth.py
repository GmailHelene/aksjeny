from flask import Blueprint, request, jsonify, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets
import re
from functools import wraps
import redis
from ..models import User, LoginAttempt, UserSession
from ..utils.rate_limiter import rate_limit
from ..utils.security import SecurityUtils
from .. import db

enhanced_auth = Blueprint('enhanced_auth', __name__)

class AuthenticationManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(current_app.config.get('REDIS_URL', 'redis://localhost:6379'))
        self.security = SecurityUtils()
        
    def authenticate_user(self, email, password, remember_me=False, request_info=None):
        """Enhanced user authentication with security features"""
        try:
            # Rate limiting check
            if not self._check_rate_limit(email, request_info):
                return {
                    'success': False,
                    'error': 'Too many login attempts. Please try again later.',
                    'locked_until': self._get_lockout_time(email)
                }
            
            # Find user
            user = User.query.filter_by(email=email.lower().strip()).first()
            
            if not user or not check_password_hash(user.password_hash, password):
                self._log_failed_attempt(email, request_info)
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            # Check if account is locked
            if user.is_locked:
                return {
                    'success': False,
                    'error': 'Account is locked. Please contact support.',
                    'account_locked': True
                }
            
            # Check if email is verified
            if not user.email_verified:
                return {
                    'success': False,
                    'error': 'Please verify your email address before logging in.',
                    'email_verification_required': True
                }
            
            # Two-factor authentication check
            if user.two_factor_enabled:
                # Generate 2FA session token
                token = self._generate_2fa_token(user.id)
                return {
                    'success': False,
                    'two_factor_required': True,
                    'token': token
                }
            
            # Successful login
            return self._complete_login(user, remember_me, request_info)
            
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return {
                'success': False,
                'error': 'Authentication service temporarily unavailable'
            }
    
    def verify_two_factor(self, token, code, request_info=None):
        """Verify two-factor authentication code"""
        try:
            user_id = self._verify_2fa_token(token)
            if not user_id:
                return {
                    'success': False,
                    'error': 'Invalid or expired token'
                }
            
            user = db.session.get(User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            if not self.security.verify_totp(user.two_factor_secret, code):
                self._log_failed_2fa_attempt(user.id, request_info)
                return {
                    'success': False,
                    'error': 'Invalid verification code'
                }
            
            # Complete login
            return self._complete_login(user, False, request_info)
            
        except Exception as e:
            current_app.logger.error(f"2FA verification error: {str(e)}")
            return {
                'success': False,
                'error': 'Verification service temporarily unavailable'
            }
    
    def _complete_login(self, user, remember_me, request_info):
        """Complete the login process"""
        try:
            # Update user login info
            user.last_login = datetime.utcnow()
            user.login_count += 1
            
            # Create user session
            session_token = secrets.token_urlsafe(32)
            user_session = UserSession(
                user_id=user.id,
                session_token=session_token,
                ip_address=request_info.get('ip') if request_info else None,
                user_agent=request_info.get('user_agent') if request_info else None,
                expires_at=datetime.utcnow() + timedelta(days=30 if remember_me else 1)
            )
            
            db.session.add(user_session)
            db.session.commit()
            
            # Log successful login
            self._log_successful_login(user.id, request_info)
            
            # Clear failed attempts
            self._clear_failed_attempts(user.email)
            
            # Login user
            login_user(user, remember=remember_me)
            
            return {
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'subscription_level': user.subscription_level,
                    'is_admin': user.is_admin
                },
                'session_token': session_token
            }
            
        except Exception as e:
            current_app.logger.error(f"Login completion error: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'Login completion failed'
            }
    
    def _check_rate_limit(self, email, request_info):
        """Check if user is rate limited"""
        ip = request_info.get('ip') if request_info else 'unknown'
        
        # Check email-based rate limiting (5 attempts per 15 minutes)
        email_key = f"login_attempts:email:{email}"
        if not rate_limit(email_key, max_attempts=5, window=900):
            return False
        
        # Check IP-based rate limiting (10 attempts per 15 minutes)
        ip_key = f"login_attempts:ip:{ip}"
        if not rate_limit(ip_key, max_attempts=10, window=900):
            return False
        
        return True
    
    def _log_failed_attempt(self, email, request_info):
        """Log failed login attempt"""
        try:
            attempt = LoginAttempt(
                email=email,
                ip_address=request_info.get('ip') if request_info else None,
                user_agent=request_info.get('user_agent') if request_info else None,
                success=False,
                timestamp=datetime.utcnow()
            )
            db.session.add(attempt)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to log login attempt: {str(e)}")
    
    def _log_successful_login(self, user_id, request_info):
        """Log successful login"""
        try:
            user = db.session.get(User, user_id)
            attempt = LoginAttempt(
                email=user.email,
                user_id=user_id,
                ip_address=request_info.get('ip') if request_info else None,
                user_agent=request_info.get('user_agent') if request_info else None,
                success=True,
                timestamp=datetime.utcnow()
            )
            db.session.add(attempt)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to log successful login: {str(e)}")
    
    def _generate_2fa_token(self, user_id):
        """Generate 2FA session token"""
        token = secrets.token_urlsafe(32)
        key = f"2fa_token:{token}"
        self.redis_client.setex(key, 300, user_id)  # 5 minute expiry
        return token
    
    def _verify_2fa_token(self, token):
        """Verify 2FA session token"""
        key = f"2fa_token:{token}"
        user_id = self.redis_client.get(key)
        if user_id:
            self.redis_client.delete(key)  # Single use token
            return int(user_id)
        return None
    
    def logout_user_session(self, session_token):
        """Logout user and invalidate session"""
        try:
            user_session = UserSession.query.filter_by(session_token=session_token).first()
            if user_session:
                user_session.is_active = False
                db.session.commit()
            
            logout_user()
            return {'success': True}
            
        except Exception as e:
            current_app.logger.error(f"Logout error: {str(e)}")
            return {'success': False, 'error': 'Logout failed'}

# Authentication decorators
def require_subscription(level='basic'):
    """Decorator to require specific subscription level"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_subscription_level(level):
                return jsonify({
                    'error': 'Premium subscription required',
                    'required_level': level,
                    'current_level': current_user.subscription_level
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_admin():
    """Decorator to require admin access"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_session():
    """Decorator to validate active session"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                session_token = session.get('session_token')
                if session_token:
                    user_session = UserSession.query.filter_by(
                        session_token=session_token,
                        user_id=current_user.id,
                        is_active=True
                    ).first()
                    
                    if not user_session or user_session.expires_at < datetime.utcnow():
                        logout_user()
                        return jsonify({'error': 'Session expired'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_rate_limit(max_requests=60, window=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not rate_limit(request.remote_addr, max_requests, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per {window} seconds'
                }), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Route handlers
@enhanced_auth.route('/login', methods=['POST'])
def enhanced_login():
    """Enhanced login endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember_me = data.get('remember_me', False)
    totp_code = data.get('totp_code')
    two_factor_token = data.get('two_factor_token')
    
    # Input validation
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    request_info = {
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'timestamp': datetime.utcnow()
    }
    
    auth_manager = AuthenticationManager()
    
    # Handle 2FA verification
    if two_factor_token and totp_code:
        result = auth_manager.verify_two_factor(two_factor_token, totp_code, request_info)
    else:
        result = auth_manager.authenticate_user(email, password, remember_me, request_info)
    
    if result['success']:
        session['session_token'] = result['session_token']
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@enhanced_auth.route('/logout', methods=['POST'])
@login_required
def enhanced_logout():
    """Enhanced logout endpoint"""
    session_token = session.get('session_token')
    auth_manager = AuthenticationManager()
    result = auth_manager.logout_user_session(session_token)
    
    session.clear()
    return jsonify(result)

@enhanced_auth.route('/session/validate', methods=['GET'])
@validate_session()
def validate_session_endpoint():
    """Validate current session"""
    if current_user.is_authenticated:
        return jsonify({
            'valid': True,
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'name': current_user.name,
                'subscription_level': current_user.subscription_level
            }
        })
    else:
        return jsonify({'valid': False}), 401
