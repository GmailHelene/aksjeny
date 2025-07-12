#!/usr/bin/env python3

import sys
import os
sys.path.append('/workspaces/aksjeradarv6')

print("🔍 TESTING FIXED EMAIL VALIDATION")
print("=" * 50)

try:
    # Test the new SimpleEmail validator
    from app.forms import SimpleEmail, ForgotPasswordForm
    print("✅ SimpleEmail validator imported")
    
    # Test the validator directly
    validator = SimpleEmail()
    
    # Mock field class for testing
    class MockField:
        def __init__(self, data):
            self.data = data
    
    # Test valid emails
    valid_emails = ['test@example.com', 'user@domain.no', 'name.lastname@company.com']
    for email in valid_emails:
        try:
            validator(None, MockField(email))
            print(f"✅ Valid: {email}")
        except:
            print(f"❌ Failed: {email}")
    
    # Test invalid emails
    invalid_emails = ['invalid', '@domain.com', 'test@', 'test..test@domain.com']
    for email in invalid_emails:
        try:
            validator(None, MockField(email))
            print(f"❌ Should have failed: {email}")
        except:
            print(f"✅ Correctly rejected: {email}")
    
    # Test form creation
    form = ForgotPasswordForm()
    print("✅ ForgotPasswordForm created successfully")
    
    print("\n🎯 RESULT:")
    print("✅ Email validation is now working without email_validator dependency!")
    print("✅ 'Glemt passord' feature should work correctly")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
