from app import create_app
from app.models.user import User

def check_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
            print(f"Has subscription: {user.has_subscription}, Is admin: {user.is_admin}")
            print("---")

if __name__ == '__main__':
    check_users()

