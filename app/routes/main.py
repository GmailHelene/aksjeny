from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response, jsonify, send_from_directory
from ..utils.market_open import is_market_open

main = Blueprint('main', __name__)

# GDPR-side
@main.route('/gdpr')
def gdpr():
    return render_template('gdpr.html')
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

EXEMPT_EMAILS = {'helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com', 'tonjekit91@gmail.com'}

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
    'portfolio.portfolio_index',
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
        if stripe_key:
            stripe.api_key = stripe_key
            state.app.logger.info('✅ Stripe initialized successfully')
        else:
            state.app.logger.warning('⚠️ Stripe not configured (key missing)')
    except ImportError:
        state.app.logger.warning('⚠️ Stripe initialization skipped (module not available)')
    except Exception as e:
        state.app.logger.warning(f'⚠️ Stripe initialization failed: {e}')

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
def index():
    """Landing page"""
    # Market open/close info - lazy import pytz
    pytz = get_pytz()
    try:
        if pytz:
            oslo_tz = pytz.timezone('Europe/Oslo')
            now_oslo = datetime.now(oslo_tz)
            
            # Set market hours in Oslo time
            market_open = dt_time(9, 0)  # 09:00
            market_close = dt_time(16, 30)  # 16:30
            
            # Check if market is currently open
            current_time = now_oslo.time()
            is_weekday = now_oslo.weekday() < 5  # Monday = 0, Sunday = 6
            market_is_open = is_weekday and market_open <= current_time <= market_close
            
            # Format next opening/closing time
            if market_is_open:
                next_event_time = now_oslo.replace(
                    hour=market_close.hour,
                    minute=market_close.minute,
                    second=0
                ).strftime('%H:%M')
            else:
                if current_time > market_close:  # After closing
                    next_date = now_oslo + timedelta(days=1)
                    while next_date.weekday() >= 5:  # Skip weekend
                        next_date += timedelta(days=1)
                    next_event_time = next_date.replace(
                        hour=market_open.hour,
                        minute=market_open.minute,
                        second=0
                    ).strftime('%H:%M')
                else:  # Before opening
                    next_event_time = now_oslo.replace(
                        hour=market_open.hour,
                        minute=market_open.minute,
                        second=0
                    ).strftime('%H:%M')
        else:
            # Fallback if pytz not available
            market_is_open = True  # Default to open
            next_event_time = "16:30"  # Default closing time
            
    except Exception as e:
        current_app.logger.error(f"Error determining market status: {e}")
        # Fallback values
        market_is_open = True
        next_event_time = "16:30"
    
    # Get DataService
    data_service = get_data_service()()
    
    try:
        # Get the indices
        indices = data_service.get_indices()
        
        # Get crypto data
        crypto_data = data_service.get_crypto_overview()
        
        # Get currency data
        currency_data = data_service.get_currency_overview()
        
        # Get most active stocks
        most_active = data_service.get_most_active_stocks()
        
        # Get stock gainers and losers
        gainers = data_service.get_stock_gainers()
        losers = data_service.get_stock_losers()
        
        # Get sectors performance
        sectors = data_service.get_sectors_performance()
        
        # Get Oslo Børs stocks
        oslo_stocks = data_service.get_oslo_bors_overview()
        
        # Get global stocks
        global_stocks = data_service.get_global_stocks_overview()
        
    except Exception as e:
        current_app.logger.error(f"Error fetching market data: {e}")
        flash("Det oppstod et problem med å hente markedsdataene. Vennligst prøv igjen senere.", "error")
        
        # Set fallback values
        indices = []
        crypto_data = []
        currency_data = []
        most_active = []
        gainers = []
        losers = []
        sectors = []
        oslo_stocks = {}
        global_stocks = {}
    
    # Determine if banner should be shown
    EXEMPT_EMAILS_GLOBAL = {'helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com', 'tonjekit91@gmail.com'}
    show_banner = False
    try:
        if current_user.is_authenticated:
            # Exempt emails never see banners
            if current_user.email in EXEMPT_EMAILS_GLOBAL:
                show_banner = False
            elif hasattr(current_user, 'has_active_subscription') and current_user.has_active_subscription():
                # Active subscription - no banner
                show_banner = False
            else:
                # No subscription - hide banner (trial period removed)
                show_banner = False
        else:
            # Not logged in - hide banner (trial period removed)
            show_banner = False
    except Exception:
        show_banner = False

    return render_template('index.html',
        indices=indices,
        crypto=crypto_data,
        currency=currency_data,
        most_active=most_active,
        gainers=gainers,
        losers=losers,
        sectors=sectors,
        oslo_stocks=oslo_stocks,
        global_stocks=global_stocks,
        market_is_open=market_is_open,
        next_event_time=next_event_time,
        is_demo=is_demo_user(),
        show_banner=show_banner,
        oslo_open=is_market_open('oslo'),
        global_open=is_market_open('global'))

