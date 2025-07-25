from flask import Flask, render_template, request, jsonify, url_for, get_flashed_messages, g, redirect
from .config import config
from .extensions import db, login_manager, csrf, mail, socketio
from .utils.market_open import is_oslo_bors_open, is_global_markets_open
from flask_login import current_user
import logging
import os
from datetime import datetime
import atexit
import signal
import sys
from flask_wtf.csrf import CSRFProtect, CSRFError
from dotenv import load_dotenv
from flask_migrate import Migrate
import psutil
import time
import redis

# Load environment variables
load_dotenv()

# Export db for use in main.py
__all__ = ['create_app', 'db']

def create_app(config_class=None):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Set strict_slashes to False globally
    app.url_map.strict_slashes = False
    
    # Set configuration
    if config_class is None:
        config_name = os.getenv('FLASK_ENV', 'default')
        app.config.from_object(config[config_name])
        app.logger.info(f"✅ App created in {config_name} mode")
    elif isinstance(config_class, str):
        # Handle string config names (existing behavior)
        app.config.from_object(config[config_class])
        app.logger.info(f"✅ App created in {config_class} mode")
    else:
        # Handle config class objects (for testing)
        app.config.from_object(config_class)
        app.logger.info(f"✅ App created with custom config")
    
    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    
    # Register WebSocket handlers
    try:
        from .routes import websocket_handlers
        app.logger.info("✅ WebSocket handlers registered")
    except Exception as e:
        app.logger.warning(f"Failed to register WebSocket handlers: {e}")
    
    # Initialize Stripe before configuring stripe webhooks
    setup_stripe(app)
    
    # Initialize migrations
    migrate = Migrate(app, db)
    
    # Set up CSRF protection
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    
    # Exempt API routes from CSRF protection
    csrf.exempt(lambda: request.endpoint and (
        request.endpoint.startswith('api.') or 
        '/api/' in request.path or
        request.endpoint.startswith('insider_trading.api_')
    ))
    
    # Custom unauthorized handler to ensure users aren't redirected to /
    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for('main.index'))
    
    app.logger.info("Custom unauthorized handler registered for Flask-Login")
    
    # Import models for database creation
    try:
        from . import models
        app.logger.info("✅ Database models imported successfully")
    except Exception as e:
        app.logger.error(f"❌ Failed to import models: {e}")
        raise
    
    # Import cache service to initialize
    try:
        from .services.cache_service import cache_service
    except Exception as e:
        app.logger.warning(f"Cache service initialization failed: {e}")
    
    try:
        # Log static endpoint
        for rule in app.url_map.iter_rules():
            if rule.endpoint == 'static':
                app.logger.info(f"Endpoint: {rule.endpoint} -> {rule}")
                break
        
        register_blueprints(app)
        setup_error_handlers(app)
        
        # Setup global access control middleware
        from .middleware.access_control import apply_global_access_control
        app.before_request(apply_global_access_control)
        
        # Import and setup security headers
        from .utils.security import setup_security_headers
        setup_security_headers(app)
        
        register_template_filters(app)
        
        # Add hasattr to Jinja2 globals to prevent template errors
        app.jinja_env.globals['hasattr'] = hasattr
        app.jinja_env.globals['getattr'] = getattr
        app.jinja_env.globals['isinstance'] = isinstance
        
        # Add translation functions to Jinja2 globals - Setup safely without app context dependency
        def setup_translation_service():
            """Setup translation service safely"""
            try:
                from .services.translation_service import t, get_current_language, get_supported_languages
                app.jinja_env.globals['t'] = t
                app.jinja_env.globals['get_current_language'] = get_current_language
                app.jinja_env.globals['get_supported_languages'] = get_supported_languages
                app.logger.info("✅ Translation service integrated")
                return True
            except Exception as e:
                app.logger.warning(f"Translation service setup failed: {e}")
                return False
                
        # Try main translation service first
        translation_success = setup_translation_service()
        
        # If main service failed, setup fallbacks
        if not translation_success:
            try:
                from .utils.i18n import get_current_language as fallback_get_current_language
                app.jinja_env.globals['get_current_language'] = fallback_get_current_language
                app.logger.info("✅ Fallback get_current_language added to Jinja2 globals")
            except Exception as e:
                app.logger.warning(f"Fallback get_current_language setup failed: {e}")
                # Final fallback: always provide a safe default
                def get_current_language():
                    return 'no'  # Default to Norwegian
                app.jinja_env.globals['get_current_language'] = get_current_language
                app.logger.info("✅ Default get_current_language added to Jinja2 globals")
            
            # Always provide a dummy translation function if t is missing
            if 't' not in app.jinja_env.globals:
                def t(key, **kwargs):
                    fallback = kwargs.get('fallback', key)
                    return fallback
                app.jinja_env.globals['t'] = t
                app.logger.info("✅ Default translation function 't' added to Jinja2 globals")

        # Add a global error handler for template rendering issues
        from jinja2 import TemplateError
        @app.errorhandler(TemplateError)
        def handle_template_error(error):
            app.logger.error(f"Template rendering error: {error}")
            # Return a safe error page instead of crashing
            return render_template('errors/500.html', error_message=str(error)), 500
        
        # Set up app context globals for templates
        @app.context_processor
        def inject_market_status():
            """Make market status available in templates"""
            try:
                return {
                    'oslo_bors_open': is_oslo_bors_open(),
                    'global_markets_open': is_global_markets_open()
                }
            except Exception as e:
                app.logger.warning(f"Error getting market status: {e}")
                return {
                    'oslo_bors_open': False,
                    'global_markets_open': False
                }
        
        # Log all registered endpoints
        app.logger.info("Registered endpoints:")
        for rule in app.url_map.iter_rules():
            app.logger.info(f"Endpoint: {rule.endpoint} -> {rule}")
        
        # Initialize market data service
        def setup_market_data_service():
            """Setup real-time market data service safely"""
            try:
                from .services.market_data_service import MarketDataService
                # Initialize market data service
                app.market_data_service = MarketDataService()
                app.logger.info("✅ Market data service initialized")
                return True
            except Exception as e:
                app.logger.warning(f"Market data service setup failed: {e}")
                return False
        
        # Setup market data service
        setup_market_data_service()
        
        app.logger.info("✅ App initialization complete")
        
        # Initialize database tables within app context
        with app.app_context():
            try:
                if app.config.get('TESTING'):
                    db.create_all()
            except Exception as e:
                app.logger.warning(f"Database initialization skipped: {e}")
        
        return app
        
    except Exception as e:
        app.logger.error(f"❌ Critical error during app creation: {e}")
        raise

