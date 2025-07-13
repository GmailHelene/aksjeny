import math
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user
from datetime import datetime, timedelta
from ..services.data_service import DataService
from ..services.analysis_service import AnalysisService
from ..services.usage_tracker import usage_tracker
from ..utils.access_control import access_required

stocks = Blueprint("stocks", __name__, url_prefix="/stocks")

@stocks.route("/")
@access_required
def index():
    """Show stocks landing page with links to all markets"""
    return render_template("stocks/index.html")

@stocks.route("/list")
@access_required
def list_stocks():
    """List stocks with real-time data"""
    try:
        category = request.args.get("category", "all")
        
        # Get real data from DataService
        if category == "oslo":
            stocks_data = DataService.get_oslo_bors_overview()
        elif category == "global":
            stocks_data = DataService.get_global_stocks_overview()
        elif category == "crypto":
            stocks_data = DataService.get_crypto_overview()
        else:
            # Get all categories
            oslo_stocks = DataService.get_oslo_bors_overview()
            global_stocks = DataService.get_global_stocks_overview()
            crypto = DataService.get_crypto_overview()
            
            stocks_data = {
                "oslo": oslo_stocks,
                "global": global_stocks,
                "crypto": crypto
            }
        
        return render_template("stocks/list.html", 
                             stocks=stocks_data,
                             category=category)
                             
    except Exception as e:
        current_app.logger.error(f"Error in list_stocks: {str(e)}")
        return render_template("error.html", 
                             error="Kunne ikke hente aksjedata. Prøv igjen senere.")

@stocks.route("/list/<category>")
@access_required
def list_stocks_by_category(category):
    """List stocks by category"""
    try:
        if category == "oslo":
            stocks = DataService.get_oslo_bors_overview()
            title = "Oslo Børs"
            # Get "mest omsatte" data for Oslo Børs - sorted by volume
            all_oslo_stocks = DataService.get_oslo_bors_overview()
            most_traded_list = sorted(all_oslo_stocks.items(), 
                                    key=lambda x: float(x[1].get("volume", 0)), 
                                    reverse=True)[:10]  # Top 10 most traded
            mest_omsatte = dict(most_traded_list)
        elif category == "global":
            stocks = DataService.get_global_stocks_overview()
            title = "Globale Aksjer"
            mest_omsatte = None
        else:
            stocks = {}
            title = "Ukjent kategori"
            mest_omsatte = None
            
        return render_template("stocks/list.html",
                             stocks=stocks,
                             category=category,
                             title=title,
                             mest_omsatte=mest_omsatte)
    except Exception as e:
        current_app.logger.error(f"Error listing stocks: {str(e)}")
        return render_template("error.html", error=str(e))

@stocks.route("/details/<ticker>")
@access_required
def details(ticker):
    """Stock details page"""
    try:
        from app.services.data_service import DataService
        
        stock_data = DataService.get_stock_info(ticker)
        if not stock_data:
            flash(f"Kunne ikke finne informasjon om {ticker}", "warning")
            return redirect(url_for("stocks.index"))
        
        # Get additional data
        technical_data = DataService.get_technical_indicators(ticker)
        news = DataService.get_stock_news(ticker, limit=5)
        
        return render_template("stocks/details.html",
                             ticker=ticker,
                             stock=stock_data,
                             technical=technical_data,
                             news=news,
                             last_updated=datetime.utcnow())
    except Exception as e:
        current_app.logger.error(f"Error loading stock details for {ticker}: {e}")
        flash("Kunne ikke laste aksjedetaljer. Prøv igjen senere.", "error")
        return redirect(url_for("stocks.index"))

@stocks.route("/search")
@access_required
def search():
    """Search for stocks"""
    query = request.args.get("q", "")
    if not query:
        return render_template("stocks/search.html")
    
    results = DataService.search_stocks(query)
    return render_template("stocks/search.html", 
                         results=results,
                         query=query)

@stocks.route("/api/search")
@access_required
def api_search():
    """API endpoint for stock search"""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    
    try:
        results = DataService.search_stocks(query)
        return jsonify(results)
    except Exception as e:
        current_app.logger.error(f"Error in stock search: {str(e)}")
        return jsonify({"error": "Søket feilet. Vennligst prøv igjen."})

