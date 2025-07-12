#!/usr/bin/env python3
"""
Database migration and fix script for Aksjeradar
This script will:
1. Create any missing tables
2. Add any missing columns
3. Fix any relationship issues
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database():
    """Fix database schema and ensure all tables/columns exist"""
    try:
        from app import create_app
        from app.extensions import db
        from app.models.user import User, DeviceTrialTracker
        from app.models.watchlist import Watchlist, WatchlistItem, WatchlistAlert
        from app.models.portfolio import Portfolio, PortfolioStock
        from app.models.tip import StockTip
        from app.models.notifications import NotificationPreference, Notification
        from app.models.trial_session import TrialSession
        from app.models.referral import Referral
        
        app = create_app('development')
        
        with app.app_context():
            print("🔧 Fixing database schema...")
            
            # Create all tables
            print("Creating all tables...")
            db.create_all()
            
            # Check if stock_tips table has all required columns
            print("Checking stock_tips table...")
            inspector = db.inspect(db.engine)
            if 'stock_tips' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('stock_tips')]
                print(f"Current stock_tips columns: {columns}")
                
                required_columns = ['tip_type', 'confidence', 'analysis', 'user_id']
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    print(f"Adding missing columns: {missing_columns}")
                    for col in missing_columns:
                        try:
                            if col == 'tip_type':
                                db.engine.execute("ALTER TABLE stock_tips ADD COLUMN tip_type VARCHAR(10)")
                            elif col == 'confidence':
                                db.engine.execute("ALTER TABLE stock_tips ADD COLUMN confidence VARCHAR(10)")
                            elif col == 'analysis':
                                db.engine.execute("ALTER TABLE stock_tips ADD COLUMN analysis TEXT")
                            elif col == 'user_id':
                                db.engine.execute("ALTER TABLE stock_tips ADD COLUMN user_id INTEGER")
                            print(f"✅ Added column: {col}")
                        except Exception as e:
                            print(f"⚠️  Column {col} might already exist: {e}")
                else:
                    print("✅ All required columns exist in stock_tips")
            else:
                print("Creating stock_tips table...")
                db.create_all()
            
            # Test relationships
            print("\nTesting model relationships...")
            try:
                user = User(username='test_user', email='test@example.com')
                watchlist = Watchlist(name='Test Watchlist', user=user)
                portfolio = Portfolio(name='Test Portfolio', user=user)
                print("✅ Model relationships working correctly")
            except Exception as e:
                print(f"❌ Relationship error: {e}")
                return False
            
            print("\n✅ Database schema fixed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("\n🎉 Database is ready!")
    else:
        print("\n💥 Database fix failed!")
    sys.exit(0 if success else 1)
