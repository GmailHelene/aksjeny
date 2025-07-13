from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

# Import backup column handling
try:
    from app.models.backup_columns import add_missing_column_properties
    add_missing_column_properties()
except:
    pass  # Fail silently if backup not available

class DeviceTrialTracker(db.Model):
    """Track trial usage per device to prevent abuse by clearing cookies"""
    __tablename__ = 'device_trial_tracker'
    
    id = db.Column(db.Integer, primary_key=True)
    device_fingerprint = db.Column(db.String(32), unique=True, index=True, nullable=False)
    trial_start_time = db.Column(db.DateTime, default=datetime.utcnow)
    trial_used = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeviceTrialTracker {self.device_fingerprint}>'
    
    def trial_expired(self):
        """Check if trial period (10 minutes) has expired"""
        if not self.trial_start_time:
            return True
        return datetime.utcnow() - self.trial_start_time > timedelta(minutes=10)

class User(UserMixin, db.Model):
    __tablename__ = 'users'  # <-- Viktig!
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships - using backref instead of back_populates to avoid conflicts
    portfolios = db.relationship('Portfolio', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    watchlists = db.relationship('Watchlist', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Subscription fields
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_type = db.Column(db.String(20), default='free')  # 'free', 'monthly', 'yearly', 'lifetime'
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    trial_used = db.Column(db.Boolean, default=False)
    trial_start = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(128), nullable=True)  # For å lagre Stripe Customer ID
    reports_used_this_month = db.Column(db.Integer, default=0)  # Track consultant report usage
    last_reset_date = db.Column(db.DateTime, default=datetime.utcnow)  # Track monthly reset
    is_admin = db.Column(db.Boolean, default=False)  # Admin flag
    
    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def start_free_trial(self):
        """Start the free trial for this user"""
        if not self.trial_used:
            self.trial_used = True
            self.trial_start = datetime.utcnow()
            return True
        return False
    
    def is_in_trial_period(self):
        """Check if the user is in their free trial period (10 minutes)"""
        if not self.trial_used or not self.trial_start:
            return False
        
        # Trial period is 10 minutes
        trial_end = self.trial_start + timedelta(minutes=10)
        return datetime.utcnow() <= trial_end
    
    def has_active_subscription(self):
        """Check if the user has an active subscription"""
        # If user has a subscription and it's not expired
        if self.has_subscription and self.subscription_end:
            return datetime.utcnow() <= self.subscription_end
        
        # Or if they have a lifetime subscription
        if self.has_subscription and self.subscription_type == 'lifetime':
            return True
        
        # Or if they're in trial period
        return self.is_in_trial_period()
    
    def subscription_days_left(self):
        """Return the number of days left in the subscription"""
        if not self.has_subscription or not self.subscription_end:
            return 0
        
        delta = self.subscription_end - datetime.utcnow()
        return max(0, delta.days)
    
    def get_referral_code(self):
        """Get or create a referral code for this user"""
        from app.models.referral import Referral
        
        # Check if user already has a referral code
        existing_referral = Referral.query.filter_by(referrer_id=self.id).first()
        if existing_referral:
            return existing_referral.referral_code
        
        # Create new referral code
        new_referral = Referral(
            referrer_id=self.id,
            referral_code=Referral.generate_referral_code()
        )
        db.session.add(new_referral)
        db.session.commit()
        return new_referral.referral_code
    
    def get_completed_referrals_count(self):
        """Get number of successful referrals"""
        from app.models.referral import Referral
        return Referral.query.filter_by(referrer_id=self.id, is_completed=True).count()
    
    def get_available_referral_discounts(self):
        """Get available referral discounts for this user"""
        from app.models.referral import ReferralDiscount
        return ReferralDiscount.query.filter_by(
            user_id=self.id, 
            is_used=False
        ).all()
    
    def has_referral_discount(self):
        """Check if user has any available referral discounts"""
        discounts = self.get_available_referral_discounts()
        return len([d for d in discounts if d.is_valid()]) > 0

# NOTE: Portfolio and Watchlist relationships are defined in the models themselves
# No need to import them here as SQLAlchemy will resolve relationships automatically

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    if user_id is None or user_id == 'None':
        return None
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None