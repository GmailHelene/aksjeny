import os

def setup_railway_env():
    """Setup Railway environment variables locally"""
    print("🚀 Railway Environment Setup")
    print("=" * 40)
    
    print("Please enter your Railway email configuration:")
    
    # Get email configuration
    email_user = input("EMAIL_USER (your email): ")
    email_password = input("EMAIL_PASSWORD (app password): ")
    smtp_server = input("SMTP_SERVER (default: smtp.gmail.com): ") or "smtp.gmail.com"
    smtp_port = input("SMTP_PORT (default: 587): ") or "587"
    
    # Set environment variables
    os.environ['EMAIL_USER'] = email_user
    os.environ['EMAIL_PASSWORD'] = email_password
    os.environ['SMTP_SERVER'] = smtp_server
    os.environ['SMTP_PORT'] = smtp_port
    os.environ['FROM_EMAIL'] = email_user
    
    print("\n✅ Environment variables set!")
    
    # Test the configuration
    from email_service import EmailService
    email_service = EmailService()
    
    test_choice = input("\nTest email configuration? (y/n): ")
    if test_choice.lower() == 'y':
        test_email = input("Enter test email: ")
        test_url = "http://localhost:5000/reset-password?token=TEST_TOKEN"
        
        print("📤 Sending test email...")
        success = email_service.send_reset_email(test_email, test_url)
        
        if success:
            print("✅ Email configuration working!")
        else:
            print("❌ Email configuration needs adjustment")

if __name__ == "__main__":
    setup_railway_env()
