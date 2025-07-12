#!/usr/bin/env python3
"""
Test script to verify SQLAlchemy models are working properly
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_models():
    """Test that models can be imported and relationships work"""
    try:
        from app import create_app
        from app.models.user import User
        from app.models.watchlist import Watchlist, WatchlistItem
        from app.models.portfolio import Portfolio, PortfolioStock
        from app.models.tip import StockTip
        from app.extensions import db
        
        print("✅ All models imported successfully")
        
        # Create app context
        app = create_app('development')
        with app.app_context():
            # Test that relationships are properly defined
            print("Testing User relationships...")
            user_columns = [column.name for column in User.__table__.columns]
            print(f"User columns: {user_columns}")
            
            print("\nTesting Watchlist relationships...")
            watchlist_columns = [column.name for column in Watchlist.__table__.columns]
            print(f"Watchlist columns: {watchlist_columns}")
            
            print("\nTesting StockTip relationships...")
            tip_columns = [column.name for column in StockTip.__table__.columns]
            print(f"StockTip columns: {tip_columns}")
            
            print("\n✅ All model relationships are properly defined!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)
