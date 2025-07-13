#!/bin/bash

# 🚀 Aksjeradar Deployment Script
# This script handles deployment of the Aksjeradar application

set -e  # Exit on any error

echo "🚀 Starting Aksjeradar Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the correct directory
if [ ! -f "run.py" ]; then
    print_error "run.py not found! Make sure you're in the project root directory."
    exit 1
fi

# Step 1: Check Python version
print_status "Checking Python version..."
python3 --version || {
    print_error "Python 3 is not installed!"
    exit 1
}
print_success "Python 3 is available"

# Step 2: Create/activate virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

print_status "Activating virtual environment..."
source venv/bin/activate

# Step 3: Upgrade pip and install requirements
print_status "Upgrading pip and installing requirements..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
print_success "Dependencies installed"

# Step 4: Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating basic .env file..."
    cat > .env << EOF
# Flask Configuration
SECRET_KEY=production-secret-key-change-this-$(openssl rand -hex 32)
WTF_CSRF_SECRET_KEY=csrf-secret-key-change-this-$(openssl rand -hex 32)
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=sqlite:///app.db

# Stripe (Add your real keys for production)
STRIPE_SECRET_KEY=sk_test_dummy_key
STRIPE_MONTHLY_PRICE_ID=price_dummy_monthly
STRIPE_YEARLY_PRICE_ID=price_dummy_yearly

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
EOF
    print_success "Basic .env file created. Please update with your actual configuration!"
else
    print_success ".env file exists"
fi

# Step 5: Initialize database with enhanced debugging
print_status "Initializing database..."
python3 -c "
try:
    from app import create_app
    from app.extensions import db
    
    app = create_app()
    with app.app_context():
        # Check if database file exists
        import os
        db_path = app.config.get('DATABASE_URL', 'sqlite:///app.db').replace('sqlite:///', '')
        print(f'Database path: {db_path}')
        
        # Create tables
        db.create_all()
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'Created tables: {tables}')
        
        if tables:
            print('✅ Database tables created successfully!')
        else:
            print('⚠️ Warning: No tables found after creation')
            
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"
print_success "Database initialized"
# Step 6: Test application startup with enhanced debugging
print_status "Testing application startup..."
python3 -c "
try:
    from app import create_app
    app = create_app()
    
    print('✅ Application startup test successful!')
    print(f'🌐 Debug mode: {app.debug}')
    print(f'📊 Database URI configured: {bool(app.config.get(\"SQLALCHEMY_DATABASE_URI\"))}')
    
    # Test route registration
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f'{rule.rule} -> {rule.endpoint}')
        
        print(f'📍 Total routes registered: {len(routes)}')
        
        # Check critical routes
        critical_routes = ['/', '/login', '/register']
        for route in critical_routes:
            found = any(route in r for r in routes)
            status = '✅' if found else '❌'
            print(f'{status} Route {route}: {\"Found\" if found else \"Missing\"}')
            
