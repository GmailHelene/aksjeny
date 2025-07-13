from flask import Blueprint, render_template, redirect, url_for, request
from ..services.data_service import DataService
from ..utils.access_control import access_required
import re

search_results = Blueprint('search_results', __name__)

@search_results.route('/')
@access_required
def index():
    query = request.args.get('query', '').lower()
    if not query:
        return redirect(url_for('stocks.stocks_index'))
    
    results = []
    
    # Get all available stocks from DataService
    try:
        oslo_stocks = DataService.get_oslo_bors_overview()
        global_stocks = DataService.get_global_stocks_overview()
        
        # Search through Oslo Børs stocks
        for ticker, data in oslo_stocks.items():
            if query in ticker.lower() or \
               query in data.get('name', '').lower() or \
               query in data.get('sector', '').lower():
                results.append(ticker)
        
        # Search through global stocks
        for ticker, data in global_stocks.items():
            if query in ticker.lower() or \
               query in data.get('name', '').lower() or \
               query in data.get('sector', '').lower():
                results.append(ticker)
                
    except Exception as e:
        # Fallback to basic search if DataService fails
        print(f"DataService error in search: {str(e)}")
        fallback_stocks = {
            'EQNR.OL': ['equinor', 'eqnr'],
            'DNB.OL': ['dnb'],
            'TEL.OL': ['telenor', 'tel'],
            'MOWI.OL': ['mowi', 'marine harvest'],
            'YAR.OL': ['yara'],
            'NHY.OL': ['norsk', 'hydro'],
            'AAPL': ['apple'],
            'MSFT': ['microsoft'],
            'GOOGL': ['google', 'alphabet'],
            'AMZN': ['amazon'],
            'TSLA': ['tesla']
        }
        
        for ticker, keywords in fallback_stocks.items():
            if any(kw in query for kw in keywords):
                results.append(ticker)
    
    # Sort results by relevance (Oslo Børs first)
    results.sort(key=lambda x: (not x.endswith('.OL'), x))
    
    return render_template('stocks/search_results.html', 
                         results=results, 
                         query=query,
                         title=f"Søkeresultater for '{query}'")
