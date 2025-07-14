"""
Advanced Analytics Blueprint
Handles ML predictions, portfolio optimization, and risk management
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import logging

logger = logging.getLogger(__name__)

# Create blueprint
advanced_analytics = Blueprint('advanced_analytics', __name__)

@advanced_analytics.route('/')
@login_required
def index():
    """Advanced analytics dashboard"""
    return render_template('advanced_analytics.html')

@advanced_analytics.route('/dashboard')
@login_required  
def dashboard():
    """Advanced analytics dashboard (alias for index)"""
    return render_template('advanced_analytics.html')

@advanced_analytics.route('/ml-predictions')
@login_required
def ml_predictions():
    """ML predictions page"""
    return render_template('advanced_analytics.html', active_tab='ml-predictions')

@advanced_analytics.route('/portfolio-optimization')
@login_required
def portfolio_optimization():
    """Portfolio optimization page"""
    return render_template('advanced_analytics.html', active_tab='portfolio-optimization')

@advanced_analytics.route('/risk-management')
@login_required
def risk_management():
    """Risk management page"""
    return render_template('advanced_analytics.html', active_tab='risk-management')

# Error handlers for this blueprint
@advanced_analytics.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors within advanced analytics"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Siden ble ikke funnet"), 404

@advanced_analytics.errorhandler(500)
def internal_error(error):
    """Handle 500 errors within advanced analytics"""
    logger.error(f"Advanced analytics internal error: {error}")
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Intern serverfeil"), 500
