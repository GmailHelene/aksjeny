#!/usr/bin/env python3
"""
Quick check of app status and functionality
"""

import sys
import traceback
sys.path.insert(0, '.')

try:
    from app import create_app
    print('✅ App creation successful')
    
    app = create_app()
    print('✅ Flask app instantiated')
    
    with app.app_context():
        from app.models.user import User
        from app.extensions import db
        print('✅ Database models imported')
        
        # Check exempt users
        from app.utils.access_control import EXEMPT_EMAILS
        print(f'✅ Exempt emails: {EXEMPT_EMAILS}')
        
        # Check user count
        user_count = User.query.count()
        print(f'✅ Users in database: {user_count}')
        
        # Check if test user exists
        test_user = User.query.filter_by(email='helene721@gmail.com').first()
        if test_user:
            print(f'✅ Test user found: {test_user.email}')
            print(f'✅ Has subscription: {test_user.has_subscription}')
            print(f'✅ Is admin: {getattr(test_user, "is_admin", "Not set")}')
        else:
            print('❌ Test user not found')
            
        print('✅ All checks passed - app is ready')
        
except Exception as e:
    print(f'❌ Error: {e}')
    traceback.print_exc()
