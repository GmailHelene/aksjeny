from app import create_app
from app.extensions import db
from app.models.user import User

def reset_users():
    app = create_app()
    with app.app_context():
        # Slett brukere med e-postene dine
        emails = ['helene@luxushair.com', 'helene721@gmail.com', 'helene@luxushair.com']
        for email in emails:
            user = User.query.filter_by(email=email).first()
            if user:
                db.session.delete(user)
        db.session.commit()
        # Opprett brukerne på nytt
        for email in emails:
            user = User(username=email.split('@')[0], email=email)
            user.set_password('dittnyevalgtepw')  # Sett ønsket passord
            user.has_subscription = True
            user.subscription_type = 'lifetime'
            user.is_admin = True
            db.session.add(user)
        db.session.commit()
        print("Brukere tilbakestilt og opprettet på nytt.")

if __name__ == '__main__':
    reset_users()
