# gdpr_cleanup.py
"""
Script for å anonymisere/slette brukerdata etter 30 dager uten aktivt abonnement (GDPR).
Kjør denne daglig via cron eller annen scheduler.
"""
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.watchlist import Watchlist
from app.models.tip import StockTip

app = create_app()

with app.app_context():
    cutoff = datetime.utcnow() - timedelta(days=30)
    users = User.query.filter(
        User.has_subscription == False,
        User.subscription_end != None,
        User.subscription_end < cutoff
    ).all()
    for user in users:
        # Slett porteføljer
        Portfolio.query.filter_by(user_id=user.id).delete()
        # Slett watchlists
        Watchlist.query.filter_by(user_id=user.id).delete()
        # Slett tips
        StockTip.query.filter_by(user_id=user.id).delete()
        # Anonymiser brukeren (behold for statistikk, men fjern persondata)
        user.email = f'anonym_{user.id}@deleted.local'
        user.username = f'anonym_{user.id}'
        user.password_hash = ''
        user.stripe_customer_id = None
        user.subscription_type = None
        user.subscription_start = None
        user.subscription_end = None
        user.trial_used = True
        # Du kan også velge å slette brukeren helt:
        # db.session.delete(user)
    db.session.commit()
    print(f"GDPR cleanup kjørt. {len(users)} brukere behandlet.")