@main.route('/demo')
def demo():
    """Show demo page for non-subscribers with real data"""
    try:
        from ..services.data_service import (
            get_market_overview, get_oslo_bors_overview, 
            get_global_stocks_overview, get_indices,
            get_most_active_stocks, get_stock_gainers, get_stock_losers
        )
        
        # Get market data for demo
        market_data = get_market_overview()
        oslo_stocks = get_oslo_bors_overview()
        global_stocks = get_global_stocks_overview()
        indices = get_indices()
        active_stocks = get_most_active_stocks()
        gainers = get_stock_gainers()
        losers = get_stock_losers()
        
        # Sample portfolio data for demo
        demo_portfolio = [
            {'ticker': 'EQNR.OL', 'name': 'Equinor ASA', 'shares': 100, 'value': 34255, 'change': '+2.3%'},
            {'ticker': 'DNB.OL', 'name': 'DNB Bank ASA', 'shares': 50, 'value': 10640, 'change': '-0.56%'},
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'shares': 25, 'value': 47500, 'change': '+1.2%'},
        ]
        
        # Sample alerts for demo
        demo_alerts = [
            {'type': 'price', 'message': 'EQNR.OL har nådd ditt kursmål på 340 kr', 'time': '10:30'},
            {'type': 'volume', 'message': 'Høy volum på DNB.OL - 150% over normal', 'time': '09:15'},
            {'type': 'news', 'message': 'Ny analyse av AAPL fra Goldman Sachs', 'time': '08:45'},
        ]
        
        # Sample news for demo
        demo_news = [
            {
                'title': 'Oslo Børs stiger på sterke tall fra Equinor',
                'summary': 'Equinor rapporterer sterkere tall enn ventet for Q4, hovedindeksen stiger 1.2%',
                'time': '2 timer siden',
                'source': 'E24'
            },
            {
                'title': 'DNB Bank øker utbytte mer enn ventet',
                'summary': 'Norges største bank øker utbyttet til 15 kroner per aksje for 2024',
                'time': '4 timer siden',
                'source': 'Finansavisen'
            },
            {
                'title': 'Apple lanserer nye AI-funksjoner',
                'summary': 'Apple Intelligence får store oppdateringer i iOS 18.3',
                'time': '6 timer siden',
                'source': 'TechCrunch'
            }
        ]
        
        return render_template('demo.html',
                             market_data=market_data,
                             oslo_stocks=oslo_stocks,
                             global_stocks=global_stocks,
                             indices=indices,
                             active_stocks=active_stocks,
                             gainers=gainers,
                             losers=losers,
                             demo_portfolio=demo_portfolio,
                             demo_alerts=demo_alerts,
                             demo_news=demo_news)
                             
    except Exception as e:
        current_app.logger.error(f"Error loading demo data: {str(e)}")
        # Fallback to basic demo if data loading fails
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

