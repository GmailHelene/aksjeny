from flask import Flask, render_template, request, jsonify, url_for, get_flashed_messages, g
from .config import config
from .extensions import db, login_manager, cache, socketio
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

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Set configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app.logger.info(f"✅ App created in {config_name} mode")
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    
    # Initialize Stripe before configuring stripe webhooks
    setup_stripe(app)
    
    # Initialize migrations
    migrate = Migrate(app, db)
    
    # Set up CSRF protection
    csrf = CSRFProtect(app)
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    
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
        register_template_filters(app)
        
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
        app.logger.info("✅ App initialization complete")
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
    except ImportError as e:
        app.logger.error(f"Failed to import main or portfolio blueprint: {e}")
        raise
    
    # Other blueprints with proper relative imports
    blueprint_configs = [
        ('.routes.stocks', 'stocks', '/stocks'),
        ('.routes.api', 'api', None),
        ('.routes.analysis', 'analysis', '/analysis'),
        ('.routes.pricing', 'pricing_bp', '/pricing'),
        ('.routes.news', 'news_bp', '/news'),
        ('.routes.health', 'health', '/health'),
        ('.routes.admin', 'admin', '/admin'),
        ('.routes.features', 'features', '/features'),
        ('.routes.blog', 'blog', '/blog'),
        ('.routes.investment_guides', 'investment_guides', '/investment-guides'),
        ('.routes.notifications', 'notifications_bp', '/notifications'),
        ('.routes.watchlist_advanced', 'watchlist_bp', '/watchlist'),
    ]
    
    for module_path, blueprint_name, url_prefix in blueprint_configs:
        try:
            from importlib import import_module
            module = import_module(module_path, package=__name__)
            blueprint = getattr(module, blueprint_name)
            # Special case: stocks blueprint should be registered with no prefix (root)
            if blueprint_name == 'stocks':
                app.register_blueprint(blueprint)
            elif url_prefix:
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
            app.logger.info("Stripe API key configured")
        else:
            app.logger.warning("⚠️ Stripe publishable key not found in environment")
            
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
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Format number as currency"""
        if value is None:
            return "N/A"
        try:
            return f"{float(value):,.2f} NOK"
        except (ValueError, TypeError):
            return str(value)
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """Format number as percentage"""
        if value is None:
            return "N/A"
        try:
            return f"{float(value):.2f}%"
        except (ValueError, TypeError):
            return str(value)

    @app.context_processor
    def inject_utils():
        """Make utility functions available in templates"""
        return dict(
            now=datetime.utcnow,
            datetime=datetime
        )
