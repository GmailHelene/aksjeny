from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, login_manager, mail
from app.utils.subscription import subscription_required
from app.utils.access_control import access_required
from ..utils.access_control import access_required, is_demo_user, is_trial_active
from ..utils.i18n_simple import set_language, get_available_languages
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta, time as dt_time
import time
import os
import hashlib
from flask import g
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.extensions import mail
from flask_wtf.csrf import CSRFProtect

# Lazy imports - only import when needed
def get_user_model():
    """Lazily import and return the User model."""
    from app.models.user import User
    return User

def get_data_service():
    """Lazily import and return the DataService class."""
    from app.services.data_service import DataService
    return DataService

def get_referral_service():
    """Lazily import and return the ReferralService class."""
    from app.services.referral_service import ReferralService
    return ReferralService

def get_forms():
    """Lazily import and return all forms used in this module."""
    from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm
    return LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm

def get_performance_monitor():
    """Lazily import and return the performance monitor decorator."""
    try:
        from app.services.performance_monitor import monitor_performance
        return monitor_performance
    except ImportError:
        # Return a dummy decorator if performance monitor is not available
        def dummy_decorator(f):
            return f
        return dummy_decorator

# Lazy import stripe only when needed
def get_stripe():
    """Lazily import and return the Stripe module with error handling."""
    try:
        import stripe
        # Ensure API key is set
        if not stripe.api_key:
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY', 'sk_test_dummy_key_for_development')
        return stripe
    except ImportError:
        current_app.logger.warning("Stripe not available - import failed")
        return None
    except Exception as e:
        current_app.logger.warning(f"Stripe setup failed: {e}")
        return None

def get_pytz():
    """Lazily import and return the pytz module."""
    try:
        import pytz
        return pytz
    except ImportError:
        current_app.logger.warning("pytz not available - import failed")
        return None
main = Blueprint('main', __name__)

EXEMPT_EMAILS = {'helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com'}

# Always accessible endpoints (authentication, basic info, etc.)
EXEMPT_ENDPOINTS = {
    'main.login', 'main.register', 'main.logout', 'main.privacy', 'main.privacy_policy',
    'main.offline', 'main.offline_html', 'static', 'favicon',
    'main.service_worker', 'main.manifest', 'main.version', 'main.contact', 'main.contact_submit',
    'main.subscription', 'main.subscription_plans', 'main.payment_success', 'main.payment_cancel',
    'main.forgot_password', 'main.reset_password', 'main.demo',
    'stocks.index', 'stocks.search', 'analysis.index', 'main.referrals', 'main.send_referral'
}

# Premium features that require subscription after trial
PREMIUM_ENDPOINTS = {
    # Stocks endpoints
    'stocks.details',
    'stocks.list_stocks',
    'stocks.list_oslo',
    'stocks.global_list',
    'stocks.list_crypto',
    'stocks.list_currency',
    'stocks.compare',
    'stocks.list_stocks_by_category',
    
    # Analysis endpoints
    'analysis.ai',
    'analysis.technical',
    'analysis.recommendation',
    'analysis.prediction',
    'analysis.market_overview',
    
    # Portfolio endpoints
    'portfolio.index',
    'portfolio.create_portfolio',
    'portfolio.view_portfolio',
    'portfolio.edit_stock',
    'portfolio.remove_stock',
    'portfolio.add_stock_to_portfolio',
    'portfolio.remove_stock_from_portfolio',
    'portfolio.watchlist',
    'portfolio.stock_tips',
    'portfolio.transactions',
    'portfolio.add_stock',
    'portfolio.overview'
}

