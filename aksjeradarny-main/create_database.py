#!/usr/bin/env python3
"""
Script to create database and tables
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db

def create_database():
    """Create the database and all tables"""
    print("Creating Flask app...")
    app = create_app()
    
    with app.app_context():
        print("Importing all models...")
        # Import all models to ensure they're registered with SQLAlchemy
        from app.models.user import User
        from app.models.portfolio import Portfolio, PortfolioStock
        from app.models.watchlist import Watchlist, WatchlistStock
        from app.models.notifications import (
            Notification, PriceAlert, NotificationSettings, 
            AIModel, PredictionLog
        )
        
        print("Creating database tables...")
        db.create_all()
        
        print("Database created successfully!")
        print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Print table names
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {', '.join(tables)}")

if __name__ == '__main__':
    create_database()
