from app import create_app
from app.extensions import db
from app.models.user import User
from datetime import datetime, timedelta

def create_test_users():
    app = create_app()
    with app.app_context():
        # Slett eksisterende testbrukere først
        User.query.filter(User.email.in_(['trial@example.com', 'expired@example.com'])).delete()
        
        # Opprett eller oppdater admin bruker
        admin = User.query.filter_by(email='helene721@gmail.com').first()
        if not admin:
            admin = User(
                username='helene721@gmail.com',
                email='helene721@gmail.com',
                has_subscription=True,
                subscription_type='lifetime',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        else:
            # Oppdater eksisterende admin bruker
            admin.has_subscription = True
            admin.subscription_type = 'lifetime'
            admin.is_admin = True
            admin.set_password('admin123')
        
        # Opprett trial bruker
        trial_user = User(
            username='trial_user',
            email='trial@example.com',
            trial_used=True,
            trial_start=datetime.utcnow()
        )
        trial_user.set_password('trial123')
        db.session.add(trial_user)
        
        # Opprett expired bruker
        expired_user = User(
            username='expired_user',
            email='expired@example.com',
            trial_used=True,
            trial_start=datetime.utcnow() - timedelta(days=11)
        )
        expired_user.set_password('expired123')
        db.session.add(expired_user)
        
        db.session.commit()
        print("Test users created successfully!")

if __name__ == '__main__':
    create_test_users()
