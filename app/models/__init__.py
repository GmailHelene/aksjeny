"""
Database models for Aksjeradar application
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Import db from the main app module
from .. import db

# Import existing models
from .user import User, DeviceTrialTracker
from .portfolio import Portfolio, PortfolioStock, Transaction
from .watchlist import Watchlist, WatchlistStock
from .trial_session import TrialSession
from .referral import Referral, ReferralDiscount
from .tip import StockTip
from .favorites import Favorites

# Add new models to __all__
__all__ = [
    'User', 
    'DeviceTrialTracker',
    'Portfolio', 
    'PortfolioStock', 
    'Transaction',
    'Watchlist', 
    'WatchlistStock',
    'TrialSession',
    'Referral',
    'ReferralDiscount',
    'StockTip',
    'Favorites',
    'LoginAttempt',
    'UserSession'
]

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    success = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<LoginAttempt {self.email} - {"Success" if self.success else "Failed"}>'

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic'))
    
    def __repr__(self):
        return f'<UserSession {self.user_id} - {"Active" if self.is_active else "Inactive"}>'