def register_blueprints(app):
    """Register all blueprints"""
    blueprints_registered = []
    
    # Core blueprints that must be registered
    try:
        from .routes.main import main
        app.register_blueprint(main)
        blueprints_registered.append('main')
        
        # Explicitly import and register portfolio blueprint
        from .routes.portfolio import portfolio
        app.register_blueprint(portfolio, url_prefix='/portfolio')
        blueprints_registered.append('portfolio')
        
        # Register Stripe blueprint
        try:
            from .routes.stripe_routes import stripe_bp
            app.register_blueprint(stripe_bp)
            blueprints_registered.append('stripe')
            app.logger.info("✅ Registered Stripe blueprint")
        except ImportError as e:
            app.logger.warning(f"Could not import Stripe blueprint: {e}")
        
        # Register Cache Management blueprint
        try:
            from .routes.cache_management import cache_bp
            app.register_blueprint(cache_bp)
            blueprints_registered.append('cache_management')
            app.logger.info("✅ Registered Cache Management blueprint")
        except ImportError as e:
            app.logger.warning(f"Could not import Cache Management blueprint: {e}")
    except ImportError as e:
        app.logger.error(f"Failed to import main or portfolio blueprint: {e}")
        raise
    
    # Other blueprints with proper relative imports
    blueprint_configs = [
        ('.routes.stocks', 'stocks', '/stocks'),
        ('.routes.insider_trading', 'insider_trading', '/insider-trading'),
        ('.routes.api', 'api', None),
        ('.routes.analysis', 'analysis', '/analysis'),
        ('.routes.dashboard', 'dashboard', None),
        ('.routes.pro_tools', 'pro_tools', '/pro-tools'),
        ('.routes.market_intel', 'market_intel', '/market-intel'),
        ('.routes.external_data', 'external_data_bp', '/external-data'),
        ('.routes.backtest', 'backtest_bp', '/backtest'),
        ('.routes.seo_content', 'seo_content', '/content'),
        ('.routes.portfolio_advanced', 'portfolio_advanced', '/portfolio-advanced'),
        ('.routes.advanced_analytics', 'advanced_analytics', '/advanced-analytics'),
        ('.routes.pricing', 'pricing', '/pricing'),
        ('.routes.news', 'news_bp', '/news'),
        ('.routes.health', 'health', '/health'),
        ('.routes.admin', 'admin', '/admin'),
        ('.routes.features', 'features', '/features'),
        ('.routes.blog', 'blog', '/blog'),
        ('.routes.investment_guides', 'investment_guides', '/investment-guides'),
        ('.routes.resources', 'resources_bp', '/resources'),
        ('.routes.advanced_features', 'advanced_features', '/advanced'),
        ('.routes.news_intelligence', 'news_intelligence', '/news-intelligence'),
        ('.routes.mobile_trading', 'mobile_trading', '/mobile-trading'),
        ('.routes.realtime_routes', 'realtime_bp', '/realtime'),
        ('.routes.realtime_websocket', 'realtime_data', None),
        ('.routes.portfolio_analytics', 'portfolio_analytics', '/portfolio-analytics'),
    ]
    
    for module_path, blueprint_name, url_prefix in blueprint_configs:
        try:
            from importlib import import_module
            module = import_module(module_path, package=__name__)
            blueprint = getattr(module, blueprint_name)
            # Register blueprint with appropriate prefix
            if url_prefix:
                app.register_blueprint(blueprint, url_prefix=url_prefix)
            else:
                app.register_blueprint(blueprint)
            blueprints_registered.append(blueprint_name)
            app.logger.info(f"✅ Registered blueprint: {blueprint_name}")
        except ImportError as e:
            app.logger.warning(f"Could not import {blueprint_name}: {e}")
        except Exception as e:
            app.logger.error(f"Error registering {blueprint_name}: {e}")
    
    app.logger.info(f"✅ Registered {len(blueprints_registered)} blueprints: {', '.join(blueprints_registered)}")
    
    # Register the realtime_api blueprint
    try:
        from .routes.realtime_api import realtime_api
        app.register_blueprint(realtime_api)
        blueprints_registered.append('realtime_api')
        app.logger.info("✅ Registered realtime_api blueprint")
    except ImportError as e:
        app.logger.warning(f"Could not import realtime_api blueprint: {e}")

