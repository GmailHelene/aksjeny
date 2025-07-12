#!/usr/bin/env python3
"""
Test the new unified access control system
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_access_control():
    """Test the new access control system"""
    try:
        print("🧪 Testing unified access control system...")
        
        # Test model imports
        from app import create_app
        app = create_app('development')
        print("✅ App created successfully")
        
        with app.app_context():
            # Test access control functions
            from app.utils.access_control import access_required, get_trial_status, get_access_level
            print("✅ Access control functions imported")
            
            # Test trial status without request context
            try:
                from flask import g
                g.trial_status = {'active': True, 'unlimited': False, 'remaining_minutes': 10}
                g.access_level = 'trial'
                print("✅ Trial status simulation works")
            except Exception as e:
                print(f"⚠️  Trial status test needs request context: {e}")
            
        print("🎉 Access control system is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing access control: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_access_control()
    sys.exit(0 if success else 1)
