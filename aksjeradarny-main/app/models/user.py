from ..extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Subscription fields
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_type = db.Column(db.String(20))
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    
    # Trial fields
    trial_used = db.Column(db.Boolean, default=False)
    trial_start = db.Column(db.DateTime)
    
    # Stripe integration
    stripe_customer_id = db.Column(db.String(100))
    
    # Usage tracking
    reports_used_this_month = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.DateTime, default=datetime.utcnow)
    
        # User permissions
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self):
        """Generate password reset token - store in session/cache instead of DB"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_reset_token(token):
        """Verify reset token from session/cache"""
        # This should use Flask session or Redis
        return None

@login_manager.user_loader
def load_user(user_id):
    """Load user safely with error handling"""
    if user_id is None or user_id == 'None':
        return None
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        # Log error but don't crash
        return None