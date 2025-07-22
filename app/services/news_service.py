"""
News Service for Aksjeradar
Handles fetching and processing of financial news
"""
import asyncio
import aiohttp
import feedparser
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import re
from urllib.parse import urljoin

# Try relative imports, fallback to absolute
try:
    from ..services.simple_cache import simple_cache
except ImportError:
    try:
        from app.services.simple_cache import simple_cache
    except ImportError:
        # Fallback for testing - create dummy cache
        class DummyCache:
            def get(self, key, namespace=None): return None
            def set(self, key, value, namespace=None, expire_minutes=5): pass
        simple_cache = DummyCache()

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    summary: str
    url: str
    source: str
    published_date: datetime
    image_url: Optional[str] = None
    relevance_score: float = 0.0
    categories: List[str] = None

class NewsService:
    """Service for fetching and processing financial news"""
    
    def __init__(self):
        self.news_sources = {
            # Working Norwegian financial sources
            'e24': {
                'name': 'E24',
                'rss': 'https://e24.no/rss',
                'base_url': 'https://e24.no',
                'priority': 10,
                'category': 'norwegian'
            },
            'kapital': {
                'name': 'Kapital',
                'rss': 'https://kapital.no/rss',
                'base_url': 'https://kapital.no',
                'priority': 9,
                'category': 'norwegian'
            }
        }

    async def get_latest_news(self, limit: int = 20, category: Optional[str] = None) -> List[NewsArticle]:
        """Get latest financial news from all sources"""
        try:
            # Return mock data for now to prevent crashes
            return [
                NewsArticle(
                    title="Mock News Article",
                    summary="This is a mock news article for testing",
                    url="https://example.com",
                    source="Test Source",
                    published_date=datetime.now()
                )
            ][:limit]
        except Exception as e:
            logger.error(f"Error in get_latest_news: {e}")
            return []

    async def search_news(self, query: str, limit: int = 20) -> List[NewsArticle]:
        """Search news articles by query"""
        try:
            if not query or len(query.strip()) < 2:
                return []
            
            # Return mock search results
            return [
                NewsArticle(
                    title=f"Search result for: {query}",
                    summary=f"Mock search result matching query: {query}",
                    url="https://example.com",
                    source="Search Source",
                    published_date=datetime.now(),
                    relevance_score=1.0
                )
            ][:limit]
            
        except Exception as e:
            logger.error(f"Error searching news for '{query}': {e}")
            return []

# Global instance
news_service = NewsService()

# Sync wrappers for compatibility
def get_latest_news_sync(limit: int = 20, category: Optional[str] = None) -> List[NewsArticle]:
    """Synchronous wrapper for getting latest news"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            asyncio.wait_for(news_service.get_latest_news(limit, category), timeout=10.0)
        )
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in sync news fetch: {e}")
        return []

def search_news_sync(query: str, limit: int = 20) -> List[NewsArticle]:
    """Synchronous wrapper for news search"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(news_service.search_news(query, limit))
        loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in sync news search: {e}")
        return []