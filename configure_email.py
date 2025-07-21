import os

def setup_gmail():
    """Setup Gmail SMTP (requires app password)"""
    print("📧 Setting up Gmail SMTP...")
    print("\n🔧 Steps to configure Gmail:")
    print("1. Go to your Google Account settings")
    print("2. Enable 2-factor authentication")
    print("3. Generate an 'App Password' for this application")
    print("4. Use your Gmail address and the app password below")
    
    email = input("\nEnter your Gmail address: ")
    password = input("Enter your Gmail app password: ")
    
    # Set environment variables
    os.environ['EMAIL_USER'] = email
    os.environ['EMAIL_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['FROM_EMAIL'] = email
    
    print(f"✅ Email configured for {email}")
    return True

def setup_other_smtp():
    """Setup other SMTP providers"""
    print("📧 Setting up custom SMTP...")
    
    smtp_server = input("SMTP Server (e.g., smtp.gmail.com): ")
    smtp_port = input("SMTP Port (usually 587): ")
    email = input("Email address: ")
    password = input("Email password: ")
    
    # Set environment variables
    os.environ['EMAIL_USER'] = email
    os.environ['EMAIL_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = smtp_server
    os.environ['SMTP_PORT'] = smtp_port
    os.environ['FROM_EMAIL'] = email
    
    print(f"✅ Email configured for {email}")
    return True

def test_email_service():
    """Test the email configuration"""
    from email_service import EmailService
    
    email_service = EmailService()
    test_email = input("Enter test email address: ")
    test_url = "http://localhost:5000/reset-password?token=TEST_TOKEN"
    
    print("📤 Sending test email...")
    success = email_service.send_reset_email(test_email, test_url)
    
    if success:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email")
    
    return success

def main():
    print("📧 Email Configuration Setup")
    print("=" * 40)
    
    choice = input("""
Choose email provider:
1. Gmail
2. Other SMTP provider
3. Test current configuration
4. Skip email setup (use development mode)

Enter choice (1-4): """)
    
    if choice == '1':
        setup_gmail()
        test_email_service()
    elif choice == '2':
        setup_other_smtp()
        test_email_service()
    elif choice == '3':
        test_email_service()
    elif choice == '4':
        print("⚠️ Skipping email setup - reset links will be shown in browser")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
