# Denne filen er tom. Det er ikke en feil hvis du bevisst har flyttet alle modellklasser (f.eks. StockTip, Watchlist, WatchlistStock) til andre filer.
# Men hvis du forventer at denne filen skal inneholde modellklasser, må du legge dem inn her.
#
# Hvis du ikke bruker denne filen, kan du la den være tom eller slette den.
# Hvis du trenger StockTip-modellen, legg inn for eksempel:
#
# from datetime import datetime
# from app.extensions import db
#
# class StockTip(db.Model):
#     __tablename__ = 'stock_tips'
#     id = db.Column(db.Integer, primary_key=True)
#     ticker = db.Column(db.String(20))
#     tip_type = db.Column(db.String(20))  # BUY, SELL, HOLD
#     confidence = db.Column(db.String(20))  # HIGH, MEDIUM, LOW
#     analysis = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
#
#     def __repr__(self):
#         return f'<StockTip {self.ticker} - {self.tip_type}>'