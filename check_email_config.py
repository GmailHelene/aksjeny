import os

def check_email_environment():
    """Check email configuration from environment variables"""
    print("📧 Checking email configuration...")
    print("=" * 40)
    
    # Sjekk alle mulige e-post environment variables
    email_vars = {
        'EMAIL_USER': os.getenv('EMAIL_USER'),
        'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD'),
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'),
        'FROM_EMAIL': os.getenv('FROM_EMAIL'),
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
    }
    
    print("Environment variables:")
    for var_name, var_value in email_vars.items():
        if var_value:
            # Mask password values for security
            if 'PASSWORD' in var_name:
                display_value = '*' * len(var_value) if var_value else 'Not set'
            else:
                display_value = var_value
            print(f"✅ {var_name}: {display_value}")
        else:
            print(f"❌ {var_name}: Not set")
    
    # Check if minimum configuration is available
    has_email = email_vars['EMAIL_USER'] or email_vars['MAIL_USERNAME']
    has_password = email_vars['EMAIL_PASSWORD'] or email_vars['MAIL_PASSWORD']
    
    if has_email and has_password:
        print("\n✅ Email configuration looks complete!")
        return True
    else:
        print("\n❌ Email configuration incomplete!")
        print("\nTo configure email in Railway:")
        print("1. Go to your Railway project dashboard")
        print("2. Click on your service")
        print("3. Go to 'Variables' tab")
        print("4. Add these variables:")
        print("   - EMAIL_USER: your-email@gmail.com")
        print("   - EMAIL_PASSWORD: your-app-password")
        print("   - SMTP_SERVER: smtp.gmail.com")
        print("   - SMTP_PORT: 587")
        return False

def test_email_with_current_config():
    """Test email sending with current configuration"""
    from email_service import EmailService
    
    try:
        email_service = EmailService()
        test_email = input("\nEnter your email to test: ")
        
        if test_email:
            test_url = "http://localhost:5000/reset-password?token=TEST_TOKEN"
            print("📤 Sending test email...")
            
            success = email_service.send_reset_email(test_email, test_url)
            
            if success:
                print("✅ Test email sent successfully!")
                print("Check your inbox for the test email.")
            else:
                print("❌ Failed to send test email")
        
    except Exception as e:
        print(f"❌ Error testing email: {e}")

if __name__ == "__main__":
    if check_email_environment():
        test_email_with_current_config()
