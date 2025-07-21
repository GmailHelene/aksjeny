import os

# Sett Railway environment variables lokalt for testing
os.environ['EMAIL_USERNAME'] = 'support@luxushair.com'
os.environ['EMAIL_PASSWORD'] = 'suetozoydejwntii'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_SERVER'] = 'imap.gmail.com'  # Will be converted to smtp.gmail.com

def test_email_config():
    """Test email configuration with Railway values"""
    print("📧 Testing Railway email configuration...")
    print("=" * 50)
    
    from email_service import EmailService
    
    try:
        email_service = EmailService()
        
        # Test med din egen e-post først
        test_email = input("Enter your email to receive test: ")
        test_url = "http://localhost:5000/reset-password?token=TEST_TOKEN_123"
        
        print("\n📤 Sending test email...")
        success = email_service.send_reset_email(test_email, test_url)
        
        if success:
            print("✅ Test email sent successfully!")
            print("✅ Railway email configuration is working!")
            print("Check your inbox for the password reset test email.")
        else:
            print("❌ Failed to send test email")
            print("Check your Gmail app password and settings")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure 2-factor authentication is enabled on Gmail")
        print("2. Use an App Password, not your regular Gmail password")
        print("3. Check that support@luxushair.com has SMTP access enabled")

if __name__ == "__main__":
    test_email_config()
