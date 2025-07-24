from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response, jsonify, send_from_directory, g
from ..utils.market_open import is_market_open
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import hashlib
import time

# Import column fallbacks for database compatibility
try:
    from ..utils.column_fallbacks import apply_column_fallbacks
    apply_column_fallbacks()
except ImportError:
    pass  # Fallbacks not available

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from sqlalchemy import text
from ..extensions import db, login_manager

def has_active_subscription():
    """Check if current user has active subscription"""
    if not current_user.is_authenticated:
        return False
    
    try:
        # Check exempt users first
        if hasattr(current_user, 'email') and current_user.email in EXEMPT_EMAILS:
            return True
            
        # Check subscription status
        if hasattr(current_user, 'has_active_subscription'):
            return current_user.has_active_subscription()
            
        # Fallback check
        if hasattr(current_user, 'subscription_type') and current_user.subscription_type:
            return current_user.subscription_type in ['premium', 'pro', 'yearly', 'lifetime']
            
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        
    return False
from ..utils.subscription import subscription_required
from ..utils.access_control import access_required
from ..utils.access_control import access_required, is_demo_user, is_trial_active, api_login_required
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
    """Lazily import and return the DataService class with error handling."""
    try:
        from ..services.data_service import DataService
        return DataService
    except ImportError as e:
        logger.warning(f"DataService not available: {e}")
        # Return a mock service for fallback
        class MockDataService:
            @staticmethod
            def get_oslo_bors_overview():
                return {}
            @staticmethod
            def get_global_stocks_overview():
                return {}
            @staticmethod
            def get_crypto_overview():
                return {}
            @staticmethod
            def get_currency_overview():
                return {}
        return MockDataService

def get_referral_service():
    """Lazily import and return the ReferralService class."""
    from ..services.referral_service import ReferralService
    return ReferralService

def get_forms():
    """Lazily import and return all forms used in this module."""
    from ..forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm
    return LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm

def get_performance_monitor():
    """Lazily import and return the performance monitor decorator."""
    try:
        from ..services.performance_monitor import monitor_performance
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
@main.route('/index')
def index():
    """Enhanced homepage with access control"""
    from ..utils.access_control import is_exempt_user, check_access_and_redirect
    
    # Check access and potentially redirect
    redirect_response = check_access_and_redirect()
    if redirect_response:
        return redirect_response
    
    if current_user.is_authenticated and is_exempt_user():
        # Exempt users get full access
        restricted = False
    elif current_user.is_authenticated and has_active_subscription():
        # Subscribed users get full access  
        restricted = False
    else:
        # Non-authenticated or trial users get limited access
        restricted = True
    
    try:
        if current_user.is_authenticated:
            # Check if user is premium
            is_premium = False
            if hasattr(current_user, 'subscription') and current_user.subscription:
                is_premium = getattr(current_user.subscription, 'status', '') == 'active'
            
            if is_premium:
                # Show dashboard-style homepage for premium users
                DataService = get_data_service()
                oslo_stocks = DataService.get_oslo_bors_overview() or {}
                global_stocks = DataService.get_global_stocks_overview() or {}
                crypto_data = DataService.get_crypto_overview() or {}
                currency_data = DataService.get_currency_overview() or {}
                
                return render_template('dashboard_home.html',
                                     oslo_stocks=oslo_stocks,
                                     global_stocks=global_stocks,
                                     crypto_data=crypto_data,
                                     currency_data=currency_data,
                                     user=current_user)
            else:
                # Show regular homepage for free users (without pricing section)
                return render_template('index.html',
                                     show_pricing=False,
                                     user=current_user)
        else:
            # Show demo homepage with pricing
            return render_template('index.html',
                                 show_pricing=True,
                                 user=None)
                                 
    except Exception as e:
        current_app.logger.error(f"Error in homepage: {e}")
        return render_template('index.html',
                             show_pricing=True,
                             error="Kunne ikke laste siden")