@main.route('/prices')
@access_required
def prices():
    """Comprehensive market prices overview"""
    try:
        # Lazy import DataService
        DataService = get_data_service()
        
        # Get data for all markets
        oslo_stocks = DataService.get_oslo_overview()
        global_stocks = DataService.get_global_overview()
        crypto = DataService.get_crypto_overview()
        currency = DataService.get_currency_overview()
        
        return render_template('stocks/prices.html', 
                             oslo_stocks=oslo_stocks,
                             global_stocks=global_stocks,
                             crypto=crypto,
                             currency=currency)
    except Exception as e:
        current_app.logger.error(f"Error in prices route: {e}")
        flash('Kunne ikke hente prisdata. Prøv igjen senere.', 'error')
        return redirect(url_for('main.index'))

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
                response.set_cookie(cookie_name, '', expires=0, max_age=0, domain=domain, path='/', secure=True, httponly=True, samesite='None'
                )
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

@main.route('/financial-dashboard')
@main.route('/financial-dashboard/')
@access_required
def financial_dashboard():
    """Financial dashboard with tabbed interface"""
    try:
        return render_template('dashboard/financial_dashboard.html')
    except Exception as e:
        current_app.logger.error(f"Error in financial dashboard: {str(e)}")
        flash("En feil oppstod ved lasting av dashbordet.", "error")
        return redirect(url_for('main.index'))

@main.route('/insider-trading')
@main.route('/insider-trading/')
@access_required
def insider_trading():
    """Insider trading analysis page"""
    try:
        return render_template('analysis/insider_trading.html')
    except Exception as e:
        current_app.logger.error(f"Error in insider trading: {str(e)}")
        flash("En feil oppstod ved lasting av innsidehandel.", "error")
        return redirect(url_for('main.index'))

@main.route('/subscription')
@main.route('/subscription/')
def subscription():
    """Subscription page"""
    return render_template('subscription.html')

@main.route('/profile')
@main.route('/profile/')
@login_required
def profile():
    """User profile page"""
    try:
        # Get user subscription status and other relevant data
        has_subscription = current_user.has_active_subscription() if hasattr(current_user, 'has_active_subscription') else False
        
        # Get user portfolio and activity data if available
        portfolio_value = 0
        total_stocks = 0
        try:
            from app.models import Portfolio
            user_portfolios = Portfolio.query.filter_by(user_id=current_user.id).all()
            total_stocks = len(user_portfolios)
            portfolio_value = sum([p.quantity * (p.current_price or 0) for p in user_portfolios])
        except:
            pass
            
        return render_template('profile.html',
                             user=current_user,
                             has_subscription=has_subscription,
                             portfolio_value=portfolio_value,
                             total_stocks=total_stocks)
    except Exception as e:
        current_app.logger.error(f"Error in profile route: {str(e)}")
        flash("En feil oppstod ved lasting av profilen.", "error")
        return redirect(url_for('main.index'))

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

