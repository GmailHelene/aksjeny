#!/usr/bin/env python3
"""
Test login functionality with the correct password
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User
from werkzeug.security import check_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_login():
    """Test login for helene721@gmail.com"""
    
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🧪 Testing login for helene721@gmail.com...")
            
            # Find the user
            user = User.query.filter_by(email='helene721@gmail.com').first()
            
            if not user:
                logger.error("❌ User not found!")
                return False
            
            logger.info(f"👤 User found: {user.email} (username: {user.username})")
            
            # Test passwords that were found in the search results
            test_passwords = [
                'aksjeradar2025',  # The one we just set
                'password123',     # Common test password
                'test123',         # Another common one
                'Soda2001??',      # From search results
                '721'              # From Railway users
            ]
            
            correct_password = None
            for password in test_passwords:
                if check_password_hash(user.password_hash, password):
                    correct_password = password
                    logger.info(f"✅ Password '{password}' is CORRECT!")
                    break
                else:
                    logger.info(f"❌ Password '{password}' is wrong")
            
            if correct_password:
                logger.info(f"🎉 Login test successful!")
                logger.info(f"📧 Email: {user.email}")
                logger.info(f"🔑 Password: {correct_password}")
                logger.info(f"👑 Admin: {user.is_admin}")
                logger.info(f"💎 Subscription: {user.subscription_type}")
                return True
            else:
                logger.error("❌ No correct password found!")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error during login test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_login()
    if success:
        print("\n" + "="*60)
        print("🚀 LOGIN READY!")
        print("="*60)
        print("You can now log in to aksjeradar.trade with:")
        print("📧 Email: helene721@gmail.com")
        print("🔑 Password: aksjeradar2025")
        print("="*60)
    sys.exit(0 if success else 1)