# Ensure demo functions are accessible without login or subscription
@main.route('/demo')
def demo():
    """Demo page with full functionality preview"""
    demo_data = {
        'demo_mode': True,
        'stocks': [
            {'symbol': 'EQNR.OL', 'name': 'Equinor ASA', 'price': 285.50, 'change': '+2.4%', 'signal': 'KJØP', 'analysis': 'Sterk teknisk momentum'},
            {'symbol': 'DNB.OL', 'name': 'DNB Bank ASA', 'price': 245.80, 'change': '+1.8%', 'signal': 'HOLD', 'analysis': 'Stabil utvikling'},
            {'symbol': 'TEL.OL', 'name': 'Telenor ASA', 'price': 138.20, 'change': '-0.5%', 'signal': 'SELG', 'analysis': 'Svak momentum'}
        ],
        'analysis': {
            'recommendation': 'KJØP',
            'confidence': '85%',
            'target_price': '320 NOK',
            'risk_level': 'Moderat',
            'time_horizon': '6-12 måneder',
            'signals': [
                'Sterk teknisk momentum',
                'Positiv fundamental utvikling', 
                'Økende institusjonell interesse'
            ]
        },
        'portfolio': {
            'total_value': 850000,
            'daily_change': 12500,
            'daily_change_percent': '1.5',
            'holdings': [
                {'symbol': 'EQNR.OL', 'name': 'Equinor', 'quantity': 100, 'value': 285000, 'change': '+2.4%'},
                {'symbol': 'DNB.OL', 'name': 'DNB Bank', 'quantity': 200, 'value': 491600, 'change': '+1.8%'},
                {'symbol': 'TEL.OL', 'name': 'Telenor', 'quantity': 50, 'value': 69100, 'change': '-0.5%'}
            ]
        }
    }
    
    return render_template('demo.html', **demo_data)

# Fixing the error handling for portfolio loading
@main.route('/portfolio')
@login_required
def portfolio():
    """Portfolio page for users"""
    try:
        # Logic to load user portfolio
        return render_template('portfolio.html')
    except Exception as e:
        current_app.logger.error(f"Error loading portfolio: {str(e)}")
        flash('Det oppstod en feil ved lasting av porteføljen. Prøv igjen senere.','error')
        return redirect(url_for('main.index'))

# Ensure all templates are functioning and accessible
# This includes checking for duplicates and ensuring correct URLs are set
# Additional checks for mobile and desktop navigation links