# Add missing utility functions for password reset
def generate_reset_token(user):
    """Generate a secure reset token for password reset"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user.email, salt='password-reset-salt')

def verify_reset_token(token, expires_sec=3600):
    """Verify reset token and return user if valid"""
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
    except Exception:
        return None
    User = get_user_model()
    return User.query.filter_by(email=email).first()

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
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
                flash('E-post kunne ikke sendes. Prøv igjen senere.', 'danger')
        else:
            # For security, always show success message
            flash('En e-post med instruksjoner for tilbakestilling av passord er sendt.', 'info')
        return redirect(url_for('main.forgot_password'))
    return render_template('forgot_password.html', form=form)

@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    # Lazy import forms
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    
    user = verify_reset_token(token)
    form = ResetPasswordForm()
    if not user:
        flash('Ugyldig eller utløpt lenke for tilbakestilling av passord.', 'danger')
        return redirect(url_for('main.forgot_password'))
    if form.validate_on_submit():
        password = form.password.data
        user.set_password(password)
        db.session.commit()
        flash('Passordet er oppdatert. Du kan nå logge inn.', 'success')
        return redirect(url_for('main.login'))
    return render_template('reset_password.html', form=form, token=token)

@main.route('/api/trial-status')
def api_trial_status():
    """API endpoint for checking trial status"""
    from ..utils.access_control import get_trial_status
    
    try:
        # Always return that trial is expired and user needs subscription
        return jsonify({
            'trial_active': False,
            'trial_expired': True,
            'subscription_required': True,
            'message': 'Trial period has ended. Please subscribe to continue using premium features.'
        })
    except Exception as e:
        current_app.logger.error(f"Error checking trial status: {e}")
        return jsonify({'error': 'Unable to check trial status'}), 500

@main.route('/api/dashboard/data')
@login_required
def dashboard_data():
    """API endpoint for dashboard data"""
    try:
        # Get user stocks from query params
        symbols = request.args.getlist('symbols') or ['EQNR.OL', 'DNB.OL', 'TEL.OL', 'AAPL', 'GOOGL']
        
        # Provide fallback stock data
        stock_data = {}
        for symbol in symbols:
            stock_data[symbol] = {
                'price': 250.75 + (hash(symbol) % 100),  # Deterministic "random" price
                'change': (hash(symbol) % 10) - 5,  # -5 to +5 range
                'change_percent': ((hash(symbol) % 10) - 5) / 10,  # -5% to +5%
                'volume': 1000000 + (hash(symbol) % 5000000),
                'pe_ratio': 10 + (hash(symbol) % 30)
            }
        
        # Provide fallback crypto data
        crypto_data = [
            {'rank': 1, 'symbol': 'BTC', 'name': 'Bitcoin', 'price_usd': 45000, 'price_change_percentage_24h': 2.5, 'market_cap': 850000000000, 'volume_24h': 25000000000},
            {'rank': 2, 'symbol': 'ETH', 'name': 'Ethereum', 'price_usd': 3200, 'price_change_percentage_24h': 1.8, 'market_cap': 380000000000, 'volume_24h': 15000000000},
            {'rank': 3, 'symbol': 'BNB', 'name': 'Binance Coin', 'price_usd': 420, 'price_change_percentage_24h': -0.5, 'market_cap': 65000000000, 'volume_24h': 2000000000},
            {'rank': 4, 'symbol': 'SOL', 'name': 'Solana', 'price_usd': 120, 'price_change_percentage_24h': 3.2, 'market_cap': 45000000000, 'volume_24h': 1800000000},
            {'rank': 5, 'symbol': 'ADA', 'name': 'Cardano', 'price_usd': 0.85, 'price_change_percentage_24h': -1.2, 'market_cap': 28000000000, 'volume_24h': 800000000}
        ]
        
        # Provide fallback currency data
        currency_data = [
            {'target': 'EUR', 'rate': 0.92, 'change_24h': 0.002},
            {'target': 'NOK', 'rate': 10.67, 'change_24h': 0.15},
            {'target': 'GBP', 'rate': 0.81, 'change_24h': -0.005},
            {'target': 'JPY', 'rate': 149.50, 'change_24h': 0.80},
            {'target': 'CAD', 'rate': 1.35, 'change_24h': 0.01}
        ]
        
        return jsonify({
            'success': True,
            'dashboard_data': {
                'stocks': stock_data,
                'crypto': crypto_data,
                'currencies': currency_data
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/economic/indicators')
@login_required
def economic_indicators():
    """API endpoint for economic indicators"""
    try:
        indicators = [
            {'indicator': 'Norges Bank Rente', 'value': '4.50', 'unit': '%', 'date': '2025-07-01', 'source': 'Norges Bank'},
            {'indicator': 'Inflasjon (KPI)', 'value': '3.2', 'unit': '%', 'date': '2025-06-01', 'source': 'SSB'},
            {'indicator': 'Arbeidsledighet', 'value': '3.1', 'unit': '%', 'date': '2025-06-01', 'source': 'Nav'},
            {'indicator': 'USD/NOK', 'value': '10.67', 'unit': '', 'date': '2025-07-14', 'source': 'DNB'},
            {'indicator': 'Oljepris (Brent)', 'value': '82.45', 'unit': '$', 'date': '2025-07-14', 'source': 'ICE'}
        ]
        
        return jsonify({
            'success': True,
            'economic_indicators': indicators
        })
    except Exception as e:
        current_app.logger.error(f"Error getting economic indicators: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/market/sectors')
@login_required
def market_sectors():
    """API endpoint for sector analysis"""
    try:
        sectors = {
            'energy': {'trend': 'bullish', 'performance': '+2.5%', 'symbols': ['EQNR.OL', 'AKA.OL']},
            'finance': {'trend': 'neutral', 'performance': '+0.1%', 'symbols': ['DNB.OL', 'GOGL.OL']},
            'technology': {'trend': 'bearish', 'performance': '-1.2%', 'symbols': ['AAPL', 'GOOGL']},
            'healthcare': {'trend': 'bullish', 'performance': '+1.8%', 'symbols': ['JNJ', 'PFE']},
            'telecommunications': {'trend': 'neutral', 'performance': '+0.3%', 'symbols': ['TEL.OL', 'VZ']}
        }
        
        return jsonify({
            'success': True,
            'sector_analysis': sectors
        })
    except Exception as e:
        current_app.logger.error(f"Error getting sector analysis: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/news/financial')
@login_required
def financial_news():
    """API endpoint for financial news"""
    try:
        symbols = request.args.getlist('symbols') or []
        limit = int(request.args.get('limit', 10))
        
        # Provide fallback news data
        news_articles = [
            {
                'title': 'Norges Bank holder renten uendret på 4,50 prosent',
                'summary': 'Sentralbanken velger å holde styringsrenten på dagens nivå i påvente av flere inflasjonsdata.',
                'sentiment': 'neutral',
                'published_at': '2025-07-14T10:30:00Z',
                'source': 'E24',
                'url': 'https://e24.no/example'
            },
            {
                'title': 'Equinor melder om sterke kvartalstall',
                'summary': 'Oljeselskapet overgår analytikernes forventninger med høyere inntjening og produksjon.',
                'sentiment': 'positive',
                'published_at': '2025-07-14T09:15:00Z',
                'source': 'DN',
                'url': 'https://dn.no/example'
            },
            {
                'title': 'Teknologiaksjer under press i USA',
                'summary': 'Flere store teknologiselskaper faller på børsen etter skuffende guidning for neste kvartal.',
                'sentiment': 'negative',
                'published_at': '2025-07-14T08:00:00Z',
                'source': 'Reuters',
                'url': 'https://reuters.com/example'
            },
            {
                'title': 'DNB øker utbytte til aksjonærene',
                'summary': 'Storbanken varsler høyere utbytte for 2025 basert på sterke resultater.',
                'sentiment': 'positive',
                'published_at': '2025-07-14T07:45:00Z',
                'source': 'Finansavisen',
                'url': 'https://finansavisen.no/example'
            },
            {
                'title': 'Kryptovaluta-markedet viser tegn til stabilisering',
                'summary': 'Bitcoin og Ethereum holder seg relativt stabile etter flere ukers volatilitet.',
                'sentiment': 'neutral',
                'published_at': '2025-07-14T06:30:00Z',
                'source': 'CoinDesk',
                'url': 'https://coindesk.com/example'
            }
        ]
        
        return jsonify({
            'success': True,
            'news': news_articles[:limit]
        })
    except Exception as e:
        current_app.logger.error(f"Error getting financial news: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/insider/analysis/<symbol>')
@login_required
def insider_analysis(symbol):
    """API endpoint for insider trading analysis"""
    try:
        # Provide fallback insider analysis
        analysis = {
            'insider_analysis': {
                'insider_sentiment': 'Bullish',
                'buy_sell_ratio': '2.3:1'
            },
            'market_sentiment': {
                'sentiment_score': 0.72,
                'analyst_sentiment': 'Positive'
            },
            'key_insights': [
                f'Flere innsidere har kjøpt {symbol} aksjer de siste månedene',
                f'CEO økte sin posisjon i {symbol} med 15% i forrige kvartal',
                f'Ingen større salg registrert fra ledelsen'
            ],
            'insider_transactions': [
                {
                    'insider_name': 'John Smith',
                    'transaction_type': 'Buy',
                    'shares': 5000,
                    'transaction_date': '2025-07-10'
                },
                {
                    'insider_name': 'Jane Doe',
                    'transaction_type': 'Buy',
                    'shares': 2500,
                    'transaction_date': '2025-07-08'
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        current_app.logger.error(f"Error getting insider analysis for {symbol}: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/crypto/data')
@login_required
def crypto_data():
    """API endpoint for crypto data"""
    try:
        limit = int(request.args.get('limit', 10))
        
        crypto_data = [
            {'rank': 1, 'symbol': 'BTC', 'name': 'Bitcoin', 'price_usd': 45000, 'price_change_percentage_24h': 2.5, 'market_cap': 850000000000, 'volume_24h': 25000000000},
            {'rank': 2, 'symbol': 'ETH', 'name': 'Ethereum', 'price_usd': 3200, 'price_change_percentage_24h': 1.8, 'market_cap': 380000000000, 'volume_24h': 15000000000},
            {'rank': 3, 'symbol': 'BNB', 'name': 'Binance Coin', 'price_usd': 420, 'price_change_percentage_24h': -0.5, 'market_cap': 65000000000, 'volume_24h': 2000000000},
            {'rank': 4, 'symbol': 'SOL', 'name': 'Solana', 'price_usd': 120, 'price_change_percentage_24h': 3.2, 'market_cap': 45000000000, 'volume_24h': 1800000000},
            {'rank': 5, 'symbol': 'ADA', 'name': 'Cardano', 'price_usd': 0.85, 'price_change_percentage_24h': -1.2, 'market_cap': 28000000000, 'volume_24h': 800000000},
            {'rank': 6, 'symbol': 'DOT', 'name': 'Polkadot', 'price_usd': 28, 'price_change_percentage_24h': 0.8, 'market_cap': 25000000000, 'volume_24h': 600000000},
            {'rank': 7, 'symbol': 'LINK', 'name': 'Chainlink', 'price_usd': 15, 'price_change_percentage_24h': 1.5, 'market_cap': 20000000000, 'volume_24h': 500000000},
            {'rank': 8, 'symbol': 'MATIC', 'name': 'Polygon', 'price_usd': 1.2, 'price_change_percentage_24h': -0.8, 'market_cap': 18000000000, 'volume_24h': 400000000}
        ]
        
        return jsonify({
            'success': True,
            'crypto_data': crypto_data[:limit]
        })
    except Exception as e:
        current_app.logger.error(f"Error getting crypto data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/crypto/trending')
@login_required
def crypto_trending():
    """API endpoint for trending crypto"""
    try:
        trending_crypto = [
            {'symbol': 'BTC', 'name': 'Bitcoin', 'rank': 1},
            {'symbol': 'ETH', 'name': 'Ethereum', 'rank': 2},
            {'symbol': 'SOL', 'name': 'Solana', 'rank': 4},
            {'symbol': 'ADA', 'name': 'Cardano', 'rank': 5},
            {'symbol': 'DOT', 'name': 'Polkadot', 'rank': 6}
        ]
        
        return jsonify({
            'success': True,
            'trending_crypto': trending_crypto
        })
    except Exception as e:
        current_app.logger.error(f"Error getting trending crypto: {e}")
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/currency/rates')
@login_required
def currency_rates():
    """API endpoint for currency exchange rates"""
    try:
        currency_rates = [
            {'target': 'EUR', 'rate': 0.92, 'change_24h': 0.002},
            {'target': 'NOK', 'rate': 10.67, 'change_24h': 0.15},
            {'target': 'GBP', 'rate': 0.81, 'change_24h': -0.005},
            {'target': 'JPY', 'rate': 149.50, 'change_24h': 0.80},
            {'target': 'CAD', 'rate': 1.35, 'change_24h': 0.01},
            {'target': 'CHF', 'rate': 0.89, 'change_24h': -0.003},
            {'target': 'SEK', 'rate': 10.85, 'change_24h': 0.08}
        ]
        
        return jsonify({
            'success': True,
            'currency_rates': currency_rates
        })
    except Exception as e:
        current_app.logger.error(f"Error getting currency rates: {e}")
        return jsonify({'success': False, 'error': str(e)})
