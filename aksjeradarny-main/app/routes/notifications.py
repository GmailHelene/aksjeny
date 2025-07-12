"""
Notification routes for real-time user alerts
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.notifications import Notification
from app.services.notification_service import notification_service
from app.extensions import db
from app.utils.access_control import access_required
from datetime import datetime, timedelta
import logging

notifications_bp = Blueprint('notifications', __name__)
logger = logging.getLogger(__name__)

@notifications_bp.route('/')
@login_required
def index():
    """Main notifications page"""
    try:
        # Get filter parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = Notification.query.filter_by(user_id=current_user.id)
        
        if unread_only:
            query = query.filter_by(read=False)
        
        # Order by newest first
        query = query.order_by(Notification.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        notifications = pagination.items
        
        # Get summary statistics
        total_count = Notification.query.filter_by(user_id=current_user.id).count()
        unread_count = Notification.query.filter_by(user_id=current_user.id, read=False).count()
        
        # Get counts by type
        type_counts = db.session.query(
            Notification.type, 
            db.func.count(Notification.id)
        ).filter_by(user_id=current_user.id).group_by(Notification.type).all()
        
        summary = {
            'total': total_count,
            'unread': unread_count,
            'types': dict(type_counts),
            'recent_activity': Notification.query.filter_by(user_id=current_user.id)\
                .filter(Notification.created_at >= datetime.utcnow() - timedelta(days=7)).count(),
            'priority_breakdown': {
                'high': Notification.query.filter_by(user_id=current_user.id, priority='high').count(),
                'medium': Notification.query.filter_by(user_id=current_user.id, priority='medium').count(),
                'low': Notification.query.filter_by(user_id=current_user.id, priority='low').count()
            }
        }
        
        return render_template('notifications/index.html',
                             notifications=notifications,
                             pagination=pagination,
                             unread_only=unread_only,
                             summary=summary)
    except Exception as e:
        logger.error(f"Error loading notifications: {str(e)}")
        flash('Error loading notifications. Please try again later.', 'error')
        return redirect(url_for('main.index'))

@notifications_bp.route('/api/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def api_mark_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id, 
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
        
        notification.read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/mark-unread/<int:notification_id>', methods=['POST'])
@login_required
def api_mark_unread(notification_id):
    """Mark notification as unread"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()

        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404

        notification.read = False
        notification.read_at = None
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error marking notification as unread: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/mark-all-read', methods=['POST'])
@login_required
def api_mark_all_read():
    """Mark all notifications as read"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id, 
            read=False
        ).update({
            'read': True,
            'read_at': datetime.utcnow()
        })
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/delete/<int:notification_id>', methods=['DELETE'])
@login_required
def api_delete(notification_id):
    """Delete a notification"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404
        
        db.session.delete(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/unread-count')
@login_required
def api_unread_count():
    """Get unread notification count"""
    try:
        count = Notification.query.filter_by(
            user_id=current_user.id,
            read=False
        ).count()
        
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/settings')
@login_required
def settings():
    """Notification settings page"""
    try:
        # Get user's notification preferences
        preferences = {
            'email_enabled': getattr(current_user, 'email_notifications', True),
            'push_enabled': getattr(current_user, 'push_notifications', False),
            'price_alerts': getattr(current_user, 'price_alerts_enabled', True),
            'insider_alerts': getattr(current_user, 'insider_alerts_enabled', True),
            'earnings_alerts': getattr(current_user, 'earnings_alerts_enabled', True),
            'analyst_alerts': getattr(current_user, 'analyst_alerts_enabled', True),
            'volume_alerts': getattr(current_user, 'volume_alerts_enabled', False),
            'daily_summary': getattr(current_user, 'daily_summary_enabled', False),
            'market_news': getattr(current_user, 'market_news_enabled', False),
            'system_updates': getattr(current_user, 'system_updates_enabled', True)
        }
        
        return render_template('notifications/settings.html', preferences=preferences)
    except Exception as e:
        logger.error(f"Error loading notification settings: {str(e)}")
        flash('Error loading settings. Please try again later.', 'error')
        return redirect(url_for('notifications.index'))

@notifications_bp.route('/api/settings', methods=['POST'])
@login_required
def api_update_settings():
    """Update notification settings"""
    try:
        data = request.get_json()
        
        # Update user preferences
        if hasattr(current_user, 'email_notifications'):
            current_user.email_notifications = data.get('email_enabled', True)
        if hasattr(current_user, 'push_notifications'):
            current_user.push_notifications = data.get('push_enabled', False)
        if hasattr(current_user, 'price_alerts_enabled'):
            current_user.price_alerts_enabled = data.get('price_alerts', True)
        if hasattr(current_user, 'insider_alerts_enabled'):
            current_user.insider_alerts_enabled = data.get('insider_alerts', True)
        if hasattr(current_user, 'earnings_alerts_enabled'):
            current_user.earnings_alerts_enabled = data.get('earnings_alerts', True)
        if hasattr(current_user, 'analyst_alerts_enabled'):
            current_user.analyst_alerts_enabled = data.get('analyst_alerts', True)
        if hasattr(current_user, 'volume_alerts_enabled'):
            current_user.volume_alerts_enabled = data.get('volume_alerts', False)
        if hasattr(current_user, 'daily_summary_enabled'):
            current_user.daily_summary_enabled = data.get('daily_summary', False)
        if hasattr(current_user, 'market_news_enabled'):
            current_user.market_news_enabled = data.get('market_news', False)
        if hasattr(current_user, 'system_updates_enabled'):
            current_user.system_updates_enabled = data.get('system_updates', True)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Innstillinger oppdatert'})
    except Exception as e:
        logger.error(f"Error updating notification settings: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/test', methods=['POST'])
@login_required
def api_test_notification():
    """Send a test notification"""
    try:
        notification_service.create_notification(
            user_id=current_user.id,
            notification_type='SYSTEM_UPDATE',
            title='Test Varsel',
            message='Dette er et testvarsel for å verifisere at innstillingene dine fungerer korrekt.',
            priority='medium'
        )
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/push_subscription', methods=['POST'])
@login_required
def save_push_subscription():
    """Save push notification subscription"""
    try:
        subscription_data = request.get_json()
        
        # Store the push subscription data
        # This would typically be saved to a user settings model
        import json
        if hasattr(current_user, 'push_subscription'):
            current_user.push_subscription = json.dumps(subscription_data)
            current_user.push_notifications = True
            db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error saving push subscription: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/clear-read', methods=['POST'])
@login_required
def api_clear_read():
    """Clear all read notifications"""
    try:
        Notification.query.filter_by(
            user_id=current_user.id,
            read=True
        ).delete()
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error clearing read notifications: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Web interface routes
notifications_web_bp = Blueprint('notifications_web', __name__, url_prefix='/notifications')

@notifications_web_bp.route('/')
@login_required
def notifications_page():
    """Notifications page"""
    return render_template('notifications/index.html')

@notifications_web_bp.route('/settings')
@login_required
def settings_page():
    """Notification settings page"""
    return render_template('notifications/settings.html')

@notifications_bp.route('/api/notifications', methods=['GET'])
@login_required
def api_get_notifications():
    """Get all notifications for the user"""
    try:
        notifications = Notification.query.filter_by(user_id=current_user.id).all()
        return jsonify({'success': True, 'notifications': [n.to_dict() for n in notifications]})
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@notifications_bp.route('/api/user/preferences', methods=['GET', 'POST'])
@login_required
def user_preferences():
    """Get or update user preferences (language, display, widgets, etc.)"""
    from app.models.notifications import NotificationSettings
    settings = NotificationSettings.query.filter_by(user_id=current_user.id).first()
    if request.method == 'GET':
        if not settings:
            return jsonify({'error': 'No preferences found'}), 404
        return jsonify({
            'language': settings.language,
            'display_mode': settings.display_mode,
            'number_format': settings.number_format,
            'dashboard_widgets': settings.dashboard_widgets
        })
    # POST: update
    data = request.get_json()
    if not settings:
        settings = NotificationSettings(user_id=current_user.id)
        db.session.add(settings)
    settings.language = data.get('language', settings.language)
    settings.display_mode = data.get('display_mode', settings.display_mode)
    settings.number_format = data.get('number_format', settings.number_format)
    settings.dashboard_widgets = data.get('dashboard_widgets', settings.dashboard_widgets)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Preferanser oppdatert'})
