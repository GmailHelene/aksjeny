#!/usr/bin/env python3
"""
Test Real-time WebSocket Implementation
=====================================

Test script to verify the real-time WebSocket data streaming system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.services.realtime_data_service import get_real_time_service
import threading
import time

def test_realtime_service():
    """Test the real-time service functionality"""
    print("🔧 Testing Real-time WebSocket Implementation...")
    
    # Create app instance
    app = create_app('development')
    
    with app.app_context():
        try:
            # Get real-time service
            rt_service = get_real_time_service()
            print(f"✅ Real-time service created: {rt_service}")
            
            # Start the service
            rt_service.start_background_updates()
            print("✅ Real-time service started")
            
            # Test market data generation
            time.sleep(2)
            
            # Get some market data
            market_summary = rt_service.get_market_summary()
            print(f"📊 Market summary: {market_summary}")
            
            # Get trending stocks
            trending = rt_service.get_trending_stocks(limit=5)
            print(f"🔥 Trending stocks: {len(trending)} stocks")
            
            # Test subscription
            session_id = "test_session_123"
            rt_service.subscribe_to_symbol(session_id, "EQNR")
            print(f"📡 Subscribed test session to EQNR")
            
            # Test price data
            price_data = rt_service.get_live_price("EQNR", "oslo")
            print(f"💰 EQNR price data: {price_data}")
            
            # Get statistics
            stats = rt_service.get_realtime_stats()
            print(f"📈 Service statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            print("✅ Real-time service test completed successfully!")
            
            # Stop the service
            rt_service.stop_background_updates()
            print("🛑 Real-time service stopped")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_websocket_handlers():
    """Test WebSocket handlers import"""
    print("\n🔧 Testing WebSocket handlers...")
    
    try:
        from app.routes.websocket_handlers import socketio
        print("✅ WebSocket handlers imported successfully")
        
        from app.routes.realtime_routes import realtime_bp
        print("✅ Realtime routes blueprint imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error importing WebSocket components: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Real-time WebSocket System Test")
    print("=" * 50)
    
    # Test WebSocket handlers
    ws_success = test_websocket_handlers()
    
    # Test real-time service
    rt_success = test_realtime_service()
    
    print("\n" + "=" * 50)
    if ws_success and rt_success:
        print("🎉 All tests passed! Real-time WebSocket system is ready!")
        print("\nNext steps:")
        print("1. Start the Flask application")
        print("2. Navigate to /realtime/dashboard")
        print("3. Test real-time market data streaming")
        print("4. Create price alerts and test notifications")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
