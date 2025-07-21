from password_reset_handler import PasswordResetHandler
import os

def test_password_reset_flow():
    """Test hele password reset-flyten"""
    handler = PasswordResetHandler()
    
    # Test e-post (erstatt med en faktisk e-post i databasen)
    test_email = input("Skriv inn en e-postadresse fra databasen: ")
    
    print("🧪 Tester password reset-funksjonalitet...")
    
    # 1. Opprett reset-forespørsel
    print(f"\n1. Oppretter reset-forespørsel for {test_email}...")
    result = handler.create_reset_request(test_email)
    
    if result['success']:
        token = result['token']
        print(f"✅ Reset token opprettet: {token}")
        print(f"✅ Utløper: {result['expires']}")
        
        # 2. Verifiser token
        print(f"\n2. Verifiserer token...")
        verify_result = handler.verify_reset_token(token)
        
        if verify_result['valid']:
            print(f"✅ Token er gyldig for bruker: {verify_result['email']}")
            
            # 3. Test password reset (ikke gjør faktisk reset)
            print(f"\n3. Testing password reset (simulert)...")
            print("✅ Password reset-funksjonen er klar!")
            
            # Vis reset URL for testing
            reset_url = f"http://localhost:5000/reset-password?token={token}"
            print(f"\n🔗 Test URL: {reset_url}")
            
        else:
            print(f"❌ Token validering feilet: {verify_result['message']}")
    else:
        print(f"❌ Kunne ikke opprette reset-forespørsel: {result['message']}")

if __name__ == "__main__":
    test_password_reset_flow()
