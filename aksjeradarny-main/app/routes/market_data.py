from flask import Blueprint, jsonify, request, current_app
import time
from datetime import datetime
from ..utils.access_control import access_required

market_data = Blueprint('market_data', __name__)

@market_data.route('/api/markets/summary')
@access_required
def market_summary():
    """Market summary API endpoint"""
    try:
        # Mock data for market summary
        summary_data = {
            "indices": [
                {"name": "OSEBX", "value": 1287.45, "change": 0.78, "change_percent": 0.52},
                {"name": "S&P 500", "value": 4580.25, "change": 15.20, "change_percent": 0.33},
                {"name": "NASDAQ", "value": 14250.75, "change": 88.50, "change_percent": 0.63},
                {"name": "DAX", "value": 15890.50, "change": -12.30, "change_percent": -0.08}
            ],
            "sectors": [
                {"name": "Technology", "change_percent": 1.25},
                {"name": "Energy", "change_percent": 0.85},
                {"name": "Financials", "change_percent": -0.32},
                {"name": "Healthcare", "change_percent": 0.45}
            ],
            "timestamp": int(time.time())
        }
        return jsonify(summary_data)
    except Exception as e:
        current_app.logger.error(f"Error in market summary API: {str(e)}")
        return jsonify({"error": "Kunne ikke hente markedsoversikt"}), 200

@market_data.route('/api/stocks/popular')
@access_required
def popular_stocks():
    """Popular stocks API endpoint"""
    try:
        # Mock data for popular stocks
        stocks_data = [
            {"symbol": "EQNR.OL", "name": "Equinor", "price": 290.25, "change_percent": 1.2},
            {"symbol": "DNB.OL", "name": "DNB", "price": 205.80, "change_percent": 0.5},
            {"symbol": "AAPL", "name": "Apple", "price": 175.50, "change_percent": 0.8},
            {"symbol": "MSFT", "name": "Microsoft", "price": 310.75, "change_percent": 1.5},
            {"symbol": "GOOGL", "name": "Alphabet", "price": 138.90, "change_percent": -0.3}
        ]
        return jsonify(stocks_data)
    except Exception as e:
        current_app.logger.error(f"Error in popular stocks API: {str(e)}")
        return jsonify({"error": "Kunde ikke hente populære aksjer"}), 200

@market_data.route('/api/news/latest')
@access_required
def latest_news():
    """Latest news API endpoint"""
    try:
        # Mock data for latest news
        current_date = datetime.now().strftime("%Y-%m-%d")
        news_data = [
            {
                "title": "Equinor rapporterer sterke resultater for Q3",
                "source": "E24",
                "date": current_date,
                "url": "https://e24.no/equinor-q3",
                "ticker": "EQNR.OL"
            },
            {
                "title": "Norges Bank holder renten uendret",
                "source": "NRK",
                "date": current_date,
                "url": "https://nrk.no/norges-bank",
                "ticker": None
            },
            {
                "title": "Apple lanserer ny MacBook Pro",
                "source": "TechCrunch",
                "date": current_date,
                "url": "https://techcrunch.com/apple-macbook",
                "ticker": "AAPL"
            }
        ]
        return jsonify(news_data)
    except Exception as e:
        current_app.logger.error(f"Error in latest news API: {str(e)}")
        return jsonify({"error": "Kunne ikke hente nyeste nyheter"}), 200
