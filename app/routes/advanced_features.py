"""
Advanced Features Blueprint
Implementing competitive features inspired by major financial platforms
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from ..services.external_data_service import ExternalDataService
from ..services.competitive_analysis_service import CompetitiveFeatureService
from ..utils.access_control import access_required  # SECURITY FIX: Corrected import path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

advanced_features = Blueprint('advanced_features', __name__, url_prefix='/advanced')

# Initialize services - delay translation service import
external_data_service = ExternalDataService()
competitive_service = CompetitiveFeatureService()

@advanced_features.route('/')
@login_required
def index():
    """Advanced features dashboard"""
    try:
        # Import translation function safely within request context
        try:
            from ..services.translation_service import t
        except ImportError:
            def t(key, fallback=None, **kwargs):
                return fallback or key
        
        # Get comprehensive market data
        market_data = {
            'oslo_bors': external_data_service.get_oslo_bors_real_time(),
            'global_markets': external_data_service.get_global_markets_overview(),
            'crypto': external_data_service.get_crypto_overview(),
            'currencies': external_data_service.get_currency_rates(),
            'economic_indicators': external_data_service.get_economic_indicators()
        }
        
        # Get competitive features analysis
        competitive_features = competitive_service.get_missing_features()
        
        return render_template('advanced_features/dashboard.html',
                             market_data=market_data,
                             competitive_features=competitive_features)
    
    except Exception as e:
        logger.error(f"Error loading advanced features: {e}")
        return render_template('advanced_features/dashboard.html',
                             market_data={},
                             competitive_features=[],
                             error=str(e))

@advanced_features.route('/api/market-data')
@access_required  # SECURITY FIX: Added missing access control
def market_overview():
    """Real-time market overview API endpoint"""
    try:
        data = {
            'oslo_bors': external_data_service.get_oslo_bors_real_time(),
            'indices': external_data_service.get_oslo_bors_indices(),
            'global_markets': external_data_service.get_global_markets_overview(),
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_features.route('/crypto-dashboard')
@login_required
def crypto_dashboard():
    """Cryptocurrency tracking dashboard"""
    try:
        crypto_data = external_data_service.get_crypto_overview()
        
        return render_template('advanced_features/crypto_dashboard.html',
                             crypto_data=crypto_data)
    
    except Exception as e:
        logger.error(f"Error loading crypto dashboard: {e}")
        return render_template('advanced_features/crypto_dashboard.html',
                             crypto_data={},
                             error=str(e))

@advanced_features.route('/currency-converter')
@access_required  # SECURITY FIX: Added missing access control
def currency_converter():
    """Advanced currency converter"""
    try:
        rates = external_data_service.get_currency_rates()
        
        return render_template('advanced_features/currency_converter.html',
                             rates=rates)
    
    except Exception as e:
        logger.error(f"Error loading currency converter: {e}")
        return render_template('advanced_features/currency_converter.html',
                             rates={},
                             error=str(e))

@advanced_features.route('/economic-calendar')
@login_required  
def economic_calendar():
    """Economic calendar with key indicators"""
    try:
        indicators = external_data_service.get_economic_indicators()
        
        return render_template('advanced_features/economic_calendar.html',
                             indicators=indicators)
    
    except Exception as e:
        logger.error(f"Error loading economic calendar: {e}")
        return render_template('advanced_features/economic_calendar.html',
                             indicators={},
                             error=str(e))

@advanced_features.route('/competitive-analysis')
@login_required
def competitive_analysis():
    """Show competitive analysis and missing features"""
    try:
        features = competitive_service.get_missing_features()
        
        return render_template('advanced_features/competitive_analysis.html',
                             features=features)
    
    except Exception as e:
        logger.error(f"Error loading competitive analysis: {e}")
        return render_template('advanced_features/competitive_analysis.html',
                             features=[],
                             error=str(e))
