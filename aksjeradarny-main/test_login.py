from app import create_app
from app.models.user import User

def test_login():
    app = create_app()
    with app.app_context():
        # Test å finne brukeren
        user = User.query.filter(
            (User.username == 'helene721@gmail.com') | 
            (User.email == 'helene721@gmail.com')
        ).first()
        
        if user:
            print(f"Bruker funnet: {user.username}, {user.email}")
            print(f"Admin: {user.is_admin}, Subscription: {user.has_subscription}")
            
            # Test passord
            if user.check_password('admin123'):
                print("Passord er riktig!")
            else:
                print("Passord er feil!")
        else:
            print("Bruker ikke funnet!")

if __name__ == '__main__':
    test_login()

