#!/usr/bin/env python3
"""
Simple database creation script
"""
from flask import Flask
from app.extensions import db
from flask_migrate import Migrate
import os

def create_simple_app():
    """Create a minimal Flask app just for database creation"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'dev-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    return app

def create_tables():
    """Create all database tables"""
    print("Creating simple Flask app...")
    app = create_simple_app()
    
    with app.app_context():
        print("Importing models...")
        from app.models.user import User
        from app.models.portfolio import Portfolio, PortfolioStock
        from app.models.watchlist import Watchlist, WatchlistStock
        from app.models.notifications import (
            Notification, PriceAlert, NotificationSettings, 
            AIModel, PredictionLog
        )
        
        print("Creating tables...")
        db.create_all()
        
        print("Success! Database created.")
        
        # Check tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")

if __name__ == '__main__':
    create_tables()
