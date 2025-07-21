from password_reset_handler import PasswordResetHandler

def generate_reset_link():
    """Generate a reset link for development testing"""
    handler = PasswordResetHandler()
    
    # List available users
    users = handler.list_users()
    if not users:
        print("❌ No users found. Create a user first!")
        return
    
    print("📋 Available users:")
    for i, (user_id, email, username) in enumerate(users, 1):
        print(f"{i}. {email} ({username})")
    
    choice = input("\nSelect user number: ")
    try:
        user_index = int(choice) - 1
        selected_email = users[user_index][1]
        
        # Generate reset token
        result = handler.create_reset_request(selected_email)
        
        if result['success']:
            reset_url = f"http://localhost:5000/reset-password?token={result['token']}"
            print(f"\n🔗 Development reset URL:")
            print(f"   {reset_url}")
            print(f"\n📅 Expires: {result['expires']}")
            print(f"\n✅ Copy this URL and paste it in your browser to test reset")
        else:
            print(f"❌ Failed to create reset token: {result['message']}")
            
    except (ValueError, IndexError):
        print("❌ Invalid selection")

if __name__ == "__main__":
    print("🔧 Development Password Reset Link Generator")
    print("=" * 50)
    generate_reset_link()