def url_is_safe(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def init_stripe():
    """Non-blocking Stripe initialization"""
    try:
        stripe = get_stripe()
        if current_app.config.get('STRIPE_SECRET_KEY'):
            stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
            current_app.logger.info('Stripe initialized successfully')
        else:
            current_app.logger.warning('Stripe not configured - using fallback mode')
    except Exception as e:
        current_app.logger.error(f'Stripe initialization failed: {str(e)}')
        # Don't raise - allow app to continue without Stripe

# Initialize Stripe when the blueprint is registered
@main.record_once
def on_register(state):
    """Initialize Stripe when blueprint is registered - non-blocking"""
    try:
        # Import stripe only when needed and safely
        stripe = __import__('stripe')
        
        # Set Stripe API key with safe fallback
        stripe_key = state.app.config.get('STRIPE_SECRET_KEY', 'sk_test_fallback_key')
        stripe.api_key = stripe_key
        
        # Only test connection in real production and if the key looks valid
        if (state.app.config.get('IS_REAL_PRODUCTION') and 
            stripe_key and 
            (stripe_key.startswith('sk_live') or stripe_key.startswith('sk_test_'))):
            try:
                # Test the connection by making a simple API call in background
                import threading
                def test_stripe():
                    try:
                        stripe.Price.list(limit=1)
                        state.app.logger.info('Stripe connection validated successfully')
                    except Exception as e:
                        state.app.logger.warning(f'Stripe connection test failed: {e}')
                
                # Run test in background thread to avoid blocking startup
                threading.Thread(target=test_stripe, daemon=True).start()
            except Exception as e:
                state.app.logger.warning(f'Could not start Stripe validation thread: {e}')
        
        state.app.logger.info('Stripe initialized (development mode)')
        
    except Exception as e:
        state.app.logger.warning(f'Stripe initialization failed (non-critical): {str(e)}')
        # Don't raise - allow app to continue without Stripe

@main.before_app_request
def restrict_non_subscribed_users():
    """
    LEGACY: This function is being replaced by the new @access_required decorator system.
    Only keeping it for exempt user privilege updates.
    """
    try:
        # Skip if login_manager is not initialized (for testing)
        if not hasattr(current_app, 'login_manager'):
            return
        
        # Only handle exempt user privilege updates now
        # Access control is handled by @access_required decorator
        if current_user.is_authenticated and current_user.email in EXEMPT_EMAILS:
            try:
                if not current_user.has_subscription:
                    current_user.has_subscription = True
                    current_user.subscription_type = 'lifetime'
                    db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Error updating exempt user: {str(e)}")
            return

    except Exception as e:
        current_app.logger.error(f"Error in access restriction: {str(e)}")
        # On error, allow access to prevent breaking the app
        return None

# Device fingerprinting for trial tracking
def get_device_fingerprint(request):
    """Create a device fingerprint based on IP, User-Agent, and Accept headers"""
    components = [
        request.remote_addr,
        request.headers.get('User-Agent', ''),
        request.headers.get('Accept-Language', ''),
        request.headers.get('Accept-Encoding', ''),
        request.headers.get('Accept', ''),
    ]
    fingerprint = hashlib.sha256('|'.join(components).encode()).hexdigest()
    return fingerprint[:16]  # Use first 16 characters for storage efficiency

def track_device_trial(fingerprint):
    """Track trial usage for a device fingerprint"""
    from app.models.user import DeviceTrialTracker
    from app.extensions import db
    
    # Check if device has already used trial
    tracker = DeviceTrialTracker.query.filter_by(device_fingerprint=fingerprint).first()
    if tracker:
        return tracker.trial_start_time, tracker.trial_used
    
    # Create new trial tracker
    now = datetime.utcnow()
    tracker = DeviceTrialTracker(
        device_fingerprint=fingerprint,
        trial_start_time=now,
        trial_used=True
    )
    db.session.add(tracker)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving device trial tracker: {e}")
    
    return now, True

@main.before_app_request
def before_request():
    """Initialize session and handle trial logic before each request"""
    # Skip if login_manager is not initialized (for testing)
    if not hasattr(current_app, 'login_manager'):
        return
    
    # Make sure sessions are permanent for trial tracking
    session.permanent = True
    
    # Store current time for template usage
    g.current_time = int(time.time())
    
    # Ensure login state consistency across all pages
    if current_user.is_authenticated:
        # Update session with current user info for consistency
        session['user_logged_in'] = True
        session['user_id'] = current_user.id
        session['user_email'] = current_user.email
        
        # Make user info available globally for templates
        g.current_user = current_user
        g.user_logged_in = True
        g.user_email = current_user.email
        
        # Ensure exempt users have correct permissions
        if current_user.email in EXEMPT_EMAILS:
            try:
                if not current_user.has_subscription:
                    current_user.has_subscription = True
                    current_user.subscription_type = 'lifetime'
                    current_user.is_admin = True
                    db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Error updating exempt user: {str(e)}")
    else:
        # Clear user session data if not authenticated
        session.pop('user_logged_in', None)
        session.pop('user_id', None)
        session.pop('user_email', None)
        
        # Clear global user info
        g.current_user = None
        g.user_logged_in = False
        g.user_email = None

    # 1. Device fingerprinting and trial tracking
    # DISABLED: Using @trial_required decorator instead for consistent trial logic
    # try:
    #     fingerprint = get_device_fingerprint(request)
    #     session['device_fingerprint'] = fingerprint
    #     
    #     # Track trial usage for the device
    #     trial_start, trial_used = track_device_trial(fingerprint)
    #     session['trial_start_time'] = trial_start.isoformat()
    #     session['trial_used'] = trial_used
    # except Exception as e:
    #     current_app.logger.error(f"Error in device fingerprinting/trial tracking: {str(e)}")
    
    # 2. Restrict access for non-subscribed users
    try:
        restrict_non_subscribed_users()
    except Exception as e:
        current_app.logger.error(f"Error in restrict_non_subscribed_users: {str(e)}")
        # Allow access if there's an error to prevent app from breaking
        return

@main.route('/')
# @access_required
def index():
    """Landing page"""
    # Market open/close info - lazy import pytz
    pytz = get_pytz()
    try:
        if pytz:
            oslo_tz = pytz.timezone('Europe/Oslo')
            now_oslo = datetime.now(oslo_tz)
        else:
            now_oslo = datetime.now()  # Use local time as fallback
        # Oslo Børs: 09:00-16:30 CET/CEST, man-fre
        is_oslo_open = now_oslo.weekday() < 5 and dt_time(9, 0) <= now_oslo.time() <= dt_time(16, 30)
        oslo_status = 'ÅPEN' if is_oslo_open else 'STENGT'
        oslo_open = '09:00'
        oslo_close = '16:30'
        # NYSE: 15:30-22:00 norsk tid (09:30-16:00 ET)
        nyse_open = '15:30'
        nyse_close = '22:00'
        is_nyse_open = now_oslo.weekday() < 5 and dt_time(15, 30) <= now_oslo.time() <= dt_time(22, 0)
        nyse_status = 'ÅPEN' if is_nyse_open else 'STENGT'
    except Exception as e:
        current_app.logger.error(f"Error with timezone handling: {e}")
        # Fallback to basic status
        now_oslo = datetime.now()
        oslo_status = 'STENGT'
        oslo_open = '09:00'
        oslo_close = '16:30'
        nyse_status = 'STENGT'
        nyse_open = '15:30'
        nyse_close = '22:00'
        is_oslo_open = False
        is_nyse_open = False
    try:
        # Lazy import DataService only when needed
        DataService = get_data_service()
        oslo_stocks = DataService.get_oslo_bors_overview() or {}
        global_stocks = DataService.get_global_stocks_overview() or {}
        crypto = DataService.get_crypto_overview() or {}
        currency = DataService.get_currency_overview() or {}
        # Finn siste oppdateringstidspunkt fra en av datakildene (faller tilbake til nå hvis ikke mulig)
        last_updated = None
        if hasattr(oslo_stocks, 'get') and oslo_stocks:
            for stock in oslo_stocks.values():
                if 'last_update' in stock:
                    last_updated = stock['last_update']
                    break
        if not last_updated:
            last_updated = now_oslo.strftime('%d.%m.%Y %H:%M')
    except Exception as e:
        current_app.logger.error(f"Error fetching market data: {str(e)}")
        oslo_stocks = {
            'EQNR.OL': {'name': 'Equinor ASA', 'last_price': 342.55, 'change': 2.30, 'change_percent': 0.68, 'volume': 3200000, 'signal': 'BUY', 'last_update': now_oslo.strftime('%d.%m.%Y %H:%M')},
            'DNB.OL': {'name': 'DNB Bank ASA', 'last_price': 212.80, 'change': -1.20, 'change_percent': -0.56, 'volume': 1500000, 'signal': 'HOLD', 'last_update': now_oslo.strftime('%d.%m.%Y %H:%M')},
            'TEL.OL': {'name': 'Telenor ASA', 'last_price': 125.90, 'change': -2.10, 'change_percent': -1.64, 'volume': 1200000, 'signal': 'SELL', 'last_update': now_oslo.strftime('%d.%m.%Y %H:%M')},
            'YAR.OL': {'name': 'Yara International', 'last_price': 456.20, 'change': 3.80, 'change_percent': 0.84, 'volume': 800000, 'signal': 'BUY', 'last_update': now_oslo.strftime('%d.%m.%Y %H:%M')},
            'NHY.OL': {'name': 'Norsk Hydro ASA', 'last_price': 67.85, 'change': 0.95, 'change_percent': 1.42, 'volume': 2100000, 'signal': 'BUY', 'last_update': now_oslo.strftime('%d.%m.%Y %H:%M')}
        }
        global_stocks = {
            'AAPL': {'name': 'Apple Inc.', 'last_price': 185.70, 'change': 1.23, 'change_percent': 0.67, 'volume': 1000000, 'signal': 'BUY'},
            'MSFT': {'name': 'Microsoft Corp.', 'last_price': 390.20, 'change': 2.10, 'change_percent': 0.54, 'volume': 900000, 'signal': 'BUY'},
            'AMZN': {'name': 'Amazon.com', 'last_price': 178.90, 'change': -0.80, 'change_percent': -0.45, 'volume': 800000, 'signal': 'HOLD'},
            'GOOGL': {'name': 'Alphabet Inc.', 'last_price': 2850.10, 'change': 5.60, 'change_percent': 0.20, 'volume': 700000, 'signal': 'HOLD'},
            'TSLA': {'name': 'Tesla Inc.', 'last_price': 230.10, 'change': -3.50, 'change_percent': -1.50, 'volume': 1200000, 'signal': 'SELL'}
        }
        crypto = {
            'BTC-USD': {'name': 'Bitcoin', 'last_price': 65432.10, 'change': 1200, 'change_percent': 1.87, 'volume': 10000, 'signal': 'BUY'},
            'ETH-USD': {'name': 'Ethereum', 'last_price': 3456.78, 'change': 56.78, 'change_percent': 1.67, 'volume': 8000, 'signal': 'BUY'}
        }
        currency = {
            'USD': {'symbol': 'USD', 'name': 'USD/NOK', 'rate': 10.45, 'change': -0.15, 'change_percent': -1.42, 'last_updated': now_oslo.strftime('%d.%m.%Y %H:%M')}
        }
        last_updated = now_oslo.strftime('%d.%m.%Y %H:%M')
    
    # Since @access_required ensures only users with valid access reach this point,
    # we no longer need to check for restricted access or show trial banners.
    # All users reaching this endpoint have valid access (exempt, subscription, or active trial)
    restricted = False
    show_banner = False
    
    return render_template('index.html',
                         oslo_stocks=oslo_stocks,
                         global_stocks=global_stocks,
                         crypto=crypto,
                         currency=currency,
                         datetime=datetime,
                         oslo_status=oslo_status,
                         oslo_open=oslo_open,
                         oslo_close=oslo_close,
                         nyse_status=nyse_status,
                         nyse_open=nyse_open,
                         nyse_close=nyse_close,
                         last_updated=last_updated,
                         restricted=restricted,
                         show_banner=show_banner)

@main.route('/demo')
def demo():
    """Demo page for non-registered users"""
    return render_template('demo.html')

@main.route('/ai-explained')
def ai_explained():
    """AI explanation page"""
    return render_template('ai_explained.html')

@main.route('/pricing')
@main.route('/pricing/')
def pricing():
    """Pricing page"""
    return render_template('pricing.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Lazy import forms and User model
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    User = get_user_model()
    
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter(
                (User.username == form.username.data) | 
                (User.email == form.username.data)
            ).first()
            
            if user and user.check_password(form.password.data):
                # Ensure exempt users always have correct permissions
                if user.email in EXEMPT_EMAILS:
                    try:
                        user.has_subscription = True
                        user.subscription_type = 'lifetime'
                        user.is_admin = True
                        db.session.commit()
                    except Exception as e:
                        current_app.logger.error(f"Failed to update exempt user permissions: {e}")
                
                # Clear all session data before login to ensure clean state
                session.clear()
                
                # Login user with remember me for persistent login
                login_user(user, remember=True, duration=timedelta(days=30))
                current_app.logger.info(f'User logged in: {user.email}')
                
                # Set session to permanent for proper login persistence
                session.permanent = True
                
                # Set session flags for consistency across all pages
                session['user_logged_in'] = True
                session['user_id'] = user.id
                session['user_email'] = user.email
                
                # Flash login success message that will only show on homepage
                flash('Du er nå logget inn!', 'success')
                
                # Always redirect to home page after login for consistent experience
                response = make_response(redirect(url_for('main.index')))
                
                # Force complete cache refresh to ensure login state updates
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                response.headers['Vary'] = '*'
                response.headers['Clear-Site-Data'] = '"cache"'
                
                # Set secure cookie for login state with immediate expiry to force refresh
                response.set_cookie('user_logged_in', 'true', max_age=30*24*60*60, secure=False, httponly=False, samesite='Lax')
                response.set_cookie('login_refresh', str(datetime.utcnow().timestamp()), max_age=60, secure=False, httponly=False, samesite='Lax')
                
                return response
            else:
                flash('Ugyldig brukernavn eller passord', 'danger')
        else:
            # Handle form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    if 'CSRF' in error:
                        # Don't show CSRF error to user - just log it
                        current_app.logger.warning(f'CSRF token error on login: {error}')
                    else:
                        flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    user_email = current_user.email if current_user.is_authenticated else 'Unknown'
    
    # First logout the user
    if current_user.is_authenticated:
        logout_user()
    
    # Clear all session data completely
    session.clear()
    
    current_app.logger.info(f'User logged out: {user_email}')
    
    # Flash message that will show on homepage
    flash('Du er nå utlogget.', 'success')
    
    # Create response with aggressive cache headers to force page refresh
    response = make_response(redirect(url_for('main.index')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    response.headers['Vary'] = '*'
    response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
    
    # Clear ALL possible authentication cookies more aggressively
    cookie_names = [
        'session', 'remember_token', 'user_logged_in', 'user_session', 'flask_session',
        'trial_start_time', 'trial_used', 'csrf_token', 'remember_me', 'user_id',
        'authentication', 'auth_token', 'login_session'
    ]
    
    for cookie_name in cookie_names:
        # Clear for current domain/path
        response.set_cookie(cookie_name, '', expires=0, max_age=0, path='/', secure=False, httponly=True, samesite='Lax')
        response.set_cookie(cookie_name, '', expires=0, max_age=0, path='/', secure=True, httponly=True, samesite='None')
        response.set_cookie(cookie_name, '', expires=0, max_age=0, path='/', secure=False, httponly=False, samesite='Lax')
        
        # Try different domain variants
        domains_to_try = [None, request.host, f'.{request.host}']
        for domain in domains_to_try:
            try:
                response.set_cookie(cookie_name, '', expires=0, max_age=0, domain=domain, path='/', secure=False, httponly=True, samesite='Lax')
                response.set_cookie(cookie_name, '', expires=0, max_age=0, domain=domain, path='/', secure=True, httponly=True, samesite='None')
            except:
                pass
    
    return response

def unauthorized_handler():
    flash('Du må logge inn for å få tilgang til denne siden.', 'warning')
    return redirect(url_for('main.login', next=request.url))

# Register unauthorized handler
login_manager.unauthorized_handler(unauthorized_handler)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Lazy import forms and models
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    User = get_user_model()
    
    form = RegistrationForm()
    referral_code = request.args.get('ref')
    if referral_code and request.method == 'GET':
        form.referral_code.data = referral_code

    try:
        if request.method == 'POST':
            if form.validate_on_submit():
                existing_user = User.query.filter(
                    (User.email == form.email.data) | 
                    (User.username == form.username.data)
                ).first()
                
                if existing_user:
                    if existing_user.email == form.email.data:
                        flash('E-post er allerede registrert.', 'danger')
                    else:
                        flash('Brukernavn er allerede tatt.', 'danger')
                    return render_template('register.html', form=form)

                user = User(username=form.username.data, email=form.email.data)
                user.set_password(form.password.data)
                user.trial_used = False
                user.trial_start = None
                db.session.add(user)
                
                try:
                    db.session.commit()
                    current_app.logger.info(f'New user registered: {user.email}')
                    
                    # Process referral if provided
                    referral_code = form.referral_code.data or request.args.get('ref')
                    if referral_code:
                        ReferralService = get_referral_service()
                        ReferralService.process_registration_with_referral(user, referral_code)
                        flash('Du har registrert deg med en invitasjonskode!', 'info')
                    
                    flash('Registrering fullført! Du kan nå logge inn med dine opplysninger.', 'success')
                    
                    # Redirect to login page instead of auto-login
                    return redirect(url_for('main.login'))
                    
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f'Feil ved lagring av bruker: {str(e)}')
                    flash('Det oppstod en feil ved lagring av brukeren. Prøv igjen senere.', 'danger')
                    return render_template('register.html', form=form)
            else:
                # Handle form validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        if 'CSRF' in error:
                            # Don't show CSRF error to user - just log it
                            current_app.logger.warning(f'CSRF token error on register: {error}')
                        else:
                            flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    except Exception as e:
        current_app.logger.error(f'Unexpected error in registration route: {str(e)}')
        flash('Det oppstod en uventet feil. Vennligst prøv igjen senere.', 'danger')
        
    return render_template('register.html', form=form)

@main.route('/share-target')
@access_required
def handle_share():
    """Handle content shared to the app"""
    shared_text = request.args.get('text', '')
    shared_url = request.args.get('url', '')
    
    # Hvis delt innhold ser ut som en aksjeticker (f.eks. "AAPL")
    if shared_text and len(shared_text.strip()) < 10 and shared_text.strip().isalpha():
        return redirect(url_for('stocks.details', ticker=shared_text.strip()))
    
    # Ellers, bruk søkefunksjonen
    return redirect(url_for('stocks.search', query=shared_text.strip()))

# Market overview route moved to analysis.py to avoid conflicts

@main.route('/service-worker.js')
def service_worker():
    """Serve the service worker from the root"""
    return current_app.send_static_file('service-worker.js')

@main.route('/manifest.json')
def manifest():
    """Serve the manifest.json file for PWA support"""
    try:
        return send_from_directory('static', 'manifest.json')
    except Exception as e:
        current_app.logger.error(f"Error serving manifest.json: {str(e)}")
        return jsonify({'error': 'Manifest not found'}), 404

@main.route('/version')
def version():
    """Return the current version of the application"""
    try:
        import os
        from datetime import datetime
        version_path = os.path.join(current_app.root_path, '../static/version.txt')
        version = None
        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                version = f.read().strip()
        if not version:
            # Fallback: bruk dagens dato og tid
            version = datetime.utcnow().strftime('%Y%m%d-%H%M')
        return jsonify({'version': version})
    except Exception as e:
        current_app.logger.error(f"Error reading version: {str(e)}")
        from datetime import datetime
        return jsonify({'version': datetime.utcnow().strftime('%Y%m%d-%H%M')})

@main.route('/privacy')
def privacy():
    """Display privacy policy"""
    return render_template('privacy.html')

@main.route('/privacy-policy')
def privacy_policy():
    """Return static privacy policy HTML file (for Google Play)"""
    return current_app.send_static_file('privacy_policy.html')

@main.route('/subscription')
def subscription():
    """Show subscription options"""
    # Subscription siden skal være tilgjengelig for alle
    trial_remaining = None
    subscription_active = False
    
    # Hvis bruker er innlogget, sjekk subscription status
    if current_user.is_authenticated:
        try:
            subscription_active = current_user.has_active_subscription()
            # Don't redirect users with active subscription - let them see the page
            # if subscription_active:
            #     flash('Du har allerede et aktivt abonnement.', 'info')
            #     return redirect(url_for('main.index'))
            trial_remaining = current_user.subscription_days_left()
        except Exception as e:
            current_app.logger.error(f"Error checking subscription status: {str(e)}")
            subscription_active = False
            trial_remaining = None

    # Fallback plans if Stripe is not configured (for testing)
    fallback_plans = [
        {
            'id': 'price_monthly',
            'name': 'Månedlig abonnement',
            'description': 'Full tilgang til alle funksjoner.',
            'price': 99,
            'currency': 'NOK',
            'interval': 'month',
            'features': ['Full tilgang', 'Ingen reklame', 'Premium support']
        }
    ]
    
    try:
        # Check if Stripe is properly configured
        stripe_key = current_app.config.get('STRIPE_SECRET_KEY', '')
        if (not stripe_key or 
            stripe_key.startswith('sk_test_dummy') or 
            not current_app.config.get('IS_REAL_PRODUCTION', False)):
            # Use fallback plans in development/test environment
            return render_template(
                'subscription.html',
                plans=fallback_plans,
                stripe_public_key='pk_test_demo',
                trial_remaining=trial_remaining,
                subscription_active=subscription_active
            )
        
        stripe_public_key = current_app.config.get('STRIPE_PUBLIC_KEY', '')
        
        stripe = get_stripe()
        if not stripe:
            # Stripe not available - use fallback
            return render_template(
                'subscription.html',
                plans=fallback_plans,
                stripe_public_key='',
                trial_remaining=trial_remaining,
                subscription_active=subscription_active
            )
        
        prices = stripe.Price.list(
            active=True,
            limit=3,
            expand=['data.product']
        )

        subscription_plans = []
        for price in prices.data:
            plan = {
                'id': price.id,
                'name': price.product.name,
                'description': price.product.description,
                'price': price.unit_amount / 100,
                'currency': price.currency,
                'interval': price.recurring.interval if price.recurring else 'one_time',
                'features': price.product.metadata.get('features', '').split(',')
            }
            subscription_plans.append(plan)

        return render_template(
            'subscription.html',
            plans=subscription_plans,
            stripe_public_key=stripe_public_key,
            trial_remaining=trial_remaining
        )
    except Exception as e:
        # Log error and show fallback plans
        current_app.logger.error(f'Stripe error in /subscription: {str(e)}')
        return render_template(
            'subscription.html',
            plans=fallback_plans,
            stripe_public_key='',
            trial_remaining=trial_remaining
        )

@main.route('/start-trial', methods=['POST'])
@login_required
def start_trial():
    """Start free trial for the current user"""
    if not current_user.trial_used:
        current_user.start_free_trial()
        db.session.commit()
        flash('Din 10-minutters gratis prøveperiode har startet!', 'success')
    else:
        flash('Du har allerede brukt din gratis prøveperiode.', 'warning')
    
    return redirect(url_for('main.subscription_plans'))

@main.route('/purchase_subscription', methods=['POST'])
@login_required
def purchase_subscription():
    """Handle subscription purchase (dummy implementation)"""
    subscription_type = request.form.get('subscription_type')
    
    # 1. Process payment with a payment provider (Stripe, PayPal, etc.)
    # 2. Verify payment was successful
    # 3. Then update user's subscription status
    
    # For demo purposes, we'll just update the subscription directly
    if subscription_type == 'monthly':
        current_user.has_subscription = True
        current_user.subscription_type = 'monthly'
        current_user.subscription_start = datetime.utcnow()
        current_user.subscription_end = datetime.utcnow() + timedelta(days=30)
        flash('Takk for kjøpet! Du har nå et månedsabonnement.', 'success')
    
    elif subscription_type == 'yearly':
        current_user.has_subscription = True
        current_user.subscription_type = 'yearly'
        current_user.subscription_start = datetime.utcnow()
        current_user.subscription_end = datetime.utcnow() + timedelta(days=365)
        flash('Takk for kjøpet! Du har nå et årsabonnement.', 'success')
    
    elif subscription_type == 'lifetime':
        current_user.has_subscription = True
        current_user.subscription_type = 'lifetime'
        current_user.subscription_start = datetime.utcnow()
        current_user.subscription_end = None
        flash('Takk for kjøpet! Du har nå et livsvarig abonnement.', 'success')
    
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Create a real Stripe checkout session"""
    try:
        # Import Stripe only when needed
        stripe = get_stripe()
        
        # CSRF protection is handled automatically by Flask-WTF for all POST requests
        # No need for manual validation unless we have specific exemptions
        
        # Log the request details for debugging
        current_app.logger.info(f'Create checkout session request from user: {current_user.email}')
        current_app.logger.info(f'Form data: {dict(request.form)}')
        current_app.logger.info(f'Headers: {dict(request.headers)}')
        
        # Get subscription type from form
        subscription_type = request.form.get('subscription_type')
        price_id = request.form.get('price_id')
        use_referral_discount = request.form.get('use_referral_discount') == '1'
        
        # Map subscription type to price_id if not provided directly
        if not price_id and subscription_type:
            if subscription_type == 'monthly':
                price_id = current_app.config.get('STRIPE_MONTHLY_PRICE_ID', 'price_monthly_default')
            elif subscription_type == 'yearly':
                price_id = current_app.config.get('STRIPE_YEARLY_PRICE_ID', 'price_yearly_default')
            elif subscription_type == 'lifetime':
                price_id = current_app.config.get('STRIPE_LIFETIME_PRICE_ID', 'price_lifetime_default')
        
        if not price_id:
            flash('Ingen pris-ID oppgitt. Vennligst prøv igjen.', 'danger')
            return redirect(url_for('main.subscription'))
        
        # Create or get customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={'user_id': current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()
        
        # Determine mode based on subscription type
        mode = 'payment' if subscription_type == 'lifetime' else 'subscription'
        
        # Check for referral discount (only for yearly subscriptions)
        discounts = []
        if use_referral_discount and subscription_type == 'yearly' and current_user.has_referral_discount():
            # Apply 20% discount for referral
            try:
                # Create a Stripe coupon for the referral discount
                coupon = stripe.Coupon.create(
                    percent_off=20,
                    duration='once',
                    name=f'Referral Discount 20% - User {current_user.id}',
                    metadata={'user_id': current_user.id, 'referral_discount': 'true'}
                )
                discounts = [{'coupon': coupon.id}]
                
                # Log successful coupon creation
                current_app.logger.info(f'Created referral discount coupon {coupon.id} for user {current_user.id}')
                
            except stripe.error.StripeError as e:
                current_app.logger.error(f'Failed to create referral coupon: {str(e)}')
                # If coupon creation fails, continue without discount
                flash('Kunne ikke anvende referral-rabatt. Fortsetter uten rabatt.', 'warning')
                use_referral_discount = False
        
        # Create checkout session (production-ready)
        session_params = {
            'customer': current_user.stripe_customer_id,
            'payment_method_types': ['card'],
            'line_items': [{
                'price': price_id,
                'quantity': 1
            }],
            'mode': mode,
            'success_url': url_for('main.payment_success', _external=True),
            'cancel_url': url_for('main.payment_cancel', _external=True),
            'metadata': {
                'user_id': current_user.id,
                'subscription_type': subscription_type,
                'referral_discount_used': str(use_referral_discount)
            }
        }
        
        if discounts:
            session_params['discounts'] = discounts
        
        session = stripe.checkout.Session.create(**session_params)
        return redirect(session.url, code=303)
        
    except stripe.error.StripeError as e:
        current_app.logger.error(f'Stripe error: {str(e)}')
        flash('Det oppstod en feil med Stripe. Prøv igjen senere.', 'danger')
        return redirect(url_for('main.subscription'))
    except Exception as e:
        current_app.logger.error(f'Error creating checkout session: {str(e)}')
        flash('Det oppstod en uventet feil. Prøv igjen senere.', 'danger')
        return redirect(url_for('main.subscription'))

@main.route('/subscribe/<plan>')
@login_required
def subscribe(plan):
    if plan not in ['monthly', 'yearly']:
        flash('Ugyldig abonnementstype', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        # Import stripe only when needed
        stripe = get_stripe()
        
        # Get or create customer
        if not current_user.stripe_customer_id:
            try:
                customer = stripe.Customer.create(
                    email=current_user.email,
                    metadata={"user_id": current_user.id}
                )
                current_user.stripe_customer_id = customer.id
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f'Error creating Stripe customer: {str(e)}')
                flash('Det oppstod en feil under opprettelse av kundenummer. Vennligst prøv igjen.', 'danger')
                return redirect(url_for('main.index'))

        # Get price ID based on plan
        price_id = current_app.config[f'STRIPE_{plan.upper()}_PRICE_ID']
        
        try:
            session = stripe.checkout.Session.create(
                customer=current_user.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=url_for('main.payment_success', _external=True),
                cancel_url=url_for('main.payment_cancel', _external=True),
            )
            return redirect(session.url, code=303)
        
        except Exception as e:
            current_app.logger.error(f'Error creating checkout session: {str(e)}')
            flash('Det oppstod en feil under opprettelse av betalingssiden. Vennligst prøv igjen.', 'danger')
            return redirect(url_for('main.index'))
            
    except Exception as e:
        current_app.logger.error(f'Error in subscription route: {str(e)}')
        flash('Det oppstod en uventet feil. Vennligst prøv igjen senere.', 'danger')
        return redirect(url_for('main.index'))

@main.route('/payment/success')
@login_required
def payment_success():
    flash('Takk for kjøpet! Du har nå full tilgang til Aksjeradar.', 'success')
    return redirect(url_for('main.index'))

@main.route('/payment/cancel')
@login_required
def payment_cancel():
    flash('Betalingen ble avbrutt.', 'info')
    return redirect(url_for('main.index'))

@main.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle real Stripe webhook events"""
    # Import stripe only when needed
    stripe = get_stripe()
    
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, current_app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    if event.type == 'checkout.session.completed':
        session = event.data.object
        handle_successful_subscription(session)
    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        handle_subscription_update(subscription)
    elif event.type == 'customer.subscription.deleted':
        subscription = event.data.object
        handle_subscription_deleted(subscription)

    return jsonify({'status': 'success'})

def handle_successful_subscription(session):
    """Handle successful subscription checkout"""
    try:
        User = get_user_model()
        ReferralService = get_referral_service()
        
        user_id = int(session.metadata.get('user_id'))
        subscription_type = session.metadata.get('subscription_type')
        referral_discount_used = session.metadata.get('referral_discount_used') == 'True'
        
        user = User.query.get(user_id)
        if not user:
            current_app.logger.error(f'User not found: {user_id}')
            return

        # Handle subscription logic
        if subscription_type == 'lifetime':
            user.has_subscription = True
            user.subscription_type = 'lifetime'
            user.subscription_start = datetime.utcnow()
            user.subscription_end = datetime.utcnow() + timedelta(days=36500)  # 100 years
        else:
            stripe = get_stripe()
            subscription = stripe.Subscription.retrieve(session.subscription)
            user.has_subscription = True
            user.subscription_type = subscription_type or subscription.plan.interval
            user.subscription_start = datetime.fromtimestamp(subscription.current_period_start)
            user.subscription_end = datetime.fromtimestamp(subscription.current_period_end)
        
        # Complete referral if user was referred
        ReferralService.complete_referral(user_id)
        
        # Apply referral discount if used
        if referral_discount_used and subscription_type == 'yearly':
            ReferralService.use_referral_discount(user_id)
            current_app.logger.info(f'Referral discount applied for user {user_id}')
        
        db.session.commit()
        current_app.logger.info(f'Subscription activated for user {user_id}')
        
    except Exception as e:
        current_app.logger.error(f'Error handling subscription: {str(e)}')
        db.session.rollback()

def handle_subscription_update(subscription):
    """Handle subscription updates"""
    try:
        User = get_user_model()
        customer_id = subscription.customer
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        
        if not user:
            current_app.logger.error(f'User not found for Stripe customer: {customer_id}')
            return
        
        # Update subscription status
        user.has_subscription = subscription.status == 'active'
        if subscription.status == 'active':
            if subscription.cancel_at:
                user.subscription_end = datetime.fromtimestamp(subscription.cancel_at)
            elif subscription.current_period_end:
                user.subscription_end = datetime.fromtimestamp(subscription.current_period_end)
        
        db.session.commit()
        current_app.logger.info(f'Subscription updated for user {user.id}')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Failed to update subscription: {str(e)}')
        raise

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        User = get_user_model()
        customer_id = subscription.customer
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        
        if not user:
            current_app.logger.error(f'User not found for Stripe customer: {customer_id}')
            return
        
        # Update user subscription status
        user.has_subscription = False
        user.subscription_end = datetime.utcnow()
        
        db.session.commit()
        current_app.logger.info(f'Subscription cancelled for user {user.id}')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Failed to cancel subscription: {str(e)}')
        raise

@main.route('/trial-expired')
def trial_expired():
    try:
        # Get the subscription plans from the config
        monthly_plan = {
            'id': 'monthly',
            'name': 'Månedlig abonnement',
            'price': '99',
            'period': 'mnd',
            'features': [
                'Full tilgang til alle analyser',
                'Porteføljeovervåking',
                'Varsling på kurs og volum',
                'Avanserte analyseverktøy',
                'Ingen bindingstid'
            ]
        }
        
        yearly_plan = {
            'id': 'yearly',
            'name': 'Årlig abonnement',
            'price': '2499',
            'period': 'år',
            'discount': '33%',
            'features': [
                'Alt i månedlig abonnement',
                'To måneder gratis',
                'Prioritert support',
                'Eksklusive rapporter',
                'Beta-testing av nye funksjoner'
            ]
        }
        
        return render_template(
            'trial-expired.html',
            monthly_plan=monthly_plan,
            yearly_plan=yearly_plan
        )
    except Exception as e:
        current_app.logger.error(f'Error in trial-expired route: {str(e)}')
        # Return a simplified version if there's an error
        return render_template(
            'trial-expired.html',
            error=True
        )

@main.route('/contact', methods=['GET'])
def contact():
    """Show contact page"""
    return render_template('contact.html')

@main.route('/contact/submit', methods=['POST'])
def contact_submit():
    """Handle contact form submission"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not all([name, email, subject, message]):
            flash('Alle felt må fylles ut.', 'danger')
            return redirect(url_for('main.contact'))
        
        # Log the contact request
        current_app.logger.info(f'Contact form submission from {name} ({email})')
        
        # Here you would typically send an email or store in database
        # For now we'll just log it
        current_app.logger.info(f'Subject: {subject}\nMessage: {message}')
        
        flash('Takk for din henvendelse! Vi vil svare så snart som mulig.', 'success')
        return redirect(url_for('main.contact'))
        
    except Exception as e:
        current_app.logger.error(f'Error processing contact form: {str(e)}')
        flash('Beklager, det oppstod en feil. Prøv igjen senere.', 'danger')
        return redirect(url_for('main.contact'))


@main.route('/api/oslo_stocks')
@access_required
def get_oslo_stocks():
    try:
        DataService = get_data_service()
        data = DataService.get_oslo_bors_overview()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/global_stocks')
@access_required
def get_global_stocks():
    try:
        DataService = get_data_service()
        data = DataService.get_global_stocks_overview()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# API endpoint for real-time price data
@main.route('/api/realtime/price/<ticker>')
@access_required
def api_realtime_price(ticker):
    """API endpoint for real-time stock price data"""
    try:
        # Get stock data from DataService
        DataService = get_data_service()
        stock_info = DataService.get_stock_info(ticker)
        
        if not stock_info:
            return jsonify({'error': 'Stock not found'}), 404
            
        # Return price data
        return jsonify({
            'ticker': ticker,
            'price': stock_info.get('current_price', 0),
            'change': stock_info.get('change', 0),
            'change_percent': stock_info.get('change_percent', 0),
            'volume': stock_info.get('volume', 0),
            'last_updated': stock_info.get('last_updated', ''),
            'status': 'success'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching realtime price for {ticker}: {str(e)}")
        return jsonify({'error': 'Failed to fetch price data'}), 500

@main.route('/api/realtime/batch-updates', methods=['POST'])
@access_required
def batch_updates():
    """Handle batch real-time updates for multiple tickers"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        
        if not tickers:
            return jsonify({'success': False, 'error': 'No tickers provided'}), 400
        
        # Import DataService
        DataService = get_data_service()
        
        updates = {}
        for ticker in tickers[:10]:  # Limit to 10 tickers per request
            try:
                stock_info = DataService.get_stock_info(ticker)
                if stock_info:
                    updates[ticker] = {
                        'current_price': stock_info.get('current_price', 0),
                        'change': stock_info.get('change', 0),
                        'change_percent': stock_info.get('change_percent', 0),
                        'volume': stock_info.get('volume', 0),
                        'last_updated': stock_info.get('last_updated', '')
                    }
            except Exception as e:
                current_app.logger.error(f"Error fetching data for {ticker}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'updates': updates
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in batch updates: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@main.route('/offline')
def offline():
    """Show offline page"""
    return render_template('offline.html')

@main.route('/currency')
@access_required
def currency():
    """Show actual currency rates page"""
    try:
        DataService = get_data_service()
        currency = DataService.get_currency_overview() or {}
    except Exception as e:
        current_app.logger.error(f"Error fetching currency data: {str(e)}")
        currency = {}
    return render_template('currency.html', currency=currency)

@main.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add stock to user's watchlist"""
    try:
        # Check if user is logged in for API endpoints
        if not current_user.is_authenticated:
            return jsonify({'error': 'Du må logge inn for å legge til favoritter.', 'redirect': '/login'}), 401
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        if not data or 'ticker' not in data:
            return jsonify({'error': 'Ticker er påkrevd'}), 400
        
        ticker = data['ticker'].upper()
        
        # Import here to avoid circular imports
        from app.models.watchlist import Watchlist, WatchlistStock
        from app.extensions import db
        
        # Find or create user's watchlist
        watchlist = Watchlist.query.filter_by(user_id=current_user.id).first()
        if not watchlist:
            watchlist = Watchlist(name="Min favorittliste", user_id=current_user.id)
            db.session.add(watchlist)
            db.session.commit()
        
        # Check if stock already exists in watchlist
        existing = WatchlistStock.query.filter_by(watchlist_id=watchlist.id, ticker=ticker).first()
        if existing:
            return jsonify({'error': f'{ticker} er allerede i favorittlisten'}), 400
        
        # Add stock to watchlist
        watchlist_stock = WatchlistStock(watchlist_id=watchlist.id, ticker=ticker)
        db.session.add(watchlist_stock)
        db.session.commit()
        
        return jsonify({'message': f'{ticker} lagt til i favoritter', 'ticker': ticker})
    except Exception as e:
        current_app.logger.error(f"Error adding to watchlist: {str(e)}")
        return jsonify({'error': 'Kunne ikke legge til i favoritter'}), 500

@main.route('/api/portfolio/add', methods=['POST'])
def add_to_portfolio():
    """Add stock to user's portfolio"""
    try:
        # Check if user is logged in for API endpoints
        if not current_user.is_authenticated:
            return jsonify({'error': 'Du må logge inn for å legge til i portefølje.', 'redirect': '/login'}), 401
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        if not data or 'ticker' not in data:
            return jsonify({'error': 'Ticker er påkrevd'}), 400
        
        ticker = data['ticker'].upper()
        quantity = float(data.get('quantity', 1))
        
        # Import here to avoid circular imports
        from app.models.portfolio import Portfolio, PortfolioStock
        from app.extensions import db
        
        # Validate stock exists
        DataService = get_data_service()
        stock_info = DataService.get_stock_info(ticker)
        if not stock_info:
            return jsonify({'error': f'Aksje {ticker} ble ikke funnet'}), 404
        
        # Find or create user's portfolio
        portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
        if not portfolio:
            portfolio = Portfolio(name="Min portefølje", user_id=current_user.id)
            db.session.add(portfolio)
            db.session.commit()
        
        # Check if stock already exists in portfolio
        existing_stock = PortfolioStock.query.filter_by(portfolio_id=portfolio.id, ticker=ticker).first()
        
        price = stock_info.get('last_price') or stock_info.get('regularMarketPrice') or 100.0
        
        if existing_stock:
            # Update existing stock
            existing_stock.shares += quantity
            message = f'{ticker} oppdatert i portefølje (nå {existing_stock.shares} aksjer)'
        else:
            # Add new stock
            portfolio_stock = PortfolioStock(
                portfolio_id=portfolio.id,
                ticker=ticker,
                shares=quantity,
                purchase_price=price
            )
            db.session.add(portfolio_stock)
            message = f'{ticker} lagt til i portefølje'
        
        db.session.commit()
        return jsonify({'message': message, 'ticker': ticker})
    except Exception as e:
        current_app.logger.error(f"Error adding to portfolio: {str(e)}")
        return jsonify({'error': 'Kunne ikke legge til i portefølje'}), 500


@main.route('/offline.html')
def offline_html():
    """Serve offline page"""
    return send_from_directory('static', 'offline.html')

@main.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory('static/icons', 'favicon.ico', mimetype='image/x-icon')


@main.route('/restricted_access.html')
@main.route('/restricted_access')
def restricted_access():
    """Legacy restricted access route - redirect to demo page per new access control system"""
    return redirect(url_for('main.demo', source='legacy_redirect'))


@main.route('/prediction')
@access_required
def prediction():
    """Redirect to analysis prediction page"""
    return redirect(url_for('analysis.prediction'))

def generate_reset_token(user, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user.email, salt='password-reset-salt')

def verify_reset_token(token, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
    except Exception:
        return None
    User = get_user_model()
    return User.query.filter_by(email=email).first()

@main.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    # Lazy import forms and models
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    User = get_user_model()
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user)
            reset_url = url_for('main.reset_password', token=token, _external=True)
            msg = Message('Tilbakestill passord for Aksjeradar',
                          recipients=[user.email])
            msg.body = f'Klikk på denne lenken for å tilbakestille passordet ditt:\n{reset_url}\n\nHvis du ikke ba om dette, kan du se bort fra denne e-posten.'
            try:
                mail.send(msg)
                flash('En e-post med instruksjoner for tilbakestilling av passord er sendt.', 'info')
            except Exception as e:
                current_app.logger.error(f"Feil ved sending av e-post: {str(e)}")
                flash(f'Kunne ikke sende e-post. Kontakt support. Feil: {str(e)}', 'danger')
        else:
            flash('Ingen bruker funnet med denne e-posten.', 'warning')
        return redirect(url_for('main.forgot_password'))
    return render_template('forgot_password.html', form=form)

@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Lazy import forms
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    
    user = verify_reset_token(token)
    form = ResetPasswordForm()
    if not user:
        flash('Ugyldig eller utløpt lenke for tilbakestilling av passord.', 'danger')
        return redirect(url_for('main.login'))
    if form.validate_on_submit():
        password = form.password.data
        user.set_password(password)
        db.session.commit()
        flash('Passordet er oppdatert. Du kan nå logge inn.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form, token=token)

@main.route('/pwa-test')
@access_required
def pwa_test():
    """PWA functionality test page"""
    return render_template('pwa_test.html')

@main.route('/admin/create-exempt-users')
def create_exempt_users():
    """Admin route to create exempt users - should be removed in production"""
    try:
        from datetime import datetime
        User = get_user_model()
        
        exempt_emails = ['helene@luxushair.com', 'helene721@gmail.com']
        created_users = []
        
        for email in exempt_emails:
            # Delete existing user if exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                db.session.delete(existing_user)
                flash(f'Deleted existing user: {email}', 'info')
            
            # Create new user
            username = email.split('@')[0]
            user = User(
                username=username,
                email=email,
                has_subscription=True,
                subscription_type='lifetime',
                subscription_start=datetime.utcnow(),
                subscription_end=None,
                is_admin=True
            )
            user.set_password('aksjeradar2024')
            db.session.add(user)
            created_users.append(email)
        
        db.session.commit()
        
        flash(f'Successfully created users: {", ".join(created_users)}', 'success')
        flash('All users have password: aksjeradar2024', 'info')
        return redirect(url_for('main.login'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating users: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@main.route('/debug/reset-session')
def reset_session():
    """Reset session og cookies for debugging"""
    # Only allow in debug mode
    if not current_app.config.get('DEBUG', False):
        flash('Debug routes are disabled in production mode.', 'warning')
        return redirect(url_for('main.index'))
    try:
        # Clear all session data
        session.clear()
        
        # Create response to clear cookies
        response = make_response(redirect(url_for('main.index')))
        
        # Clear all relevant cookies
        response.set_cookie('trial_start', '', expires=0)
        response.set_cookie('session', '', expires=0)
        response.set_cookie('csrf_token', '', expires=0)
        
        # Clear any trial-related session keys
        for key in list(session.keys()):
            if 'trial' in key.lower():
                session.pop(key, None)
        
        flash('Session og cookies er tilbakestilt. Prøv igjen.', 'info')
        return response
    except Exception as e:
        flash(f'Feil ved tilbakestilling: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@main.route('/debug/status')
def debug_status():
    """Vis debug-informasjon om session og tilgang"""
    # Only allow in debug mode
    if not current_app.config.get('DEBUG', False):
        flash('Debug routes are disabled in production mode.', 'warning')
        return redirect(url_for('main.index'))
    try:
        info = {
            'current_user_authenticated': current_user.is_authenticated,
            'current_user_email': current_user.email if current_user.is_authenticated else 'Not logged in',
            'session_keys': list(session.keys()),
            'trial_start_time': session.get('trial_start_time'),
            'request_endpoint': request.endpoint,
            'is_exempt': request.endpoint in EXEMPT_ENDPOINTS if request.endpoint else False,
            'is_premium': request.endpoint in PREMIUM_ENDPOINTS if request.endpoint else False,
        }
        
        # Check trial status
        if 'trial_start_time' in session:
            try:
                trial_start = datetime.fromisoformat(session['trial_start_time'])
                trial_remaining = timedelta(minutes=10) - (datetime.utcnow() - trial_start)
                info['trial_remaining_seconds'] = trial_remaining.total_seconds()
                info['trial_expired'] = trial_remaining.total_seconds() <= 0
            except Exception as e:
                info['trial_error'] = str(e)
        
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/test-email')
def test_email():
    """Test email functionality - should be removed in production"""
    from flask_mail import Message
    try:
        msg = Message(
            'Test e-post fra Aksjeradar',
            recipients=['test@example.com']  # Change to a real email for testing
        )
        msg.body = 'Dette er en test-e-post for å sjekke at e-postsystemet fungerer.'
        mail.send(msg)
        flash('Test-e-post sendt!', 'success')
    except Exception as e:
        flash(f'Feil ved sending av e-post: {str(e)}', 'danger')
        current_app.logger.error(f"Email test error: {str(e)}")
    
    return redirect(url_for('main.index'))

@main.route('/admin/user-management')
def admin_user_management():
    """Admin page for user management - should be protected in production"""
    User = get_user_model()
    users = User.query.all()
    return render_template('admin/user_management.html', users=users)

@main.route('/admin/reset-user/<int:user_id>')
def admin_reset_user(user_id):
    """Reset user's trial and subscription status"""
    User = get_user_model()
    user = User.query.get_or_404(user_id)
    user.trial_used = False
    user.trial_start = None
    user.has_subscription = False
    user.subscription_type = 'free'
    user.subscription_start = None
    user.subscription_end = None
    db.session.commit()
    flash(f'Bruker {user.username} er tilbakestilt.', 'success')
    return redirect(url_for('main.admin_user_management'))

@main.route('/check-trial')
def check_trial():
    """Debug route to check trial status"""
    trial_info = {}
    
    # Session-based trial info
    if 'trial_start_time' in session:
        trial_start = datetime.fromisoformat(session['trial_start_time'])
        time_remaining = timedelta(minutes=10) - (datetime.utcnow() - trial_start)
        trial_info['session_trial_start'] = trial_start.isoformat()
        trial_info['session_time_remaining'] = str(time_remaining)
    else:
        trial_info['session_trial_start'] = 'Not started'
    
    # Device fingerprint trial info
    try:
        from app.models.trial_session import TrialSession
        ip_address = request.remote_addr or '127.0.0.1'
        user_agent = request.headers.get('User-Agent', '')
        fingerprint = TrialSession.create_device_fingerprint(ip_address, user_agent)
        trial_session = TrialSession.query.filter_by(device_fingerprint=fingerprint).first()
        
        if trial_session:
            trial_info['device_trial_start'] = trial_session.trial_start.isoformat()
            trial_info['device_trial_active'] = trial_session.is_trial_active()
            time_elapsed = datetime.utcnow() - trial_session.trial_start
            trial_info['device_time_elapsed'] = str(time_elapsed)
        else:
            trial_info['device_trial_start'] = 'Not found'
    except Exception as e:
        trial_info['device_error'] = str(e)
    
    # User subscription info
    if current_user.is_authenticated:
        trial_info['user_has_subscription'] = getattr(current_user, 'has_subscription', False)
        trial_info['user_subscription_type'] = getattr(current_user, 'subscription_type', 'free')
        trial_info['user_trial_used'] = getattr(current_user, 'trial_used', False)
        if hasattr(current_user, 'trial_start') and current_user.trial_start:
            trial_info['user_trial_start'] = current_user.trial_start.isoformat()
    else:
        trial_info['user_status'] = 'Not authenticated'
    
    return jsonify(trial_info)

@main.route('/admin/clean-trials')
def admin_clean_trials():
    """Clean up expired trial sessions"""
    try:
        from app.models.trial_session import TrialSession
        expired_sessions = TrialSession.query.filter(
            TrialSession.trial_start < datetime.utcnow() - timedelta(days=1)
        ).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            db.session.delete(session)
        
        db.session.commit()
        flash(f'Slettet {count} utløpte trial-sesjoner.', 'success')
    except Exception as e:
        flash(f'Feil ved sletting av trial-sesjoner: {str(e)}', 'danger')
    
    return redirect(url_for('main.admin_user_management'))

@main.route('/debug/user-info')
def debug_user_info():
    """Debug route to check user and trial status"""
    # Only allow in debug mode
    if not current_app.config.get('DEBUG', False):
        flash('Debug routes are disabled in production mode.', 'warning')
        return redirect(url_for('main.index'))
        
    from app.models.trial_session import TrialSession
    from app.utils.access_control import get_trial_time_remaining
    
    info = {
        'timestamp': datetime.utcnow().isoformat(),
        'user_authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'user_email': current_user.email if current_user.is_authenticated else None,
        'user_username': current_user.username if current_user.is_authenticated else None,
        'has_subscription': current_user.has_active_subscription() if current_user.is_authenticated else False,
        'subscription_type': current_user.subscription_type if current_user.is_authenticated else None,
        'is_in_trial': current_user.is_in_trial_period() if current_user.is_authenticated else False,
        'trial_start': current_user.trial_start.isoformat() if current_user.is_authenticated and current_user.trial_start else None,
        'session_keys': ['***HIDDEN***'],  # Hide session keys for security
        'session_trial_start': '***HIDDEN***' if session.get('trial_start_time') else None,  # Hide sensitive data
        'cookie_trial_start': '***HIDDEN***' if request.cookies.get('trial_start_time') else None,  # Hide sensitive data
        'trial_time_remaining': get_trial_time_remaining(),
        'request_endpoint': request.endpoint,
        'user_agent': request.headers.get('User-Agent', '')[:50] + '...',  # Truncate user agent
        'ip_address': request.remote_addr,
    }
    
    # Check trial session from database
    try:
        ip_address = request.remote_addr or '127.0.0.1'
        user_agent = request.headers.get('User-Agent', '')
        trial_session = TrialSession.get_or_create_session(ip_address, user_agent)
        info['db_trial_session'] = {
            'id': trial_session.id,
            'fingerprint': trial_session.device_fingerprint[:16] + '...',
            'trial_start': trial_session.trial_start.isoformat(),
            'last_accessed': trial_session.last_accessed.isoformat(),
            'is_expired': trial_session.is_expired,
            'is_active': trial_session.is_trial_active()
        }
    except Exception as e:
        info['db_trial_session_error'] = str(e)
    
    return jsonify(info)

# ========== REFERRAL ROUTES ==========

@main.route('/referrals')
@login_required
@access_required
def referrals():
    """Referral dashboard for logged-in users"""
    try:
        # Lazy import ReferralService
        ReferralService = get_referral_service()
        
        # Get user's referral code
        referral_code = current_user.get_referral_code()
        
        # Get referral statistics
        stats = ReferralService.get_referral_stats(current_user.id)
        
        # Get available discounts
        available_discounts = current_user.get_available_referral_discounts()
        valid_discounts = [d for d in available_discounts if d.is_valid()]
        
        return render_template('referrals.html', 
                             referral_code=referral_code,
                             stats=stats,
                             available_discounts=valid_discounts)
    except Exception as e:
        current_app.logger.error(f'Error in referrals route: {e}')
        flash('Det oppstod en feil ved lasting av referral-siden.', 'error')
        return redirect(url_for('main.index'))


@main.route('/send-referral', methods=['POST'])
@login_required
@access_required
def send_referral():
    """Send referral invitation"""
    # Lazy import forms and services
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    ReferralService = get_referral_service()
    
    form = ReferralForm()
    
    if form.validate_on_submit():
        success, message = ReferralService.create_referral(
            current_user.id, 
            form.email.data
        )
        
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
    else:
        flash('Ugyldig e-postadresse.', 'error')
    
    return redirect(url_for('main.referrals'))


@main.route('/api/user/referral-code')
@login_required
@access_required
def get_user_referral_code():
    """API endpoint to get current user's referral code"""
    try:
        referral_code = current_user.get_referral_code()
        return jsonify({
            'success': True,
            'referral_code': referral_code
        })
    except Exception as e:
        current_app.logger.error(f'Error getting referral code: {e}')
        return jsonify({
            'success': False,
            'error': 'Kunne ikke hente referral-kode'
        }), 500

@main.route('/debug/test-reset')
def debug_test_reset():
    """Debug endpoint to test password reset functionality"""
    # Only allow in debug mode
    if not current_app.config.get('DEBUG', False):
        flash('Debug routes are disabled in production mode.', 'warning')
        return redirect(url_for('main.index'))
    try:
        # Find test user
        User = get_user_model()
        user = User.query.filter_by(email="helene721@gmail.com").first()
        if not user:
            return f"User not found", 404
        
        # Generate reset token  
        token = generate_reset_token(user)
        reset_url = url_for('main.reset_password', token=token, _external=True)
        
        return f"""
        <h2>Password Reset Debug</h2>
        <p>User: {user.email}</p>
        <p>Token: {token}</p>
        <p>Reset URL: <a href="{reset_url}">{reset_url}</a></p>
        <p>Click the link above to test the reset functionality</p>
        """
    except Exception as e:
            return f"User not found", 400

@main.route('/profile')
@login_required
@access_required
def profile():
    """User profile page with referral system"""
    try:
        # Get user's referral code
        referral_code = current_user.referral_code if hasattr(current_user, 'referral_code') else None
        
        # Get referral statistics
        referrals_made = 0
        referral_earnings = 0
        
        if hasattr(current_user, 'referrals'):
            referrals_made = len(current_user.referrals)
            # Calculate potential earnings (20% discount per successful referral)
            successful_referrals = sum(1 for ref in current_user.referrals if hasattr(ref, 'referred_user') and ref.referred_user.has_subscription)
            referral_earnings = successful_referrals * 20  # 20% discount per referral
        
        return render_template('profile.html', 
                             referral_code=referral_code,
                             referrals_made=referrals_made,
                             referral_earnings=referral_earnings)
    except Exception as e:
        current_app.logger.error(f"Error loading profile: {str(e)}")
        flash('Feil ved lasting av profil.', 'danger')
        return redirect(url_for('main.index'))

@main.route('/invite-friend', methods=['POST'])
@login_required
@access_required
def invite_friend():
    """Send invitation email to friend"""
    try:
        email = request.form.get('email')
        if not email:
            flash('E-postadresse er påkrevd.', 'danger')
            return redirect(url_for('main.profile'))
        
        # Generate referral link
        referral_code = current_user.referral_code if hasattr(current_user, 'referral_code') else current_user.username
        referral_link = url_for('main.register', ref=referral_code, _external=True)
        
        # Here you would normally send an email
        # For now, we'll just show a success message with the link
        flash(f'Invitasjon klar! Del denne lenken med {email}: {referral_link}', 'success')
        
        return redirect(url_for('main.profile'))
    except Exception as e:
        current_app.logger.error(f"Error sending invitation: {str(e)}")
        flash('Feil ved sending av invitasjon.', 'danger')
        return redirect(url_for('main.profile'))

# Debug route for testing CSRF tokens - DISABLED FOR SECURITY
@main.route('/debug/csrf', methods=['GET', 'POST'])
@login_required
def debug_csrf():
    """Debug endpoint to test CSRF tokens"""
    # Only allow in debug mode
    if not current_app.config.get('DEBUG', False):
        flash('Debug routes are disabled in production mode.', 'warning')
        return redirect(url_for('main.index'))
        
    from flask_wtf.csrf import generate_csrf
    
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        current_app.logger.info(f'CSRF token received: {csrf_token[:10]}...')  # Only log first 10 chars

        flash('CSRF token validation successful', 'info')
        return redirect(url_for('main.debug_csrf'))
    
    current_token = generate_csrf()
    current_app.logger.info(f'Generated CSRF token: {current_token[:10]}...')  # Only log first 10 chars
    
    return f"""
    <h1>CSRF Debug</h1>
    <p>Current user: {current_user.email}</p>
    <p>Token generated successfully (hidden for security)</p>
    <form method="post">
        <input type="hidden" name="csrf_token" value="{current_token}">
        <button type="submit">Test CSRF</button>
    </form>
    <a href="/">Back to home</a>
    """

# ========== FIXED DEMO ROUTES ==========
# Demo/test routes for development and QA

@main.route('/demo/ping')
def demo_ping():
    """Simple ping route for health checks"""
    return jsonify({'status': 'ok', 'message': 'pong'})

@main.route('/demo/echo', methods=['GET', 'POST'])
def demo_echo():
    """Echoes back posted data for testing"""
    if request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        return jsonify({'received': data})
    return render_template('demo_echo.html')

@main.route('/demo/user')
def demo_user():
    """Returns current user info for demo purposes"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user_id': current_user.id,
            'email': current_user.email,
            'username': current_user.username
        })
    else:
        return jsonify({'authenticated': False})

@main.route('/auth')
def auth():
    """Combined login and registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('auth.html')

@main.route('/language/<lang_code>')
@login_required
def set_user_language(lang_code):
    """Set the user's language preference"""
    try:
        # Validate language code
        available_languages = get_available_languages()
        if lang_code not in available_languages:
            flash('Ugyldig språkvalg.', 'danger')
            return redirect(url_for('main.index'))
        
        # Set language in user profile
        current_user.language = lang_code
        db.session.commit()
        
        # Set language for the session
        set_language(lang_code)
        
        flash('Språkinnstilling lagret.', 'success')
    except Exception as e:
        current_app.logger.error(f'Error setting language: {str(e)}')
        flash('Det oppstod en feil ved lagring av språkinnstilling. Prøv igjen senere.', 'danger')
    
    return redirect(url_for('main.index'))

@main.route('/set-language/<language>')
def set_app_language(language):
    """Set application language"""
    from ..utils.i18n_simple import set_language, get_available_languages
    
    if language in get_available_languages():
        set_language(language)
        flash(f'Språk endret til {get_available_languages()[language]}' if language == 'no' else f'Language changed to {get_available_languages()[language]}', 'success')
    else:
        flash('Ugyldig språk valgt' if language == 'no' else 'Invalid language selected', 'error')
    
    # Redirect back to the referring page or home
    return redirect(request.referrer or url_for('main.index'))

@main.route('/api/language/switch', methods=['POST'])
def switch_language():
    """API endpoint for switching language"""
    try:
        data = request.get_json()
        language = data.get('language', 'no')
        
        if language not in ['no', 'en']:
            return jsonify({'success': False, 'error': 'Invalid language'}), 400
            
        # Store in session
        session['language'] = language
        
        return jsonify({
            'success': True,
            'language': language,
            'message': 'Språk endret' if language == 'no' else 'Language changed'
        })
    except Exception as e:
        current_app.logger.error(f"Language switch error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Health check endpoint is now handled by health.py blueprint

# Error handler for 500 - Internal Server Error
@main.errorhandler(500)
def internal_error(error):
    # Log the error for debugging
    current_app.logger.error(f'Internal Server Error: {str(error)}')
    flash('Det oppstod en uventet feil. Vennligst prøv igjen senere.', 'danger')
    return render_template('error.html'), 500

# Check if the stock details route is correctly defined
@main.route('/stocks/details/<ticker>')
@access_required
def stock_details(ticker):
    """Vis detaljer for en spesifikk aksje"""
    try:
        DataService = get_data_service()
        stock_data = DataService.get_stock_info(ticker)
        
        if not stock_data:
            flash('Aksje ikke funnet', 'warning')
            return redirect(url_for('stocks.index'))
        
        # Få relaterte aksjer
        related_stocks = {}
        try:
            # Get related stocks logic here
            pass
        except Exception as e:
            current_app.logger.warning(f"Could not get related stocks: {e}")
        
        return render_template('stocks/details.html',
                             stock=stock_data,
                             ticker=ticker,
                             related_stocks=related_stocks,
                             last_updated=datetime.utcnow())
                             
    except Exception as e:
        current_app.logger.error(f"Error fetching stock details for {ticker}: {str(e)}")
        flash('Kunne ikke hente aksjedata. Prøv igjen senere.', 'danger')
        return redirect(url_for('main.index'))

# Check if the market overview route is correctly defined
@main.route('/analysis/market-overview')
@access_required
def market_overview():
    """Vis markedsoversikt med robuste fallback-data"""
    try:
        DataService = get_data_service()
        
        # Hent markedsdata med fallback-støtte
        oslo_stocks = DataService.get_oslo_bors_overview() or {}
        global_stocks = DataService.get_global_stocks_overview() or {}
        
        # Beregn statistikk
        stats = calculate_market_statistics(oslo_stocks, global_stocks)
        
        return render_template('analysis/market_overview.html',
                             oslo_stocks=oslo_stocks,
                             global_stocks=global_stocks,
                             market_stats=stats,
                             last_updated=datetime.utcnow())
                             
    except Exception as e:
        current_app.logger.error(f"Error in market overview: {e}")
        flash('Kunne ikke laste markedsoversikt', 'error')
        return redirect(url_for('main.index'))

def calculate_market_statistics(oslo_stocks, global_stocks):
    """Beregn markedsstatistikk fra aksjedata"""
    try:
        all_stocks = {**oslo_stocks, **global_stocks}
        
        if not all_stocks:
            return {
                'total_stocks': 0,
                'gainers': 0,
                'losers': 0,
                'unchanged': 0,
                'avg_change': 0.0
            }
        
        gainers = sum(1 for stock in all_stocks.values() if stock.get('change', 0) > 0)
        losers = sum(1 for stock in all_stocks.values() if stock.get('change', 0) < 0)
        unchanged = len(all_stocks) - gainers - losers
        
        total_change = sum(stock.get('change_percent', 0) for stock in all_stocks.values())
        avg_change = total_change / len(all_stocks) if all_stocks else 0.0
        
        return {
            'total_stocks': len(all_stocks),
            'gainers': gainers,
            'losers': losers,
            'unchanged': unchanged,
            'avg_change': round(avg_change, 2)
        }
    except Exception as e:
        current_app.logger.error(f"Error calculating market statistics: {e}")
        return {
            'total_stocks': 0,
            'gainers': 0,
            'losers': 0,
            'unchanged': 0,
            'avg_change': 0.0
        }

# Feedback route to receive user feedback
@main.route('/api/feedback', methods=['POST'])
def feedback():
    """Motta tilbakemelding fra bruker"""
    try:
        data = request.get_json()
        feedback_text = data.get('feedback')
        
        if not feedback_text:
            return jsonify({'success': False, 'message': 'Ingen tilbakemelding mottatt'}), 400
            
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Log feedback for now (siden Feedback model kanskje ikke eksisterer)
        current_app.logger.info(f'Feedback received from user {user_id}: {feedback_text}')
        
        # TODO: Lagre i database når Feedback model er implementert
        # from app.models import Feedback
        # fb = Feedback(user_id=user_id, text=feedback_text)
        # db.session.add(fb)
        # db.session.commit()
        
        return jsonify({'success': True, 'message': 'Takk for tilbakemeldingen!'})
    except Exception as e:
        current_app.logger.error(f'Error handling feedback: {str(e)}')
        return jsonify({'success': False, 'message': 'Kunne ikke lagre tilbakemelding'}), 500
