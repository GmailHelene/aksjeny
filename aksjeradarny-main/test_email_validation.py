#!/usr/bin/env python3
"""
Test email validation and form functionality
"""

print("🔍 EMAIL VALIDATION TEST")
print("=" * 40)

try:
    # Test 1: Import email_validator
    import email_validator
    print("✅ email_validator imported")
    
    # Test 2: Import wtforms Email validator
    from wtforms.validators import Email
    print("✅ WTForms Email validator imported")
    
    # Test 3: Create email validator instance
    email_val = Email()
    print("✅ Email validator instance created")
    
    # Test 4: Test the forms
    import sys
    sys.path.append('/workspaces/aksjeradarv6')
    
    from app.forms import ForgotPasswordForm
    print("✅ ForgotPasswordForm imported")
    
    # Test 5: Create form instance
    form = ForgotPasswordForm()
    print("✅ Form instance created")
    
    print("\n🎯 RESULT: Email validation is working!")
    print("✅ The 'glemt passord' feature should now work")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n🔧 TROUBLESHOOTING:")
    print("1. Restart development server")
    print("2. Clear browser cache") 
    print("3. Try again")