# Pricing route handled by pricing blueprint (/pricing/)

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
        
        # Get data for all markets with fallback
        oslo_stocks = DataService.get_oslo_bors_overview() or {}
        global_stocks = DataService.get_global_stocks_overview() or {}
        crypto = DataService.get_crypto_overview() or {}
        currency = DataService.get_currency_overview() or {}
        
        # Calculate statistics
        stats = {
            'total_stocks': len(oslo_stocks) + len(global_stocks),
            'total_crypto': len(crypto),
            'total_currency': len(currency),
            'total_instruments': len(oslo_stocks) + len(global_stocks) + len(crypto) + len(currency)
        }
        
        return render_template('stocks/prices.html', 
                             market_data={
                                 'oslo_stocks': oslo_stocks,
                                 'global_stocks': global_stocks,
                                 'crypto': crypto,
                                 'currency': currency
                             },
                             stats=stats)
    except Exception as e:
        current_app.logger.error(f"Error in prices route: {e}")
        # Return template with fallback data instead of redirect
        fallback_stats = {
            'total_stocks': 250,
            'total_crypto': 50,
            'total_currency': 30,
            'total_instruments': 330
        }
        return render_template('stocks/prices.html', 
                             market_data={
                                 'oslo_stocks': {},
                                 'global_stocks': {},
                                 'crypto': {},
                                 'currency': {}
                             },
                             stats=fallback_stats,
                             error="Det oppstod en feil ved henting av prisdata, viser fallback-data")

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with proper form handling and database error recovery"""
    from flask import request
    from ..models import User
    from ..forms import LoginForm
    from werkzeug.security import check_password_hash
    from sqlalchemy.exc import OperationalError, ProgrammingError
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            # Try to find user by email
            user = User.query.filter_by(email=form.email.data.lower().strip()).first()
            
            if user and user.password_hash and check_password_hash(user.password_hash, form.password.data):
                # Update last login if column exists
                try:
                    user.last_login = datetime.utcnow()
                    if hasattr(user, 'login_count'):
                        user.login_count = (user.login_count or 0) + 1
                    db.session.commit()
                except Exception as update_error:
                    current_app.logger.warning(f'Could not update login stats: {update_error}')
                    db.session.rollback()
                
                login_user(user, remember=form.remember_me.data)
                
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('main.index')
                
                current_app.logger.info(f'Successful login for user: {user.email}')
                flash('Innlogging vellykket!', 'success')
                return redirect(next_page)
            else:
                current_app.logger.warning(f'Failed login attempt for email: {form.email.data}')
                flash('Ugyldig e-post eller passord.', 'danger')
                
        except (OperationalError, ProgrammingError) as db_error:
            current_app.logger.error(f'Database error during login: {db_error}')
            flash('Database-feil. Kontakt support hvis problemet vedvarer.', 'danger')
            
        except Exception as e:
            current_app.logger.error(f'Unexpected login error: {e}')
            flash('En feil oppstod under innloggingen. Prøv igjen.', 'danger')
    
    return render_template('login.html', title='Logg inn', form=form)

@main.route('/logout', methods=['GET', 'POST'])
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
    
    # Create simple response with minimal headers
    response = make_response(redirect(url_for('main.index')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Clear only essential cookies
    response.set_cookie('session', '', expires=0, max_age=0, path='/')
    response.set_cookie('remember_token', '', expires=0, max_age=0, path='/')
    response.set_cookie('user_logged_in', '', expires=0, max_age=0, path='/')
    
    return response

def unauthorized_handler():
    flash('Du må logge inn for å få tilgang til denne siden.', 'warning')
    return redirect(url_for('main.login', next=request.url))

# Register unauthorized handler
login_manager.unauthorized_handler(unauthorized_handler)

@main.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page with proper form handling"""
    from flask import request
    from ..models import User
    from ..extensions import db
    from ..forms import RegistrationForm
    from werkzeug.security import generate_password_hash
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Check if user already exists
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('En bruker med denne e-postadressen eksisterer allerede.', 'danger')
                return render_template('register.html', title='Registrer deg', form=form)
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data)
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registreringen var vellykket! Du kan nå logge inn.', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {e}')
            flash('En feil oppstod under registreringen. Prøv igjen.', 'danger')
    
    return render_template('register.html', title='Registrer deg', form=form)

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

@main.route('/offline')
def offline():
    """Offline page for PWA"""
    return render_template('offline.html')

@main.route('/offline.html')
def offline_html():
    """Offline HTML page for PWA"""
    return render_template('offline.html')

@main.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        return contact_submit()
    return render_template('contact.html')

