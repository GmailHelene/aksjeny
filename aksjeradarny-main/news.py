News Blueprint for Aksjeradar
Handles news-related routes and functionality
"""

from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from app.services.news_service import news_service, get_latest_news_sync, get_company_news_sync
from app.utils.access_control import access_required
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

news_bp = Blueprint('news', __name__, url_prefix='/news')

@news_bp.route('/')
@access_required
def news_index():
    """Main news page"""
    try:
        category = request.args.get('category', 'all')
        limit = int(request.args.get('limit', 20))
        
        # Get latest news
        news_articles = get_latest_news_sync(limit=limit, category=category)
        
        return render_template('news/index.html', 
                             news_articles=news_articles,