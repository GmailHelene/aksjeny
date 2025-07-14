from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from ..services.data_service import DataService
from ..services.analysis_service import AnalysisService
from ..utils.access_control import access_required, pro_required
from datetime import datetime, timedelta
import logging

pro_tools = Blueprint('pro_tools', __name__, url_prefix='/pro-tools')
logger = logging.getLogger(__name__)

@pro_tools.route('/')
@login_required
@pro_required
def index():
    """Pro-verktøy oversikt"""
    try:
        # Hent statistikk for pro-verktøy
        stats = {
            'screener_searches': 15,
            'custom_alerts': 8,
            'portfolio_analyses': 3,
            'export_reports': 12
        }
        
        return render_template('pro/index.html', stats=stats)
    except Exception as e:
        logger.error(f"Error loading pro tools index: {e}")
        flash('Kunne ikke laste pro-verktøy. Prøv igjen senere.', 'error')
        return redirect(url_for('main.index'))

@pro_tools.route('/screener')
@login_required
@pro_required
def advanced_screener():
    """Avansert aksje-screener"""
    try:
        # Hent screening kriterier
        criteria = request.args.to_dict()
        
        # Standard screening
        results = []
        if criteria:
            results = AnalysisService.advanced_screener(criteria)
        
        return render_template('pro/screener.html', 
                             criteria=criteria, 
                             results=results)
    except Exception as e:
        logger.error(f"Error in advanced screener: {e}")
        flash('Feil ved kjøring av screener. Prøv igjen.', 'error')
        return render_template('pro/screener.html', criteria={}, results=[])

@pro_tools.route('/alerts')
@login_required
@pro_required
def price_alerts():
    """Pris-varsler og alarmer"""
    try:
        # Hent brukerens aktive varsler
        user_alerts = []  # TODO: Implementer database henting
        
        return render_template('pro/alerts.html', alerts=user_alerts)
    except Exception as e:
        logger.error(f"Error loading alerts: {e}")
        flash('Kunne ikke laste varsler.', 'error')
        return render_template('pro/alerts.html', alerts=[])

@pro_tools.route('/portfolio-analyzer')
@login_required
@pro_required
def portfolio_analyzer():
    """Avansert porteføljeanalyse"""
    try:
        # Hent brukerens porteføljer
        portfolios = []  # TODO: Implementer database henting
        
        analysis_results = None
        if request.args.get('portfolio_id'):
            # Kjør analyse på valgt portefølje
            analysis_results = {
                'risk_metrics': {
                    'beta': 1.2,
                    'volatility': 0.18,
                    'sharpe_ratio': 1.4,
                    'max_drawdown': 0.12
                },
                'diversification': {
                    'sector_concentration': 0.35,
                    'geographic_exposure': {
                        'Norway': 0.6,
                        'USA': 0.3,
                        'Europe': 0.1
                    }
                },
                'performance': {
                    'total_return': 0.15,
                    'annual_return': 0.12,
                    'benchmark_comparison': 0.03
                }
            }
        
        return render_template('pro/portfolio_analyzer.html', 
                             portfolios=portfolios,
                             analysis=analysis_results)
    except Exception as e:
        logger.error(f"Error in portfolio analyzer: {e}")
        flash('Feil ved porteføljeanalyse.', 'error')
        return render_template('pro/portfolio_analyzer.html', 
                             portfolios=[], analysis=None)

@pro_tools.route('/export')
@login_required
@pro_required
def export_tools():
    """Eksport-verktøy for data og rapporter"""
    try:
        return render_template('pro/export.html')
    except Exception as e:
        logger.error(f"Error loading export tools: {e}")
        flash('Kunne ikke laste eksport-verktøy.', 'error')
        return redirect(url_for('pro_tools.index'))

@pro_tools.route('/api/screener', methods=['POST'])
@login_required
@pro_required
def api_screener():
    """API for avansert screening"""
    try:
        criteria = request.get_json()
        results = AnalysisService.advanced_screener(criteria)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        logger.error(f"API screener error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@pro_tools.route('/api/create-alert', methods=['POST'])
@login_required
@pro_required
def create_alert():
    """Opprett nytt pris-varsel"""
    try:
        data = request.get_json()
        # TODO: Implementer database lagring
        return jsonify({'success': True, 'alert_id': 'mock_id'})
    except Exception as e:
        logger.error(f"Create alert error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