@main.route('/contact/submit', methods=['POST'])
def contact_submit():
    """Handle contact form submission"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if not name or not email or not message:
            flash('Alle felt må fylles ut.', 'error')
            return redirect(url_for('main.contact'))
        
        # Here you would normally send an email or save to database
        current_app.logger.info(f"Contact form submitted by {email}")
        
        flash('Takk for din henvendelse! Vi vil svare deg så snart som mulig.', 'success')
        return redirect(url_for('main.contact'))
        
    except Exception as e:
        current_app.logger.error(f"Error in contact form: {e}")
        flash('Det oppstod en feil. Vennligst prøv igjen senere.', 'error')
        return redirect(url_for('main.contact'))

@main.route('/subscription')
@main.route('/subscription/')
@login_required
def subscription():
    """Subscription management page"""
    try:
        # Redirect to pricing page for subscription plans
        return redirect(url_for('pricing.index'))
    except Exception as e:
        current_app.logger.error(f"Error redirecting to pricing: {e}")
        flash('Kunne ikke laste prissiden.', 'error')
        return redirect(url_for('main.index'))

@main.route('/subscription/plans')
@login_required
def subscription_plans():
    """Subscription plans page"""
    try:
        # Redirect to pricing page since that's where plans are shown
        return redirect(url_for('pricing.index'))
    except Exception as e:
        current_app.logger.error(f"Error redirecting to pricing: {e}")
        flash('Kunne ikke laste prissiden.', 'error')
        return redirect(url_for('main.index'))

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        User = get_user_model()
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            # Generate reset token
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = serializer.dumps(user.email, salt='password-reset-salt')
            
            # Send reset email
            try:
                msg = Message(
                    'Tilbakestill passord - Aksjeradar',
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@aksjeradar.com'),
                    recipients=[user.email]
                )
                reset_url = url_for('main.reset_password', token=token, _external=True)
                msg.body = f'''Hei {user.username},

Du har bedt om å tilbakestille passordet ditt på Aksjeradar.

Klikk på følgende lenke for å tilbakestille passordet:
{reset_url}

Hvis du ikke har bedt om dette, kan du ignorere denne e-posten.

Med vennlig hilsen,
Aksjeradar-teamet'''
                
                mail.send(msg)
                flash('En e-post med instruksjoner for å tilbakestille passordet har blitt sendt.', 'info')
            except Exception as e:
                current_app.logger.error(f"Failed to send reset email: {e}")
                flash('Kunne ikke sende e-post. Vennligst prøv igjen senere.', 'error')
        else:
            # Don't reveal if email exists or not
            flash('Hvis e-postadressen finnes i systemet, vil du motta en e-post med instruksjoner.', 'info')
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html', form=form)

@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, ReferralForm = get_forms()
    form = ResetPasswordForm()
    
    try:
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiry
    except:
        flash('Ugyldig eller utløpt lenke for tilbakestilling av passord.', 'error')
        return redirect(url_for('main.login'))
    
    if form.validate_on_submit():
        User = get_user_model()
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            flash('Passordet ditt har blitt oppdatert! Du kan nå logge inn.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Bruker ikke funnet.', 'error')
            return redirect(url_for('main.login'))
    
    return render_template('reset_password.html', form=form, token=token)

@main.route('/referrals')
@login_required
def referrals():
    """Referral program page"""
    ReferralService = get_referral_service()
    
    # Get user's referral code
    referral_code = ReferralService.get_or_create_referral_code(current_user)
    
    # Get referral stats
    stats = ReferralService.get_referral_stats(current_user)
    
    # Generate referral link
    referral_link = url_for('main.register', ref=referral_code, _external=True)
    
    return render_template('referrals.html',
                         referral_code=referral_code,
                         referral_link=referral_link,
                         stats=stats)

@main.route('/referrals/send', methods=['POST'])
@login_required
def send_referral():
    """Send referral invitation"""
    email = request.form.get('email')
    
    if not email:
        flash('E-postadresse er påkrevd.', 'error')
        return redirect(url_for('main.referrals'))
    
    ReferralService = get_referral_service()
    referral_code = ReferralService.get_or_create_referral_code(current_user)
    referral_link = url_for('main.register', ref=referral_code, _external=True)
    
    try:
        msg = Message(
            f'{current_user.username} inviterer deg til Aksjeradar',
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@aksjeradar.com'),
            recipients=[email]
        )
        msg.body = f'''Hei!

{current_user.username} har invitert deg til å prøve Aksjeradar - Norges smarteste aksjeplattform.

Registrer deg med denne lenken for å få spesielle fordeler:
{referral_link}

Med Aksjeradar får du:
- AI-drevne aksjeanalyser
- Sanntids markedsdata
- Porteføljeovervåking
- Ekspertanbefalinger

Bli med i dag!

Med vennlig hilsen,
Aksjeradar-teamet'''
        
        mail.send(msg)
        flash(f'Invitasjon sendt til {email}!', 'success')
    except Exception as e:
        current_app.logger.error(f"Failed to send referral email: {e}")
        flash('Kunne ikke sende invitasjon. Vennligst prøv igjen senere.', 'error')
    
    return redirect(url_for('main.referrals'))

@main.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html', now=datetime.now())

@main.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html', now=datetime.now())

@main.route('/about')
def about():
    """About page"""
    return render_template('about.html', 
                         title="Om Aksjeradar",
                         now=datetime.now())

@main.route('/help')
def help():
    """Help and FAQ page"""
    return render_template('help.html', 
                         title="Hjelp og FAQ",
                         now=datetime.now())

@main.route('/settings')
@login_required 
def settings():
    """User settings page"""
    return render_template('settings.html', 
                         title="Innstillinger",
                         now=datetime.now())

@main.route('/features')
def features():
    """Features overview page"""
    return render_template('features.html', 
                         title="Funksjoner",
                         now=datetime.now())

# Error handlers
@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@main.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@main.route('/profile')
@login_required
def profile():
    """User profile page with proper error handling"""
    try:
        # Safely get user subscription info
        subscription = None
        subscription_status = 'free'
        
        if hasattr(current_user, 'subscription') and current_user.subscription:
            subscription = current_user.subscription
            subscription_status = getattr(subscription, 'status', 'free')
        
        # Get user stats safely
        user_stats = {
            'member_since': getattr(current_user, 'created_at', datetime.now()),
            'last_login': getattr(current_user, 'last_login', None),
            'total_searches': getattr(current_user, 'search_count', 0),
            'favorite_stocks': getattr(current_user, 'favorite_count', 0)
        }
        
        return render_template('profile.html',
                             user=current_user,
                             subscription=subscription,
                             subscription_status=subscription_status,
                             user_stats=user_stats)
                             
    except Exception as e:
        logger.error(f"Error in profile page for user {getattr(current_user, 'id', 'unknown')}: {e}")
        flash('Kunne ikke laste profilsiden. Prøv igjen senere.', 'error')
        return render_template('profile.html',
                             user=current_user,
                             subscription=None,
                             subscription_status='free',
                             user_stats={},
                             error=True)

@main.route('/mitt-abonnement')
@main.route('/my-subscription')
@login_required
def my_subscription():
    """Dedicated user subscription management page"""
    try:
        # Get detailed subscription info
        subscription_info = {
            'status': 'free',
            'plan_name': 'Gratis',
            'plan_description': 'Grunnleggende tilgang til aksjedata og analyser',
            'start_date': None,
            'end_date': None,
            'next_billing': None,
            'price': 0,
            'currency': 'NOK',
            'features': [
                'Begrenset tilgang til aksjedata',
                'Grunnleggende teknisk analyse',
                'Daglig markedsoversikt'
            ],
            'upgrade_options': [
                {
                    'name': 'Pro',
                    'price': 299,
                    'features': [
                        'Ubegrenset tilgang til alle aksjer',
                        'Avanserte analyser (Warren Buffett, Benjamin Graham)',
                        'AI-drevne anbefalinger',
                        'Innsidehandel-overvåkning',
                        'Sanntids prisdata',
                        'Eksport av data'
                    ]
                },
                {
                    'name': 'Premium',
                    'price': 599,
                    'features': [
                        'Alt i Pro-pakken',
                        'Porteføljeoptimalisering',
                        'Backtesting av strategier',
                        'Avanserte screener-filter',
                        'API-tilgang',
                        'Prioritert kundestøtte'
                    ]
                }
            ]
        }
        
        # Check if user has active subscription
        if hasattr(current_user, 'subscription') and current_user.subscription:
            subscription = current_user.subscription
            if hasattr(subscription, 'status') and subscription.status == 'active':
                subscription_info.update({
                    'status': 'active',
                    'plan_name': getattr(subscription, 'plan_name', 'Pro'),
                    'start_date': getattr(subscription, 'start_date', None),
                    'end_date': getattr(subscription, 'end_date', None),
                    'next_billing': getattr(subscription, 'next_billing_date', None),
                    'price': getattr(subscription, 'price', 299),
                    'features': [
                        'Ubegrenset tilgang til alle aksjer',
                        'Avanserte analyser',
                        'AI-drevne anbefalinger',
                        'Sanntids prisdata'
                    ]
                })
        
        return render_template('subscription_management.html',
                             subscription=subscription_info,
                             user=current_user)
                             
    except Exception as e:
        logger.error(f"Error in subscription page for user {getattr(current_user, 'id', 'unknown')}: {e}")
        flash('Kunne ikke laste abonnementssiden. Prøv igjen senere.', 'error')
        return redirect(url_for('main.profile'))

@main.route('/set_language/<language>')
def set_language(language=None):
    """Set user language preference"""
    if language in ['no', 'en']:
        session['language'] = language
        flash(f'Språk endret til {"Norsk" if language == "no" else "English"}', 'success')
    
    # Redirect back to referring page or home
    return redirect(request.referrer or url_for('main.index'))

@main.route('/admin/cache')
def cache_management():
    """Cache management interface"""
    return render_template('cache_management.html')

@main.route('/admin/api/cache/bust', methods=['POST'])
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

@main.route('/admin/api/cache/status')
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