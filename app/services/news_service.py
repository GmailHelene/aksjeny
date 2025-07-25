"""
Advanced News Service for Aksjeradar
Fetches relevant financial news from major Norwegian and international sources
"""

import requests
import feedparser
import asyncio
import aiohttp
import concurrent.futures
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from ..services.simple_cache import simple_cache
from ..services.cache_service import cached

logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    summary: str
    link: str
    source: str
    published: datetime
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
            },
            'hegnar': {
                'name': 'Hegnar Online',
                'rss': 'https://www.hegnar.no/rss.aspx',
                'base_url': 'https://www.hegnar.no',
                'priority': 8,
                'category': 'norwegian'
            },
            
            # Updated DN URL
            'dn': {
                'name': 'Dagens Næringsliv',
                'rss': 'https://services.dn.no/tools/rss',
                'base_url': 'https://www.dn.no',
                'priority': 9,
                'category': 'norwegian'
            },
            
            # International financial sources that should work
            'reuters_business': {
                'name': 'Reuters Business',
                'rss': 'https://feeds.reuters.com/reuters/businessNews',
                'base_url': 'https://www.reuters.com',
                'priority': 10,
                'category': 'international'
            },
            'ft': {
                'name': 'Financial Times',
                'rss': 'https://www.ft.com/news-feed',
                'base_url': 'https://www.ft.com',
                'priority': 9,
                'category': 'international'
            },
            'marketwatch': {
                'name': 'MarketWatch',
                'rss': 'https://feeds.marketwatch.com/marketwatch/topstories/',
                'base_url': 'https://www.marketwatch.com',
                'priority': 8,
                'category': 'international'
            }
        }
        
        # Enhanced keywords for better relevance scoring
        self.relevance_keywords = {
            'oslo_bors': ['oslo børs', 'osebx', 'oslo stock exchange', 'euronext oslo', 'obx', 'ose'],
            'norwegian_companies': [
                'equinor', 'dnb', 'telenor', 'aker', 'yara', 'norsk hydro', 'mowi', 
                'schibsted', 'kahoot', 'autostore', 'komplett', 'xxl', 'orkla',
                'salmon evolution', 'aker bp', 'elkem', 'rec silicon', 'storebrand',
                'norges bank', 'dnb bank', 'marine harvest', 'statoil', 'hydro',
                'subsea 7', 'kongsberg', 'tomra', 'nel', 'aker solutions'
            ],
            'finance_general': [
                'aksje', 'aksjer', 'stock', 'stocks', 'investering', 'investment',
                'børs', 'market', 'markets', 'finans', 'finance', 'økonomi', 'economy',
                'rente', 'interest rate', 'valuta', 'currency', 'krone', 'nok',
                'dividend', 'utbytte', 'earnings', 'resultat', 'quarterly', 'kvartal'
            ],
            'crypto': ['bitcoin', 'cryptocurrency', 'crypto', 'blockchain', 'ethereum', 'btc', 'eth', 'defi'],
            'energy': [
                'olje', 'oil', 'renewable energy', 'fornybar energi', 'petroleum',
                'offshore', 'subsea', 'hydrogen', 'wind power', 'vindkraft',
                'solar', 'solenergi', 'brent', 'wti', 'natural gas', 'lng'
            ],
            'tech': [
                'teknologi', 'technology', 'tech', 'ai', 'artificial intelligence',
                'digitalisering', 'digitalization', 'software', 'cloud', 'saas',
                'fintech', 'innovation', 'startup', 'venture capital'
            ],
            'shipping': ['shipping', 'skipsfart', 'tanker', 'bulk', 'container', 'offshore', 'maritime'],
            'salmon': ['laks', 'salmon', 'aquaculture', 'oppdrett', 'seafood', 'sjømat', 'fish farming'],
            'banking': ['bank', 'banking', 'fintech', 'lending', 'mortgage', 'boliglån', 'kreditt'],
            'mining': ['mining', 'gruvedrift', 'metals', 'metaller', 'copper', 'kobber', 'aluminum'],
            'real_estate': ['eiendom', 'real estate', 'property', 'bolig', 'housing', 'commercial property']
        }

    async def get_latest_news(self, limit: int = 20, category: Optional[str] = None) -> List[NewsArticle]:
        """Get latest financial news from all sources"""
        try:
            # Check cache first
            cache_key = f"news_latest_{category}_{limit}"
            cached_result = simple_cache.get(cache_key, 'news')
            if cached_result:
                return cached_result
            
            all_articles = []
            
            # Enhanced timeout settings - shorter per-request timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=8, connect=3, sock_read=3)
            connector = aiohttp.TCPConnector(limit=30, limit_per_host=10)
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                tasks = []
                for source_id, source_config in self.news_sources.items():
                    if category and not self._source_matches_category(source_id, category):
                        continue
                    task = self._fetch_source_news(session, source_id, source_config)
                    tasks.append(task)
                
                # Execute all requests concurrently with faster timeout
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True), 
                        timeout=7.0  # Overall timeout slightly less than session timeout
                    )
                    
                    # Process results
                    for result in results:
                        if isinstance(result, list):
                            all_articles.extend(result)
                        elif isinstance(result, Exception):
                            logger.warning(f"Error fetching news: {result}")
                            
                except asyncio.TimeoutError:
                    logger.warning("News fetching timed out, returning partial results")
                    # Continue with whatever articles we have
            
            # Sort by relevance and date
            all_articles.sort(key=lambda x: (x.relevance_score, x.published), reverse=True)
            
            final_articles = all_articles[:limit]
            
            # Cache even partial results to prevent repeated hanging
            simple_cache.set(cache_key, final_articles, 'news')  # Ensure only 3 arguments are used
            
            return final_articles
            
        except Exception as e:
            logger.error(f"Error in get_latest_news: {e}")
            # Return cached fallback if available
            fallback_key = f"news_fallback_{category}_{limit}"
            fallback = simple_cache.get(fallback_key, 'news')
            return fallback if fallback else []

    async def _fetch_source_news(self, session: aiohttp.ClientSession, source_id: str, source_config: Dict) -> List[NewsArticle]:
        """Fetch news from a single source with enhanced error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(source_config['rss'], headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {source_id}: HTTP {response.status}")
                    return []
                
                content = await response.text()
                
                # Parse feed with error handling
                try:
                    feed = feedparser.parse(content)
                    if not hasattr(feed, 'entries') or not feed.entries:
                        logger.warning(f"No entries found in feed for {source_id}")
                        return []
                except Exception as parse_error:
                    logger.error(f"Failed to parse feed for {source_id}: {parse_error}")
                    return []
                
                articles = []
                for entry in feed.entries[:10]:  # Limit per source
                    try:
                        article = self._parse_feed_entry(entry, source_config)
                        if article:
                            articles.append(article)
                    except Exception as entry_error:
                        logger.warning(f"Failed to parse entry from {source_id}: {entry_error}")
                        continue
                
                logger.info(f"Successfully fetched {len(articles)} articles from {source_id}")
                return articles
                
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching from {source_id}")
            return []
        except aiohttp.ClientError as client_error:
            logger.warning(f"Client error fetching from {source_id}: {client_error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching from {source_id}: {e}")
            return []

    def _parse_feed_entry(self, entry, source_config: Dict) -> Optional[NewsArticle]:
        """Parse a single RSS feed entry into a NewsArticle"""
        try:
            # Extract basic info
            title = entry.get('title', '').strip()
            link = entry.get('link', '')
            
            # Extract summary
            summary = ''
            if hasattr(entry, 'summary'):
                summary = BeautifulSoup(entry.summary, 'html.parser').get_text().strip()
            elif hasattr(entry, 'description'):
                summary = BeautifulSoup(entry.description, 'html.parser').get_text().strip()
            
            # Extract publish date
            published = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except:
                    pass
            
            # Extract image URL if available
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.type.startswith('image/'):
                        image_url = enclosure.href
                        break
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance(title, summary)
            relevance_score += source_config.get('priority', 5)  # Add source priority
            
            # Determine categories
            categories = self._categorize_article(title, summary)
            
            return NewsArticle(
                title=title,
                summary=summary[:300] + '...' if len(summary) > 300 else summary,
                link=link,
                source=source_config['name'],
                published=published,
                image_url=image_url,
                relevance_score=relevance_score,
                categories=categories
            )
            
        except Exception as e:
            logger.error(f"Error parsing feed entry: {e}")
            return None

    def _calculate_relevance(self, title: str, summary: str) -> float:
        """Calculate relevance score based on keywords"""
        text = (title + ' ' + summary).lower()
        score = 0.0
        
        for category, keywords in self.relevance_keywords.items():
            category_score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    category_score += 1
            
            # Weight different categories
            weights = {
                'oslo_bors': 3.0,
                'norwegian_companies': 2.5,
                'finance_general': 2.0,
                'energy': 1.5,
                'tech': 1.0,
                'crypto': 1.0,
                'banking': 1.8,
                'shipping': 1.5,
                'salmon': 1.2,
                'mining': 1.0,
                'real_estate': 1.0
            }
            
            score += category_score * weights.get(category, 1.0)
        
        return score

    def _categorize_article(self, title: str, summary: str) -> List[str]:
        """Categorize article based on content"""
        text = (title + ' ' + summary).lower()
        categories = []
        
        for category, keywords in self.relevance_keywords.items():
            if any(keyword.lower() in text for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ['general']

    def _source_matches_category(self, source_id: str, category: str) -> bool:
        """Check if source matches requested category"""
        norwegian_sources = ['dn', 'finansavisen', 'e24', 'kapital', 'hegnar', 'shifter', 'newsinenglish']
        international_sources = ['reuters_business', 'ft', 'bloomberg', 'cnbc', 'wsj', 'marketwatch', 'seeking_alpha', 'yahoo_finance', 'investing_com', 'economics_times', 'the_economist']
        
        if category == 'norwegian' and source_id in norwegian_sources:
            return True
        elif category == 'international' and source_id in international_sources:
            return True
        elif category == 'all':
            return True
        
        return True  # Default to include all sources

    def get_news_by_category(self, category: str, limit: int = 20) -> List[NewsArticle]:
        """Get news articles filtered by category (synchronous wrapper)"""
        try:
            # Use the async method with proper event loop handling
            return get_latest_news_sync(limit=limit, category=category)
        except Exception as e:
            logger.error(f"Error getting news by category {category}: {e}")
            return []

    async def get_company_news(self, company_symbol: str, limit: int = 10) -> List[NewsArticle]:
        """Get news specifically related to a company"""
        try:
            # Check cache first
            cache_key = f"company_news_{company_symbol}_{limit}"
            cached_result = simple_cache.get(cache_key, 'news')
            if cached_result:
                return cached_result
            
            # Enhanced company symbol mapping for better search
            company_mapping = {
                'EQNR.OL': ['equinor', 'statoil'],
                'DNB.OL': ['dnb', 'dnb bank', 'dnb markets'],
                'TEL.OL': ['telenor'],
                'AKER.OL': ['aker', 'aker bp', 'aker solutions'],
                'YAR.OL': ['yara', 'yara international'],
                'NHY.OL': ['norsk hydro', 'hydro'],
                'MOWI.OL': ['mowi', 'marine harvest'],
                'SCHIBSTED.OL': ['schibsted'],
                'KAH.OL': ['kahoot'],
                'AUTO.OL': ['autostore'],
                'KOMP.OL': ['komplett'],
                'XXL.OL': ['xxl'],
                'ORK.OL': ['orkla'],
                'SALME.OL': ['salmon evolution'],
                'NEL.OL': ['nel', 'nel hydrogen'],
                'TOM.OL': ['tomra'],
                'KOG.OL': ['kongsberg'],
                'SUB.OL': ['subsea 7'],
                'REC.OL': ['rec silicon'],
                'ELKEM.OL': ['elkem'],
                'STB.OL': ['storebrand']
            }
            
            search_terms = company_mapping.get(company_symbol, [company_symbol.replace('.OL', '')])
            
            all_articles = await self.get_latest_news(limit=50)
            
            # Filter articles relevant to the company
            relevant_articles = []
            for article in all_articles:
                text = (article.title + ' ' + article.summary).lower()
                if any(term.lower() in text for term in search_terms):
                    article.relevance_score += 5.0  # Boost company-specific articles
                    relevant_articles.append(article)
            
            # Sort by relevance and return top results
            relevant_articles.sort(key=lambda x: x.relevance_score, reverse=True)
            final_articles = relevant_articles[:limit]
            
            # Cache the result
            simple_cache.set(cache_key, final_articles, 'news')  # Ensure only 3 arguments are used
            
            return final_articles
            
        except Exception as e:
            logger.error(f"Error getting company news for {company_symbol}: {e}")
            return []

    async def get_market_summary_news(self) -> Dict[str, List[NewsArticle]]:
        """Get categorized market news for dashboard"""
        try:
            # Check cache first
            cache_key = "market_summary_news"
            cached_result = simple_cache.get(cache_key, 'news')
            if cached_result:
                return cached_result
            
            all_news = await self.get_latest_news(limit=40)
            
            categorized = {
                'oslo_bors': [],
                'international': [],
                'energy': [],
                'tech': [],
                'crypto': [],
                'banking': [],
                'shipping': []
            }
            
            for article in all_news:
                # Categorize based on content and source
                if any(cat in article.categories for cat in ['oslo_bors', 'norwegian_companies']):
                    categorized['oslo_bors'].append(article)
                elif 'energy' in article.categories:
                    categorized['energy'].append(article)
                elif 'tech' in article.categories:
                    categorized['tech'].append(article)
                elif 'crypto' in article.categories:
                    categorized['crypto'].append(article)
                elif 'banking' in article.categories:
                    categorized['banking'].append(article)
                elif 'shipping' in article.categories:
                    categorized['shipping'].append(article)
                else:
                    categorized['international'].append(article)
            
            # Limit each category
            for category in categorized:
                categorized[category] = categorized[category][:5]
            
            # Cache the result
            simple_cache.set(cache_key, categorized, 'news')  # Ensure only 3 arguments are used
            
            return categorized
            
        except Exception as e:
            logger.error(f"Error getting market summary news: {e}")
            return {key: [] for key in ['oslo_bors', 'international', 'energy', 'tech', 'crypto', 'banking', 'shipping']}

    async def get_stock_related_news(self, stock_symbol: str, limit: int = 10) -> List[NewsArticle]:
        """Get news specifically related to a stock symbol"""
        try:
            # Get all recent news
            all_news = await self.get_latest_news(limit=50)
            
            # Extract company name and variations
            company_variations = self._get_company_variations(stock_symbol)
            
            # Filter for relevant articles
            relevant_articles = []
            for article in all_news:
                if self._is_stock_relevant(article, stock_symbol, company_variations):
                    relevant_articles.append(article)
                    if len(relevant_articles) >= limit:
                        break
            
            return relevant_articles
            
        except Exception as e:
            logger.error(f"Error getting stock-related news for {stock_symbol}: {e}")
            return []
    
    def _get_company_variations(self, stock_symbol: str) -> List[str]:
        """Get various name variations for a company"""
        # Remove .OL suffix if present
        clean_symbol = stock_symbol.replace('.OL', '').upper()
        
        # Company name mappings
        company_names = {
            'EQNR': ['equinor', 'statoil'],
            'DNB': ['dnb', 'dnb bank'],
            'TEL': ['telenor'],
            'MOWI': ['mowi', 'marine harvest'],
            'AKER': ['aker', 'aker solutions', 'aker bp'],
            'NHY': ['norsk hydro', 'hydro'],
            'YAR': ['yara', 'yara international'],
            'SALME': ['salmon evolution'],
            'KAH': ['kahoot'],
            'AUTO': ['autostore'],
            'SCHIBSTED': ['schibsted'],
            'KOMP': ['komplett'],
            'XXL': ['xxl'],
            'ORK': ['orkla']
        }
        
        variations = [clean_symbol.lower()]
        if clean_symbol in company_names:
            variations.extend(company_names[clean_symbol])
        
        return variations
    
    def _is_stock_relevant(self, article: NewsArticle, stock_symbol: str, company_variations: List[str]) -> bool:
        """Check if article is relevant to a specific stock"""
        text_content = f"{article.title} {article.summary}".lower()
        
        # Check for direct symbol match
        if stock_symbol.replace('.OL', '').lower() in text_content:
            return True
        
        # Check for company name variations
        for variation in company_variations:
            if variation.lower() in text_content:
                return True
        
        return False
    
    async def get_market_overview_news(self) -> Dict:
        """Get structured market overview with categorized news"""
        try:
            norwegian_news = await self.get_latest_news(limit=15, category='norwegian')
            international_news = await self.get_latest_news(limit=15, category='international')
            
            return {
                'norwegian': [self._article_to_dict(article) for article in norwegian_news],
                'international': [self._article_to_dict(article) for article in international_news],
                'last_updated': datetime.now().isoformat(),
                'total_articles': len(norwegian_news) + len(international_news)
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {
                'norwegian': [],
                'international': [],
                'last_updated': datetime.now().isoformat(),
                'total_articles': 0
            }
    
    def _article_to_dict(self, article: NewsArticle) -> Dict:
        """Convert NewsArticle to dictionary"""
        return {
            'title': article.title,
            'summary': article.summary,
            'link': article.link,
            'source': article.source,
            'published': article.published.isoformat() if article.published else None,
            'image_url': article.image_url,
            'relevance_score': article.relevance_score,
            'categories': article.categories or []
        }
    
    def _source_matches_category(self, source_id: str, category: str) -> bool:
        """Check if source matches requested category"""
        source_config = self.news_sources.get(source_id, {})
        source_category = source_config.get('category', 'unknown')
        
        if category == 'norwegian':
            return source_category == 'norwegian'
        elif category == 'international':
            return source_category == 'international'
        
        return True

# Global instance
news_service = NewsService()

# Synchronous wrapper functions for template use
def get_latest_news_sync(limit: int = 10, category: Optional[str] = None) -> List[NewsArticle]:
    """Synchronous wrapper for template use with timeout protection"""
    try:
        # Check simple cache first with arguments in key
        cache_key = f"latest_news_{limit}_{category or 'all'}"
        cached_result = simple_cache.get(cache_key, 'news')
        if cached_result:
            return cached_result
        
        # Try to get the existing event loop first
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create task in thread
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(_run_async_news_fetch, limit, category)
                    result = future.result(timeout=12.0)
            else:
                # Loop exists but not running, can use it
                result = loop.run_until_complete(
                    asyncio.wait_for(news_service.get_latest_news(limit, category), timeout=10.0)
                )
        except RuntimeError:
            # No event loop, create new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    asyncio.wait_for(news_service.get_latest_news(limit, category), timeout=10.0)
                )
            finally:
                loop.close()
        
        # Cache the result
        simple_cache.set(cache_key, result, 'news')
        return result
        
    except (asyncio.TimeoutError, concurrent.futures.TimeoutError):
        logger.warning("Sync news fetch timed out")
        # Try to return cached fallback
        fallback_key = f"news_fallback_{category or 'all'}_{limit}"
        fallback = simple_cache.get(fallback_key, 'news')
        return fallback if fallback else []
    except Exception as e:
        logger.error(f"Error in sync news fetch: {e}")
        # Return empty list instead of None to avoid template errors
        return []

def _run_async_news_fetch(limit: int, category: Optional[str]) -> List[NewsArticle]:
    """Helper function to run async news fetch in new thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(
            asyncio.wait_for(news_service.get_latest_news(limit, category), timeout=10.0)
        )
    finally:
        loop.close()
        return []

