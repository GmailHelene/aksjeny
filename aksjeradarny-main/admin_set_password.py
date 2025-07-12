from main import db, User
from werkzeug.security import generate_password_hash

email = "helene721@gmail.com"
new_password = "Soda2001??"

user = User.query.filter_by(email=email).first()
if user:
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    print(f"Passordet for {email} er nå satt til {new_password}")
else:
    print(f"Fant ikke bruker med e-post: {email}")