def setup_production_database(app):
    """Setup database for production with proper error handling"""
    try:
        with app.app_context():
            # Create database tables if they don't exist
            db.create_all()
            app.logger.info("✅ Database tables created/verified")
            
            # Set up exempt users for production
            setup_exempt_users(app)
            
    except Exception as e:
        app.logger.error(f"❌ Production database setup failed: {e}")

def setup_exempt_users(app):
    """Set up exempt users for production"""
    try:
        from .models.user import User
        
        exempt_users = [
            {'email': 'helene721@gmail.com', 'username': 'helene721', 'password': 'aksjeradar2024'},
            {'email': 'tonjekit91@gmail.com', 'username': 'tonjekit91', 'password': 'aksjeradar2024'},
            {'email': 'helene@luxushair.com', 'username': 'helene_luxus', 'password': 'aksjeradar2024'},
            {'email': 'eiriktollan.berntsen@gmail.com', 'username': 'eirik_berntsen', 'password': 'aksjeradar2024'}
        ]
        
        for user_data in exempt_users:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    subscription_type='premium',
                    is_admin=True,
                    trial_used=False
                )
                user.set_password(user_data['password'])
                db.session.add(user)
        
        db.session.commit()
        app.logger.info("✅ Exempt users setup completed")
        
    except Exception as e:
        app.logger.error(f"❌ Failed to setup exempt users: {e}")