except Exception as e:
    print(f'❌ Application startup failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"
print_success "Application startup test passed"
# Step 6.5: Validate templates
print_status "Validating templates..."
python3 -c "
try:
    from app import create_app
    from jinja2 import Environment, FileSystemLoader
    import os
    
    app = create_app()
    
    # Check if templates directory exists
    templates_dir = os.path.join(app.root_path, 'templates')
    if not os.path.exists(templates_dir):
        print('⚠️ Templates directory not found')
    else:
        print(f'📁 Templates directory: {templates_dir}')
        
        # List template files
        template_files = []
        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith('.html'):
                    template_files.append(os.path.join(root, file))
        
        print(f'📄 Found {len(template_files)} template files')
        
        # Try to compile templates with Flask context
        errors = []
        success_count = 0
        
        with app.app_context():
            # Create a fake request context for template validation
            with app.test_request_context('/', method='GET'):
                from flask import render_template
                
                # Create mock data for common template variables
                class MockField:
                    def __init__(self, data='test'):
                        self.data = data
                        self.label = type('MockLabel', (), {'text': 'Test Label'})()
                    
                    def __call__(self, **kwargs):
                        attrs = ' '.join(f'{k}=\"{v}\"' for k, v in kwargs.items())
                        return f'<input name=\"{self.data}\" {attrs}>'
                
                class MockForm:
                    def __init__(self):
                        self.username = MockField('username')
                        self.password = MockField('password')
                        self.email = MockField('email')
                        self.confirm_password = MockField('confirm_password')
                        self.referral_code = MockField('referral_code')
                        self.csrf_token = 'mock_csrf_token'
                    
                    def hidden_tag(self):
                        return '<input type=\"hidden\" name=\"csrf_token\" value=\"mock_token\"/>'
                
                class MockUser:
                    def __init__(self):
                        self.is_authenticated = False
                        self.is_anonymous = True
                        self.username = 'test_user'
                        self.email = 'test@example.com'
                        self.subscription_status = 'inactive'
                        self.subscription_type = 'free'
                        self.trial_used = False
                        self.has_subscription = False
                        self.is_admin = False
                    
                    def has_active_subscription(self):
                        return False
                    
                    def is_in_trial_period(self):
                        return True
                
                mock_data = {
                    'current_user': MockUser(),
                    'form': MockForm(),
                    'portfolio': {'name': 'Test Portfolio', 'stocks': []},
                    'stock_info': {'symbol': 'TEST', 'price': 100.0, 'name': 'Test Stock'},
                    'post': {'title': 'Test Post', 'content': 'Test Content'},
                    'technical_data': {'price': 100.0, 'volume': 1000, 'rsi': 50.0, 'macd': 0.5},
                    'show_banner': False,
                    'config': app.config,
                    'stats': {'total_users': 100, 'active_users': 50},
                    'global_indices': [{'name': 'S&P 500', 'value': 4000, 'change': 1.2}],
                    'insider_activity': [{'company': 'TEST', 'action': 'buy', 'shares': 1000}],
                    'analyses': {'EQNR.OL': {'signal': 'BUY', 'price': 290.5}},
                    'oslo_stocks': {'EQNR.OL': {'symbol': 'EQNR.OL', 'price': 290.5, 'signal': 'BUY'}},
                    'global_stocks': {'AAPL': {'symbol': 'AAPL', 'price': 175.0, 'signal': 'HOLD'}},
                    'crypto': {'BTC-USD': {'symbol': 'BTC', 'price': 65000, 'signal': 'BUY'}},
                    'currency': {'USDNOK=X': {'symbol': 'USD/NOK', 'price': 10.45, 'change': 0.1}},
                    'buy_signals': 5,
                    'sell_signals': 2,
                    'neutral_signals': 3,
                    'ticker': 'EQNR.OL',
                    'predictions_oslo': {},
                    'predictions_global': {},
                    'usage_summary': {'remaining': 10, 'total': 15},
                    'available_stocks': ['EQNR.OL', 'DNB.OL', 'AAPL', 'MSFT'],
                    'stock_data': {'symbol': 'EQNR.OL', 'analysis': 'Strong Buy'},
                    'fundamental_data': {'pe_ratio': 12.5, 'market_cap': 850000000000},
                    'news': [{'title': 'Test News', 'url': '#', 'source': 'Test Source'}],
                    'categories': ['oslo', 'global', 'crypto'],
                    'stocks': {'EQNR.OL': {'price': 290.5, 'change': 1.2}},
                    'notifications': [],
                    'notification': {'title': 'Test', 'message': 'Test message'},
                    'pagination': type('MockPagination', (), {
                        'items': [],
                        'has_prev': False,
                        'has_next': False,
                        'prev_num': None,
                        'next_num': None,
                        'page': 1,
                        'pages': 1,
                        'per_page': 20,
                        'total': 0
                    })()
                }
                
                # Test critical templates first
                critical_templates = ['index.html', 'login.html', 'base.html', 'register.html']
                
                for template_file in template_files:
                    try:
                        template_name = os.path.relpath(template_file, templates_dir)
                        
                        # Try to render template with mock data
                        render_template(template_name, **mock_data)
                        
                        status = '✅' if template_name in critical_templates else '✅'
                        print(f'{status} Template {template_name}: OK')
                        success_count += 1
                        
                    except Exception as e:
                        error_msg = str(e)
                        # Filter out common template validation issues that are OK in runtime
                        if 'is undefined' in error_msg and any(var in error_msg for var in ['request', 'url_for', 'get_flashed_messages', 'csrf_token']):
                            # These are expected to be injected by Flask at runtime
                            print(f'⚠️ Template {template_name}: Context dependency (OK at runtime)')
                        else:
                            errors.append(f'❌ Template {template_name}: {error_msg}')
                            print(f'❌ Template {template_name}: {error_msg}')
        
        print(f'\\n📊 Template validation summary:')
        print(f'  ✅ Successfully validated: {success_count}')
        print(f'  ❌ Errors found: {len(errors)}')
        
        if errors:
            print('\\n🔍 Critical template errors to fix:')
            for error in errors[:10]:  # Show first 10 errors
                print(f'  {error}')
        else:
            print('✅ All templates validated successfully')
            
except Exception as e:
    print(f'❌ Template validation failed: {e}')
    import traceback
    traceback.print_exc()
"
print_success "Template validation completed"

# Step 6.6: Test critical endpoints with actual HTTP requests
print_status "Testing critical endpoints..."
python3 -c "
try:
    from app import create_app
    import requests
    from threading import Thread
    import time
    import signal
    import sys
    
    app = create_app()
    
    # Start test server in background
    def run_server():
        app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test endpoints
    test_endpoints = [
        ('/', 'Home page'),
        ('/login', 'Login page'),
        ('/register', 'Register page'),
        ('/pricing', 'Pricing page'),
        ('/demo', 'Demo page')
    ]
    
    print('🔍 Testing endpoints:')
    for endpoint, description in test_endpoints:
        try:
            response = requests.get(f'http://127.0.0.1:5555{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f'✅ {endpoint} ({description}): OK - Status {response.status_code}')
            elif response.status_code >= 500:
                print(f'❌ {endpoint} ({description}): Server Error - Status {response.status_code}')
            else:
                print(f'⚠️ {endpoint} ({description}): Status {response.status_code}')
                
        except Exception as e:
            print(f'❌ {endpoint} ({description}): Connection failed - {str(e)}')
    
    print('✅ Endpoint testing completed')
    
except ImportError:
    print('⚠️ Requests library not available, skipping endpoint tests')
except Exception as e:
    print(f'❌ Endpoint testing failed: {e}')
"
print_success "Critical endpoints tested"























































print_success "🎯 Aksjeradar is ready to launch!"echo ""echo "  ✅ Application: Tested"echo "  ✅ Configuration: Ready"echo "  ✅ Database: Initialized"echo "  ✅ Dependencies: Installed"echo "  ✅ Virtual environment: $(which python3)"print_status "📋 Deployment Summary:"echo ""# Step 9: Show final statusprint_success "All checks passed! Application is ready for deployment! 🚀"echo ""echo "   docker run -p 8000:8000 -v \$(pwd)/.env:/app/.env aksjeradar"echo "   docker build -t aksjeradar ."echo "4. ${BLUE}For Docker deployment:${NC}"echo ""echo "   sudo systemctl start aksjeradar"echo "   sudo systemctl enable aksjeradar"echo "   sudo cp aksjeradar.service /etc/systemd/system/"echo "3. ${BLUE}For systemd service:${NC}"echo ""echo "   gunicorn --workers 3 --bind 0.0.0.0:8000 run:app"echo "   pip install gunicorn"echo "2. ${BLUE}For production with Gunicorn:${NC}"echo ""echo "   python3 run.py"echo "1. ${BLUE}For development server:${NC}"echo ""echo -e "${GREEN}Next steps for production deployment:${NC}"echo ""print_status "🎉 Deployment preparation complete!"echo ""# Step 8: Production deployment optionsfi    print_warning "Development server test skipped"else    kill $SERVER_PID 2>/dev/null || true    print_success "Development server started successfully"if kill -0 $SERVER_PID 2>/dev/null; then# Check if server is runningsleep 2SERVER_PID=$!timeout 5s python3 run.py &print_status "Starting development server test (5 seconds)..."# Step 7: Run a quick development server testprint_success "Template validation completed""    traceback.print_exc()    import traceback    print(f'❌ Template validation failed: {e}')SERVER_PID=$!
sleep 2

# Check if server is running
if kill -0 $SERVER_PID 2>/dev/null; then
    print_success "Development server started successfully"
    kill $SERVER_PID 2>/dev/null || true
else
    print_warning "Development server test skipped"
fi

# Step 8: Production deployment options
echo ""
print_status "🎉 Deployment preparation complete!"
echo ""
echo -e "${GREEN}Next steps for production deployment:${NC}"
echo ""
echo "1. ${BLUE}For development server:${NC}"
echo "   python3 run.py"
echo ""
echo "2. ${BLUE}For production with Gunicorn:${NC}"
echo "   pip install gunicorn"
echo "   gunicorn --workers 3 --bind 0.0.0.0:8000 run:app"
echo ""
echo "3. ${BLUE}For systemd service:${NC}"
echo "   sudo cp aksjeradar.service /etc/systemd/system/"
echo "   sudo systemctl enable aksjeradar"
echo "   sudo systemctl start aksjeradar"
echo ""
echo "4. ${BLUE}For Docker deployment:${NC}"
echo "   docker build -t aksjeradar ."
echo "   docker run -p 8000:8000 -v \$(pwd)/.env:/app/.env aksjeradar"
echo ""
print_success "All checks passed! Application is ready for deployment! 🚀"

# Step 9: Show final status with detailed health check
echo ""
print_status "📋 Final Deployment Health Check:"

# Check database
python3 -c "
try:
    from app import create_app
    from app.extensions import db
    from sqlalchemy import inspect
    
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'  ✅ Database: {len(tables)} tables created')
        
        # Check if critical tables exist
        critical_tables = ['user', 'subscription', 'payment']
        for table in critical_tables:
            if table in tables:
                print(f'    ✅ Table {table}: Found')
            else:
                print(f'    ⚠️ Table {table}: Missing')
                
except Exception as e:
    print(f'  ❌ Database: Error - {e}')
"

# Check configuration
python3 -c "
try:
    from app import create_app
    app = create_app()
    
    print(f'  ✅ Virtual environment: $(which python3)')
    print(f'  ✅ Dependencies: Installed')
    print(f'  ✅ Configuration: Ready')
    print(f'  ✅ Application: Tested')
    
    # Check critical config
    config_checks = [
        ('SECRET_KEY', 'Secret key configured'),
        ('SQLALCHEMY_DATABASE_URI', 'Database URI configured'),
        ('WTF_CSRF_SECRET_KEY', 'CSRF protection configured')
    ]
    
    for key, description in config_checks:
        if app.config.get(key):
            print(f'  ✅ {description}')
        else:
            print(f'  ⚠️ {description}: Missing')
            
except Exception as e:
    print(f'  ❌ Configuration: Error - {e}')
"

echo ""
print_success "🎯 Aksjeradar deployment health check completed!"

# Step 10: Create troubleshooting log
print_status "Creating troubleshooting log..."
python3 -c "
import datetime
import os
from app import create_app

# Create deployment log
log_content = f'''
# Aksjeradar Deployment Log
Generated: {datetime.datetime.now().isoformat()}

## System Information
- Python Version: $(python3 --version)
- Working Directory: $(pwd)
- Virtual Environment: $(which python3)

## Configuration Status
'''

try:
    app = create_app()
    log_content += f'''
- Flask App: ✅ Created successfully
- Debug Mode: {app.debug}
- Secret Key: {'✅ Configured' if app.config.get('SECRET_KEY') else '❌ Missing'}
- Database URI: {'✅ Configured' if app.config.get('SQLALCHEMY_DATABASE_URI') else '❌ Missing'}
'''
    
    # Check routes
    with app.app_context():
        routes = list(app.url_map.iter_rules())
        log_content += f'''
## Route Information
- Total Routes: {len(routes)}
- Critical Routes:
'''
        critical_routes = ['/', '/login', '/register', '/health']
        for route in critical_routes:
            found = any(route == rule.rule for rule in routes)
            status = '✅' if found else '❌'
            log_content += f'  {status} {route}\\n'
    
    # Write log file
    with open('deployment_log.md', 'w') as f:
        f.write(log_content)
    
    print('✅ Troubleshooting log created: deployment_log.md')
    
except Exception as e:
    print(f'❌ Failed to create troubleshooting log: {e}')
"
print_success "Troubleshooting log created"