def search_news_sync(query: str, limit: int = 20) -> List[NewsArticle]:
    """Synchronous wrapper for news search"""
    try:
        if not query or not query.strip():
            # Return some general financial news when no query
            return get_latest_news_sync(limit)
        
        # Create mock search results based on query
        mock_articles = []
        for i in range(min(limit, 10)):
            article = NewsArticle(
                title=f"Søkeresultat for '{query}' - Artikkel {i+1}",
                summary=f"Dette er en finansiell nyhet relatert til søket '{query}'. Artikkelen inneholder relevant informasjon om dette emnet.",
                link=f"https://example.com/news/{query.lower().replace(' ', '-')}-{i+1}",
                source="Finanstidende",
                published=datetime.now() - timedelta(hours=i),
                image_url="https://via.placeholder.com/400x200/0066cc/ffffff?text=Finansnyhet",
                relevance_score=1.0 - (i * 0.1),
                categories=["finansiell", "søk"]
            )
            mock_articles.append(article)
        
        return mock_articles
        
    except Exception as e:
        logger.error(f"Error in news search: {e}")
        return []

def get_company_news_sync(company_symbol: str, limit: int = 5) -> List[NewsArticle]:
    """Synchronous wrapper for company news"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(news_service.get_company_news(company_symbol, limit))
    except Exception as e:
        logger.error(f"Error in sync company news fetch: {e}")
        return []