def setup_stripe(app):
    """Initialize Stripe with proper error handling"""
    try:
        import stripe
        stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        
        if stripe_secret_key:
            stripe.api_key = stripe_secret_key
            app.logger.info("✅ Stripe initialized successfully")
        else:
            app.logger.warning("⚠️ Stripe secret key not found in environment")
        
        stripe_public_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        
        if stripe_public_key:
            app.config['STRIPE_PUBLISHABLE_KEY'] = stripe_public_key
            app.logger.info("✅ Stripe publishable key configured")
        else:
            app.logger.info("ℹ️ Stripe publishable key not configured - payment features disabled")
            app.config['STRIPE_PUBLISHABLE_KEY'] = None
            
    except ImportError:
        app.logger.warning("⚠️ Stripe not installed")
    except Exception as e:
        app.logger.error(f"❌ Stripe initialization failed: {e}")

def setup_error_handlers(app):
    """Setup custom error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(429)
    def rate_limit_error(error):
        """Handle rate limit errors"""
        app.logger.warning(f'Rate limit exceeded: {error}')
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Rate limit exceeded',
                'status_code': 429,
                'retry_after': 60
            }), 429
        else:
            return render_template('errors/500.html'), 429
    
    # Add database error handler
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        app.logger.error(f'Database error: {error}')
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        app.logger.error(f'Database integrity error: {error}')
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(OperationalError)
    def operational_error(error):
        app.logger.error(f'Database operational error: {error}')
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Add TemplateNotFound error handler
    from jinja2 import TemplateNotFound
    @app.errorhandler(TemplateNotFound)
    def template_not_found_error(error):
        app.logger.error(f"Template not found: {error}")
        return render_template('errors/500.html', 
                             error_message=f"Template ikke funnet: {error}"), 500
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """Handle CSRFError specifically"""
        from flask import redirect, url_for
        
        app.logger.warning(f'CSRFError: {str(e)}')
        
        if 'checkout' in request.path:
            return redirect(url_for('main.subscription'))
        elif 'login' in request.path:
            return redirect(url_for('main.login'))
        else:
            return redirect(url_for('main.index'))

def register_template_filters(app):
    """Register custom template filters"""
    from .utils.filters import register_filters
    
    # Register filters from utils/filters.py
    register_filters(app)
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Format number as currency"""
        if value is None:
            return "—"
        try:
            return f"{float(value):,.2f} NOK"
        except (ValueError, TypeError):
            return str(value)
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """Format number as percentage"""
        if value is None:
            return "—"
        try:
            return f"{float(value):.2f}%"
        except (ValueError, TypeError):
            return str(value)

    @app.template_filter('datetimeformat')
    def datetimeformat_filter(value):
        """Format datetime for display"""
        if value is None:
            return "—"
        try:
            if isinstance(value, str):
                # Parse ISO format datetime
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                dt = value
            return dt.strftime('%d.%m.%Y kl. %H:%M')
        except (ValueError, TypeError):
            return str(value)

    @app.context_processor
    def inject_utils():
        """Make utility functions available in templates"""
        return dict(
            now=datetime.utcnow,
            datetime=datetime
        )
    
    @app.template_filter('nn')
    def nn_filter(value, decimals=2, suffix=''):
        """Norwegian number formatting filter"""
        if value is None:
            return "—"
        try:
            if isinstance(value, str):
                value = float(value)
            formatted = f"{value:,.{decimals}f}".replace(',', ' ').replace('.', ',')
            if suffix:
                return f"{formatted} {suffix}"
            return formatted
        except (ValueError, TypeError):
            return str(value) if value is not None else "—"

    @app.template_filter('pct')
    def pct_filter(value):
        """Format as percentage"""
        if value is None:
            return "—"
        try:
            formatted = f"{float(value):.2f}".replace('.', ',')
            return f"{formatted} %"
        except (ValueError, TypeError):
            return str(value) if value is not None else "—"
