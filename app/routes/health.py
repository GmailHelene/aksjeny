from flask import Blueprint, jsonify, current_app
from flask_login import current_user
from sqlalchemy import text
from ..extensions import db
from ..models.user import User
import stripe
import os
from datetime import datetime
import platform
import psutil
import time

health = Blueprint('health', __name__)

@health.route('/')
@health.route('/health')  # Add alias for Docker health check
@health.route('/ready')   # Railway uses /ready for health checks
def check_health():
    """Basic health check endpoint that verifies critical services."""
    try:
        # Quick database connection check with timeout
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Database query timeout")
        
        # Set 5 second timeout for database query
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(5)
        
        try:
            db.session.execute(text('SELECT 1'))
            db.session.commit()
            database_status = 'connected'
        finally:
            signal.alarm(0)  # Cancel the alarm
        
        health_status = {
            'status': 'healthy',
            'ready': True,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'database': database_status,
                'app': 'running'
            }
        }
        return jsonify(health_status), 200
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'ready': False,
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503  # Service Unavailable

@health.route('/detailed')
def detailed_health():
    """Detailed health check with information about the system and application."""
    health_data = {
        'status': 'ok',
        'timestamp': time.time(),
        'application': {
            'name': 'Aksjeradar',
            'environment': 'production' if current_app.config.get('IS_REAL_PRODUCTION') else 'development',
            'debug_mode': current_app.debug,
        },
        'system': {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_usage': psutil.cpu_percent(interval=0.1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent_used': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free,
                'percent_used': psutil.disk_usage('/').percent
            }
        }
    }
    
    # Check database connection
    try:
        db.session.execute(text('SELECT 1'))
        health_data['database'] = {
            'status': 'connected',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_data['database'] = {
            'status': 'error',
            'message': str(e)
        }
        health_data['status'] = 'degraded'
    
    # Check export folder is writable
    export_folder = current_app.config.get('EXPORT_FOLDER')
    if export_folder:
        try:
            if os.access(export_folder, os.W_OK):
                health_data['export_folder'] = {
                    'status': 'writable',
                    'path': export_folder
                }
            else:
                health_data['export_folder'] = {
                    'status': 'not_writable',
                    'path': export_folder
                }
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['export_folder'] = {
                'status': 'error',
                'message': str(e)
            }
            health_data['status'] = 'degraded'
    
    return jsonify(health_data)

@health.route('/ready')
def readiness():
    """Readiness probe that verifies if the application is ready to serve traffic."""
    ready = True
    status_code = 200
    
    # Check database connection
    try:
        db.session.execute(text('SELECT 1'))
        database_ok = True
    except Exception:
        database_ok = False
        ready = False
        status_code = 503  # Service Unavailable
    
    return jsonify({
        'ready': ready,
        'database': database_ok
    }), status_code

@health.route('/live')
def liveness():
    """Liveness probe that verifies if the application is alive."""
    return jsonify({
        'alive': True
    })

@health.route('/routes')
def check_routes():
    """Check all registered routes and their status."""
    from flask import current_app as app
    
    # Only allow in development mode for security reasons
    if not app.debug and app.config.get('IS_REAL_PRODUCTION', False):
        return jsonify({
            'error': 'This endpoint is only available in development mode'
        }), 403
    
    routes_data = []
    
    for rule in app.url_map.iter_rules():
        # Skip the static routes and the current route to avoid infinite recursion
        if 'static' in rule.endpoint or rule.endpoint == 'health.check_routes':
            continue
            
        # Get methods excluding HEAD and OPTIONS
        methods = [method for method in rule.methods if method not in ('HEAD', 'OPTIONS')]
        
        # Get the blueprint name
        blueprint = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'app'
        
        route_info = {
            'endpoint': rule.endpoint,
            'methods': sorted(methods),
            'path': str(rule),
            'blueprint': blueprint,
            'is_authenticated_required': 'login' in rule.endpoint.lower() or 'account' in rule.endpoint.lower()
        }
        
        routes_data.append(route_info)
    
    # Sort by path for easier reading
    routes_data = sorted(routes_data, key=lambda x: x['path'])
    
    # Group by blueprint
    blueprints = {}
    for route in routes_data:
        bp = route['blueprint']
        if bp not in blueprints:
            blueprints[bp] = []
        blueprints[bp].append(route)
    
    response = {
        'total_routes': len(routes_data),
        'blueprints_summary': {bp: len(routes) for bp, routes in blueprints.items()},
        'routes_by_blueprint': blueprints
    }
    
    return jsonify(response)

@health.route('/check-all')
def check_all_dependencies():
    """Comprehensive check of all application dependencies."""
    results = {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        results['checks']['database'] = {
            'status': 'ok',
            'message': 'Database connection successful'
        }
    except Exception as e:
        results['checks']['database'] = {
            'status': 'error',
            'message': str(e)
        }
        results['status'] = 'degraded'
    
    # Stripe API check if configured
    if current_app.config.get('STRIPE_SECRET_KEY'):
        try:
            stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
            # Just check if we can access the API (list a small number of customers)
            stripe.Customer.list(limit=1)
            results['checks']['stripe'] = {
                'status': 'ok',
                'message': 'Stripe API connection successful'
            }
        except Exception as e:
            results['checks']['stripe'] = {
                'status': 'error',
                'message': str(e)
            }
            # Don't mark as degraded as Stripe may not be critical
    
    # Export folder check
    export_folder = current_app.config.get('EXPORT_FOLDER')
    if export_folder:
        try:
            if os.path.exists(export_folder) and os.access(export_folder, os.W_OK):
                results['checks']['export_folder'] = {
                    'status': 'ok',
                    'message': 'Export folder is accessible and writable',
                    'path': export_folder
                }
            else:
                results['checks']['export_folder'] = {
                    'status': 'error',
                    'message': 'Export folder is not accessible or not writable',
                    'path': export_folder
                }
                results['status'] = 'degraded'
        except Exception as e:
            results['checks']['export_folder'] = {
                'status': 'error',
                'message': str(e)
            }
            results['status'] = 'degraded'
    
    # Application configuration check
    config_issues = []
    critical_configs = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI']
    
    for config in critical_configs:
        if not current_app.config.get(config):
            config_issues.append(f"Missing {config}")
    
    if config_issues:
        results['checks']['configuration'] = {
            'status': 'error',
            'message': 'Configuration issues detected',
            'issues': config_issues
        }
        results['status'] = 'degraded'
    else:
        results['checks']['configuration'] = {
            'status': 'ok',
            'message': 'All critical configurations are present'
        }
    
    return jsonify(results)
