from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db, login_manager
from ..utils.subscription import subscription_required
from ..utils.access_control import access_required
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
from ..extensions import mail
from flask_wtf.csrf import CSRFProtect

# Lazy imports - only import when needed
def get_user_model():
    """Lazily import and return the User model."""
    from ..models.user import User
    return User

def get_data_service():
    """Lazily import and return the DataService class."""
    from ..services.data_service import DataService
    return DataService

def get_referral_service():
    """Lazily import and return the ReferralService class."""
    from ..services.referral_service import ReferralService
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
@access_required
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

@main.route('/search')
@access_required
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('main.index'))
     
    # Lazy import DataService
    DataService = get_data_service()
    results = DataService.search_ticker(query)
    return render_template('search_results.html', results=results, query=query)

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
@main.route('/subscription/')
def subscription():
    """Subscription page"""
    return jsonify({
        'status': 'OK',
        'page': 'subscription',
        'message': 'Abonnement-side fungerer!',
        'plans': [
            {'name': 'Basic', 'price': '199 kr/mnd'},
            {'name': 'Pro', 'price': '399 kr/mnd'},
            {'name': 'Pro Årlig', 'price': '3499 kr/år'}
        ]
    })

@main.route('/profile')
@main.route('/profile/')
@login_required
def profile():
    """User profile page"""
    return jsonify({
        'status': 'OK',
        'page': 'profile',
        'message': 'Profil-side fungerer!',
        'user': {
            'email': current_user.email if current_user.is_authenticated else None,
            'username': current_user.username if current_user.is_authenticated else None
        }
    })

@main.route('/terms')
@main.route('/terms/')
def terms():
    """Terms of service page"""
    return jsonify({
        'status': 'OK',
        'page': 'terms',
        'message': 'Vilkår-side fungerer!',
        'content': 'Vilkår for bruk av Aksjeradar'
    })

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