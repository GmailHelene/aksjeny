import math
import pandas as pd
from flask import Blueprint, render_template, request, flash
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from ..services.data_service import DataService
from ..services.analysis_service import AnalysisService
from ..services.usage_tracker import usage_tracker
from ..utils.access_control import access_required, demo_access
from ..models.favorites import Favorites
from ..services.notification_service import NotificationService
import logging

dashboard = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard.route('/financial-dashboard')
@demo_access
def financial_dashboard():
    """Financial dashboard with working tabs"""
    try:
        # Get data for all tabs with proper error handling
        dashboard_data = {
            'overview': {
                'oslo_stocks': DataService.get_oslo_bors_overview() or {},
                'global_stocks': DataService.get_global_stocks_overview() or {},
                'market_summary': DataService.get_market_overview() or {}
            },
            'stocks': DataService.get_oslo_bors_overview() or {},
            'crypto': DataService.get_crypto_overview() or {},
            'currency': DataService.get_currency_overview() or {},
            'news': DataService.get_latest_news() or [],
            'insider_trading': DataService.get_insider_trading_data() or []
        }
        
        # Get active tab from query parameter
        active_tab = request.args.get('tab', 'overview')
        
        return render_template('dashboard/financial.html',
                             data=dashboard_data,
                             active_tab=active_tab)
                             
    except Exception as e:
        logger.error(f"Error in financial dashboard: {e}")
        flash('Kunne ikke laste dashboard data.', 'error')
        return render_template('dashboard/financial.html',
                             data={},
                             active_tab='overview',
                             error="Dashboard kunne ikke lastes")