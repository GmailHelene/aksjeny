from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
import json
from datetime import datetime, timedelta
from ..services.performance_monitor import PerformanceMonitor
from ..models.user import User
from ..models.portfolio import Portfolio

admin = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Du må logge inn for å få tilgang til admin-siden.', 'error')
            return redirect(url_for('main.login'))
        
        # Check if user has admin rights - safe check
        is_admin = getattr(current_user, 'is_admin', False)
        if not is_admin:
            flash('Tilgang nektet. Admin-rettigheter kreves.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    return render_template('admin/dashboard.html')

@admin.route('/admin/performance')
@login_required
@admin_required
def performance_stats():
    """Vis ytelsesstatistikk"""
    try:
        monitor = PerformanceMonitor()
        
        # Hent statistikk for siste 24 timer
        stats = monitor.get_performance_stats(hours=24)
        
        # Hent feillog
        error_log = monitor.get_error_log(limit=50)
        
        return render_template('admin/performance.html', 
                             stats=stats, 
                             error_log=error_log)
    except Exception as e:
        flash(f'Feil ved henting av ytelsesstatistikk: {str(e)}', 'error')
        return render_template('admin/performance.html', 
                             stats={'total_requests': 0, 'avg_response_time': 0, 'error_count': 0, 'error_rate': 0, 'slowest_endpoints': [], 'most_used_endpoints': []}, 
                             error_log=[])

@admin.route('/admin/api/performance')
@login_required
@admin_required
def api_performance_stats():
    """API for å hente ytelsesstatistikk"""
    try:
        monitor = PerformanceMonitor()
        hours = request.args.get('hours', 24, type=int)
        
        stats = monitor.get_performance_stats(hours=hours)
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin.route('/admin/api/errors')
@login_required
@admin_required
def api_error_log():
    """API for å hente feillog"""
    monitor = PerformanceMonitor()
    limit = request.args.get('limit', 50, type=int)
    
    error_log = monitor.get_error_log(limit=limit)
    
    return jsonify({
        'success': True,
        'data': error_log
    })

@admin.route('/admin/users')
@login_required
@admin_required
def user_management():
    """Brukerhåndtering"""
    # Dette kan utvides senere
    return render_template('admin/users.html')

@admin.route('/admin/system')
@login_required
@admin_required
def system_status():
    """Systemstatus og helse"""
    return render_template('admin/system.html')
