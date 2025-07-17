from flask import request, session, current_app as app, render_template
from flask_login import current_user
from . import main
import traceback

# Exempt endpoints that don't need access control
EXEMPT_ENDPOINTS = {
    'main.register', 'main.login', 'main.logout', 
    'main.privacy', 'main.subscription', 'main.demo',
    'main.api_trial_status', 'static', 'main.demo_ping',
    'main.demo_echo', 'main.market_overview', 'main.stock_details'
}

@main.before_request
def before_request():
    """Handle access control before each request"""
    try:
        # Skip access control for demo and certain endpoints
        if request.endpoint in EXEMPT_ENDPOINTS:
            return
        
        # Skip for static files
        if request.endpoint == 'static':
            return
            
        # Allow all demo functionality
        if request.path.startswith('/demo'):
            return
            
        # Allow market overview for everyone
        if request.path.startswith('/market-overview'):
            return
            
    except Exception as e:
        app.logger.error(f"Error in access restriction: {e}")
        # On error, allow access to prevent blocking the site
        return

@main.route('/demo')
def demo():
    """Demo page with full functionality - no restrictions"""
    # Prepare demo data
    demo_stocks = [
        {'symbol': 'EQNR.OL', 'name': 'Equinor ASA', 'price': 342.55, 'change': '+2.1%'},
        {'symbol': 'DNB.OL', 'name': 'DNB Bank ASA', 'price': 234.10, 'change': '+1.8%'},
        {'symbol': 'TEL.OL', 'name': 'Telenor ASA', 'price': 156.80, 'change': '-0.5%'}
    ]
    
    demo_analysis = {
        'recommendation': 'BUY',
        'confidence': '87%',
        'target_price': '375 NOK',
        'signals': ['Strong momentum', 'Good fundamentals', 'Positive sentiment']
    }
    
    return render_template('demo.html', 
                         stocks=demo_stocks, 
                         analysis=demo_analysis,
                         demo_mode=True)