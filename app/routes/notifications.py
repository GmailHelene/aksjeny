"""
Notification routes for real-time user alerts
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models.notifications import Notification
from ..models.user import User
from ..services.notification_service import notification_service
from ..extensions import db
from ..utils.access_control import access_required
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
        # Get user's notification preferences using new methods
        user_settings = current_user.get_notification_settings()
        
        preferences = {
            'email_enabled': user_settings.get('email_enabled', True),
            'push_enabled': user_settings.get('push_enabled', False),
            'price_alerts': user_settings.get('price_alerts', True),
            'insider_alerts': user_settings.get('insider_alerts', True),
            'earnings_alerts': user_settings.get('earnings_alerts', True),
            'analyst_alerts': user_settings.get('analyst_alerts', True),
            'volume_alerts': user_settings.get('volume_alerts', False),
            'daily_summary': user_settings.get('daily_summary', False),
            'market_news': user_settings.get('market_news', False),
            'system_updates': user_settings.get('system_updates', True)
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
        
        # Get current settings
        current_settings = current_user.get_notification_settings()
        
        # Update settings with new values
        current_settings.update({
            'email_enabled': data.get('email_enabled', True),
            'push_enabled': data.get('push_enabled', False),
            'price_alerts': data.get('price_alerts', True),
            'insider_alerts': data.get('insider_alerts', True),
            'earnings_alerts': data.get('earnings_alerts', True),
            'analyst_alerts': data.get('analyst_alerts', True),
            'volume_alerts': data.get('volume_alerts', False),
            'daily_summary': data.get('daily_summary', False),
            'market_news': data.get('market_news', False),
            'system_updates': data.get('system_updates', True)
        })
        
        # Save updated settings
        success = current_user.update_notification_settings(current_settings)
        
        if success:
            return jsonify({'success': True, 'message': 'Innstillinger oppdatert'})
        else:
            return jsonify({'success': False, 'error': 'Kunne ikke oppdatere innstillinger'})
            
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
    """User notification preferences API"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            # Update user's language setting
            if 'language' in data:
                current_user.set_language(data['language'])
            
            # Update notification settings using the new notification_settings column
            current_settings = current_user.get_notification_settings()
            
            # Update settings from request data
            if 'display_mode' in data:
                current_settings['display_mode'] = data['display_mode']
            if 'number_format' in data:
                current_settings['number_format'] = data['number_format']
            if 'dashboard_widgets' in data:
                current_settings['dashboard_widgets'] = data['dashboard_widgets']
            if 'email_enabled' in data:
                current_settings['email_enabled'] = data['email_enabled']
            if 'push_enabled' in data:
                current_settings['push_enabled'] = data['push_enabled']
            
            # Save updated settings
            success = current_user.update_notification_settings(current_settings)
            
            if success:
                return jsonify({'success': True, 'message': 'Preferanser oppdatert'})
            else:
                return jsonify({'success': False, 'error': 'Kunne ikke lagre preferanser'})
        
        # GET request - return current preferences
        current_settings = current_user.get_notification_settings()
        
        # Return preferences with safe defaults
        preferences = {
            'language': current_user.get_language(),
            'display_mode': current_settings.get('display_mode', 'light'),
            'number_format': current_settings.get('number_format', 'norwegian'),
            'dashboard_widgets': current_settings.get('dashboard_widgets', 'default'),
            'email_enabled': current_settings.get('email_enabled', True),
            'push_enabled': current_settings.get('push_enabled', False)
        }
        
        return jsonify(preferences)
        
    except Exception as e:
        logger.error(f"Error in user preferences: {e}")
        return jsonify({'success': False, 'error': 'Kunne ikke hente preferanser'})
