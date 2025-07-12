from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Aksjeradar kjører!"

@app.route("/login", methods=["POST"])
def login():
    return "", 200

# Stub endpoints for testing access
@app.route("/analysis")
def analysis():
    return "", 200

@app.route("/portfolio")
def portfolio():
    return "", 200

@app.route("/portfolio/advanced")
def portfolio_advanced():
    return "", 200

@app.route("/features/analyst-recommendations")
def analyst_recommendations():
    return "", 200

@app.route("/features/social-sentiment")
def social_sentiment():
    return "", 200

@app.route("/features/ai-predictions")
def ai_predictions():
    return "", 200

@app.route("/market-intel")
def market_intel():
    return "", 200

@app.route("/profile")
def profile():
    return "", 200

@app.route("/notifications")
def notifications():
    return "", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)