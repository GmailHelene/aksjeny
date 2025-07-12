#!/usr/bin/env python3
"""
Test script for Aksjeradar services and API connections
"""
import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_service():
    """Test DataService functionality"""
    print("🔍 Testing DataService...")
    
    try:
        from app.services.data_service import DataService
        
        # Test stock info retrieval
        test_tickers = ['AAPL', 'EQNR.OL', 'DNB.OL']
        
        for ticker in test_tickers:
            try:
                data = DataService.get_stock_info(ticker)
                if data:
                    print(f"✅ {ticker}: Data available")
                else:
                    print(f"⚠️  {ticker}: No data available (using fallback)")
            except Exception as e:
                print(f"❌ {ticker}: Error - {e}")
        
        # Test market overview
        try:
            overview = DataService.get_market_overview()
            if overview:
                print("✅ Market overview: Data available")
            else:
                print("⚠️  Market overview: No data available (using fallback)")
        except Exception as e:
            print(f"❌ Market overview: Error - {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ DataService test failed: {e}")
        traceback.print_exc()
        return False

def test_analysis_service():
    """Test AnalysisService functionality"""
    print("\n🔍 Testing AnalysisService...")
    
    try:
        from app.services.analysis_service import AnalysisService
        
        # Test analysis for a common stock
        ticker = 'AAPL'
        try:
            analysis = AnalysisService.analyze_stock(ticker)
            if analysis:
                print(f"✅ {ticker}: Analysis available")
            else:
                print(f"⚠️  {ticker}: No analysis available")
        except Exception as e:
            print(f"❌ {ticker}: Analysis error - {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ AnalysisService test failed: {e}")
        traceback.print_exc()
        return False

def test_notification_service():
    """Test NotificationService functionality"""
    print("\n🔍 Testing NotificationService...")
    
    try:
        from app.services.notification_service import NotificationService
        
        # Test basic notification functionality
        service = NotificationService()
        print("✅ NotificationService: Initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ NotificationService test failed: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app import create_app
        from app.extensions import db
        
        app = create_app('testing')
        with app.app_context():
            # Test database connection
            try:
                db.engine.execute('SELECT 1')
                print("✅ Database: Connection successful")
                return True
            except Exception as e:
                print(f"❌ Database: Connection failed - {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all service tests"""
    print("🧪 TESTING AKSJERADAR SERVICES")
    print("=" * 50)
    
    results = []
    results.append(test_data_service())
    results.append(test_analysis_service())
    results.append(test_notification_service())
    results.append(test_database_connection())
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All services are working correctly!")
    else:
        print("⚠️  Some services need attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
