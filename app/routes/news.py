"""
News Blueprint for Aksjeradar
Handles news-related routes and functionality
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from ..services.news_service import NewsService
from ..services.data_service import DataService
from ..utils.access_control import demo_access, access_required
from datetime import datetime, timedelta
import logging
import asyncio

news_bp = Blueprint('news_bp', __name__)
logger = logging.getLogger(__name__)

# Initialize news service
try:
    news_service = NewsService()
except Exception as e:
    logger.warning(f"Could not initialize NewsService: {e}")
    news_service = None

# Helper functions for news data
def get_company_news_sync(symbol, limit=5):
    """Get company news synchronously with mock data"""
    mock_articles = [
        type('Article', (), {
            'title': f'{symbol} viser sterk utvikling',
            'summary': f'Selskapet {symbol} rapporterer positive resultater.',
            'link': f'https://aksjeradar.trade/news/{symbol.lower()}-positive-results',
            'source': 'Finansavisen',
            'published': datetime.now() - timedelta(hours=1),
            'image_url': None,
            'relevance_score': 0.8,
            'categories': ['norwegian', 'stocks']
        })(),
        type('Article', (), {
            'title': f'{symbol} lanserer ny strategi',
            'summary': f'Ny strategi kan påvirke {symbol}s fremtidige vekst.',
            'link': f'https://aksjeradar.trade/news/{symbol.lower()}-new-strategy',
            'source': 'E24',
            'published': datetime.now() - timedelta(hours=3),
            'image_url': None,
            'relevance_score': 0.7,
            'categories': ['norwegian', 'strategy']
        })()
    ]
    return mock_articles[:limit]

def get_latest_news_sync(limit=10, category='all'):
    """Get latest news synchronously with comprehensive mock data"""
    mock_articles = [
        type('Article', (), {
            'title': 'Oslo Børs stiger på bred front - OSEBX opp 1,2%',
            'summary': 'Hovedindeksen stiger 1,2% i åpningen etter positive signaler fra USA og sterke kvartalstall fra Equinor.',
            'link': 'https://aksjeradar.trade/news/oslo-bors-stiger',
            'source': 'Dagens Næringsliv',
            'published': datetime.now(),
            'image_url': None,
            'relevance_score': 0.9,
            'categories': ['norwegian', 'market']
        })(),
        type('Article', (), {
            'title': 'Equinor leverer sterke kvartalstall',
            'summary': 'Oljeselskapet Equinor rapporterer overskudd på 4,9 milliarder dollar i tredje kvartal.',
            'link': 'https://aksjeradar.trade/news/equinor-kvartalstall',
            'source': 'E24',
            'published': datetime.now() - timedelta(hours=1),
            'image_url': None,
            'relevance_score': 0.9,
            'categories': ['norwegian', 'energy']
        })(),
        type('Article', (), {
            'title': 'DNB Bank øker utbytte etter solid resultat',
            'summary': 'Norges største bank øker kvartalsutbyttet til 2,70 kroner per aksje.',
            'link': 'https://aksjeradar.trade/news/dnb-utbytte',
            'source': 'Finansavisen',
            'published': datetime.now() - timedelta(hours=2),
            'image_url': None,
            'relevance_score': 0.8,
            'categories': ['norwegian', 'banking']
        })(),
        type('Article', (), {
            'title': 'Teknologi-aksjer i vinden på Wall Street',
            'summary': 'NASDAQ stiger 2,1% på grunn av sterke tall fra teknologiselskaper.',
            'link': 'https://aksjeradar.trade/news/tech-aksjer-vinden',
            'source': 'Reuters',
            'published': datetime.now() - timedelta(hours=3),
            'image_url': None,
            'relevance_score': 0.8,
            'categories': ['international', 'tech']
        })(),
        type('Article', (), {
            'title': 'Bitcoin klatrer over $45,000',
            'summary': 'Kryptovalutaen Bitcoin fortsetter oppgangen og har nå steget 15% denne uken.',
            'link': 'https://aksjeradar.trade/news/bitcoin-stiger',
            'source': 'CoinDesk',
            'published': datetime.now() - timedelta(hours=4),
            'image_url': None,
            'relevance_score': 0.7,
            'categories': ['crypto', 'international']
        })(),
        type('Article', (), {
            'title': 'Norsk Hydro med solid margin på aluminium',
            'summary': 'Aluminiumsprodusenten drar nytte av høye priser og sterk etterspørsel.',
            'link': 'https://aksjeradar.trade/news/hydro-aluminium',
            'source': 'Hegnar Online',
            'published': datetime.now() - timedelta(hours=5),
            'image_url': None,
            'relevance_score': 0.8,
            'categories': ['norwegian', 'materials']
        })(),
        type('Article', (), {
            'title': 'Fed holder renten uendret',
            'summary': 'Den amerikanske sentralbanken holder styringsrenten i området 5,25-5,50 prosent.',
            'link': 'https://aksjeradar.trade/news/fed-rente',
            'source': 'Financial Times',
            'published': datetime.now() - timedelta(hours=6),
            'image_url': None,
            'relevance_score': 0.9,
            'categories': ['international', 'monetary']
        })(),
        type('Article', (), {
            'title': 'Telenor vurderer salg av asiatiske eiendeler',
            'summary': 'Telekomgiganten ser på strategiske alternativer for sine investeringer i Asia.',
            'link': 'https://aksjeradar.trade/news/telenor-asia',
            'source': 'Dagens Næringsliv',
            'published': datetime.now() - timedelta(hours=7),
            'image_url': None,
            'relevance_score': 0.7,
            'categories': ['norwegian', 'telecom']
        })(),
        type('Article', (), {
            'title': 'Renewable Energy ETF ser stor tilstrømming',
            'summary': 'Investorer strømmer til fornybar energi-fond etter nye klimamål.',
            'link': 'https://aksjeradar.trade/news/renewable-etf',
            'source': 'MarketWatch',
            'published': datetime.now() - timedelta(hours=8),
            'image_url': None,
            'relevance_score': 0.6,
            'categories': ['international', 'energy']
        })(),
        type('Article', (), {
            'title': 'Mowi med sterk laksepris i Q3',
            'summary': 'Verdens største lakseoppdrettsselskap drar nytte av høye laksepriser.',
            'link': 'https://aksjeradar.trade/news/mowi-laksepris',
            'source': 'IntraFish',
            'published': datetime.now() - timedelta(hours=9),
            'image_url': None,
            'relevance_score': 0.7,
            'categories': ['norwegian', 'seafood']
        })()
    ]
    
    if category != 'all':
        filtered = [a for a in mock_articles if category in a.categories]
        return filtered[:limit]
    return mock_articles[:limit]

@news_bp.route('/')
@demo_access
def index():
    """News main page without debug output"""
    try:
        # Get news articles without debug output using mock data
        news_articles = get_latest_news_sync(limit=20, category='all')
        
        # Get categories
        categories = ['alle', 'aksjer', 'økonomi', 'marked', 'crypto']
        selected_category = request.args.get('category', 'alle')
        
        # Filter by category if specified
        if selected_category != 'alle':
            # Filter mock data by category if needed
            pass
        
        return render_template('news/index.html',
                             news_articles=news_articles,
                             categories=categories,
                             selected_category=selected_category,
                             current_category=selected_category)
                             
    except Exception as e:
        logger.error(f"Error in news index: {e}")
        return render_template('news/index.html',
                             news_articles=[],
                             categories=['alle', 'aksjer', 'økonomi', 'marked', 'crypto'],
                             selected_category='alle',
                             current_category='alle',
                             error="Kunne ikke laste nyheter")

@news_bp.route('/<slug>')
@demo_access
def article(slug):
    """Individual news article with proper routing"""
    try:
        # Get article by slug
        article_data = DataService.get_news_article_by_slug(slug)
        
        if not article_data:
            flash('Artikkelen ble ikke funnet.', 'error')
            return redirect(url_for('news.index'))
        
        # Get related articles
        related_articles = DataService.get_related_news(slug, limit=5) or []
        
        return render_template('news/article.html',
                             article=article_data,
                             related_articles=related_articles)
                             
    except Exception as e:
        logger.error(f"Error loading news article {slug}: {e}")
        flash('Beklager, en feil oppsto. Vi jobber med å løse problemet.', 'error')
        return redirect(url_for('news.index'))

@news_bp.route('/api/latest')
@demo_access
def api_latest_news():
    """API endpoint for latest news with robust error handling"""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)  # Cap at 50
        category = request.args.get('category', 'all')
        
        # Use the sync function for API calls with fallback
        try:
            news_articles = get_latest_news_sync(limit=limit, category=category)
        except Exception as news_error:
            logger.warning(f"News service error: {news_error}")
            # Fallback to mock data
            news_articles = [
                type('Article', (), {
                    'title': 'Markedet stiger på Oslo Børs',
                    'summary': 'Positive nyheter fra norske selskaper driver markedet oppover.',
                    'link': 'https://aksjeradar.trade/news/market-rise',
                    'source': 'Finansavisen',
                    'published': datetime.now() - timedelta(hours=1),
                    'image_url': None,
                    'relevance_score': 0.8
                })(),
                type('Article', (), {
                    'title': 'Nye investeringsmuligheter',
                    'summary': 'Eksperter anbefaler å se på teknologiaksjer.',
                    'link': 'https://aksjeradar.trade/news/tech-opportunities', 
                    'source': 'E24',
                    'published': datetime.now() - timedelta(hours=2),
                    'image_url': None,
                    'relevance_score': 0.7
                })()
            ][:limit]
        
        # Convert to JSON-serializable format
        articles_data = []
        for article in news_articles:
            try:
                articles_data.append({
                    'title': getattr(article, 'title', 'Ukjent tittel'),
                    'summary': getattr(article, 'summary', 'Ingen sammendrag tilgjengelig'),
                    'link': getattr(article, 'link', '#'),
                    'source': getattr(article, 'source', 'Ukjent kilde'),
                    'published': getattr(article, 'published', datetime.now()).isoformat() if hasattr(article, 'published') and article.published else datetime.now().isoformat(),
                    'image_url': getattr(article, 'image_url', None),
                    'relevance_score': getattr(article, 'relevance_score', 0.5)
                })
            except Exception as article_error:
                logger.warning(f"Error processing article: {article_error}")
                continue
        
        return jsonify({
            'success': True,
            'articles': articles_data,
            'total': len(articles_data),
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Critical error in API latest news: {e}")
        return jsonify({
            'success': False,
            'error': 'Kunne ikke laste nyheter',
            'articles': [],
            'total': 0
        }), 500

@news_bp.route('/article/<int:article_id>')
@demo_access
def article_by_id(article_id):
    """Individual news article by ID"""
    try:
        article_data = NewsService.get_article_by_id(article_id)
        
        if not article_data:
            return render_template('news/article.html', 
                                 article=None,
                                 error="Artikkel ikke funnet")
        
        return render_template('news/article.html', article=article_data)
        
    except Exception as e:
        logger.error(f"Error loading article {article_id}: {e}")
        return render_template('news/article.html', 
                             article=None,
                             error="Feil ved lasting av artikkel")

@news_bp.route('/search')
@demo_access
def search():
    """News search"""
    query = request.args.get('q', '')
    results = []
    
    if query:
        try:
            results = NewsService.search_news(query)
        except Exception as e:
            logger.error(f"Error searching news for {query}: {e}")
    
    return render_template('news/search.html', 
                         query=query, 
                         results=results)

@news_bp.route('/category/<category>')
@demo_access
def category(category):
    """News by category"""
    try:
        if news_service:
            news_articles = news_service.get_news_by_category(category)
        else:
            # Mock data when service is not available
            news_articles = [
                type('Article', (), {
                    'title': f'Siste nytt fra {category}',
                    'summary': f'Dette er en eksempelnyhet innen kategorien {category}.',
                    'link': f'https://aksjeradar.trade/news/{category}-sample',
                    'source': 'Aksjeradar',
                    'published': datetime.now() - timedelta(hours=i),
                    'image_url': None,
                    'relevance_score': 0.8,
                    'categories': [category]
                })() for i in range(1, 6)
            ]
        
        return render_template('news/category_simple.html',
                             news_articles=news_articles,
                             category=category)
                             
    except Exception as e:
        logger.error(f"Error loading category {category}: {e}")
        # Return with mock data instead of empty list
        mock_articles = [
            type('Article', (), {
                'title': f'Eksempelnyhet - {category}',
                'summary': f'Dette er en demo-nyhet for kategorien {category}.',
                'link': f'https://aksjeradar.trade/news/{category}-demo',
                'source': 'Demo',
                'published': datetime.now(),
                'image_url': None,
                'relevance_score': 0.5,
                'categories': [category]
            })()
        ]
        return render_template('news/category_simple.html',
                             news_articles=mock_articles,
                             category=category,
                             error="Feil ved lasting av kategori - viser demo-data")

@news_bp.route('/widget')
@demo_access
def widget():
    """News widget for embedding"""
    try:
        limit = request.args.get('limit', 5, type=int)
        news_articles = NewsService.get_latest_news(limit=limit)
        
        return render_template('news/widget.html', 
                             news_articles=news_articles)
                             
    except Exception as e:
        logger.error(f"Error loading news widget: {e}")
        return render_template('news/widget.html', news_articles=[])

@news_bp.route('/embed')
@demo_access
def embed():
    """Embeddable news feed"""
    try:
        limit = request.args.get('limit', 10, type=int)
        style = request.args.get('style', 'default')
        
        news_articles = NewsService.get_latest_news(limit=limit)
        
        return render_template('news/embed.html',
                             news_articles=news_articles,
                             style=style)
                             
    except Exception as e:
        logger.error(f"Error loading embed: {e}")
        return render_template('news/embed.html', news_articles=[])

@news_bp.route('/api/company/<string:symbol>')
@access_required
def api_company_news(symbol):
    """API endpoint for company-specific news"""
    try:
        limit = int(request.args.get('limit', 5))
        limit = min(max(limit, 1), 20)  # Between 1 and 20
        
        # Get company news
        news_articles = get_company_news_sync(symbol, limit=limit)
        
        # Convert to dict for JSON response
        articles_data = []
        for article in news_articles:
            articles_data.append({
                'title': article.title,
                'summary': article.summary,
                'link': article.link,
                'source': article.source,
                'published': article.published.isoformat(),
                'image_url': article.image_url,
                'relevance_score': article.relevance_score,
                'categories': article.categories or []
            })
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'articles': articles_data,
            'count': len(articles_data),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API company news: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'articles': []
        }), 500

@news_bp.route('/api/market-summary')
@access_required
def api_market_summary():
    """API endpoint for categorized market news"""
    try:
        # Get market summary
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        categorized_news = loop.run_until_complete(news_service.get_market_summary_news())
        
        # Convert to JSON-serializable format
        result = {}
        for category, articles in categorized_news.items():
            result[category] = []
            for article in articles:
                result[category].append({
                    'title': article.title,
                    'summary': article.summary,
                    'link': article.link,
                    'source': article.source,
                    'published': article.published.isoformat(),
                    'image_url': article.image_url,
                    'relevance_score': article.relevance_score,
                    'categories': article.categories or []
                })
        
        return jsonify({
            'success': True,
            'market_news': result,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API market summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'market_news': {}
        }), 500

@news_bp.route('/api/market-overview')
@access_required
def api_market_overview():
    """Get structured market overview with Norwegian and international news"""
    try:
        # Get Norwegian news
        norwegian_news = get_latest_news_sync(limit=10, category='norwegian')
        
        # Get international news  
        international_news = get_latest_news_sync(limit=10, category='international')
        
        return jsonify({
            'success': True,
            'overview': {
                'norwegian': [
                    {
                        'title': article.title,
                        'summary': article.summary,
                        'link': article.link,
                        'source': article.source,
                        'published': article.published.isoformat() if article.published else None,
                        'image_url': article.image_url,
                        'relevance_score': article.relevance_score
                    } for article in norwegian_news
                ],
                'international': [
                    {
                        'title': article.title,
                        'summary': article.summary,
                        'link': article.link,
                        'source': article.source,
                        'published': article.published.isoformat() if article.published else None,
                        'image_url': article.image_url,
                        'relevance_score': article.relevance_score
                    } for article in international_news
                ],
                'last_updated': datetime.now().isoformat(),
                'total_articles': len(norwegian_news) + len(international_news)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch market overview'
        }), 500

@news_bp.route('/api/stock/<stock_symbol>')
@access_required
def api_stock_news(stock_symbol):
    """Get news for a specific stock symbol"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(max(limit, 1), 20)
        
        # Get stock-specific news
        stock_news = get_company_news_sync(stock_symbol, limit=limit)
        
        return jsonify({
            'success': True,
            'stock_symbol': stock_symbol,
            'articles': [
                {
                    'title': article.title,
                    'summary': article.summary,
                    'link': article.link,
                    'source': article.source,
                    'published': article.published.isoformat() if article.published else None,
                    'image_url': article.image_url,
                    'relevance_score': article.relevance_score
                } for article in stock_news
            ],
            'count': len(stock_news),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting stock news for {stock_symbol}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch news for {stock_symbol}'
        }), 500

@news_bp.route('/api/trending')
@access_required
def api_trending_news():
    """Get trending financial news based on relevance and recency"""
    try:
        limit = request.args.get('limit', 15, type=int)
        limit = min(max(limit, 1), 30)
        
        # Get latest news and sort by relevance
        all_news = get_latest_news_sync(limit=50, category='all')
        
        # Filter for high-relevance articles from the last 24 hours
        now = datetime.now()
        trending_articles = []
        
        for article in all_news:
            hours_old = (now - article.published).total_seconds() / 3600
            if hours_old <= 24 and article.relevance_score >= 5:  # Recent and relevant
                trending_articles.append(article)
        
        # Sort by relevance score and take top articles
        trending_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        trending_articles = trending_articles[:limit]
        
        return jsonify({
            'success': True,
            'trending_articles': [
                {
                    'title': article.title,
                    'summary': article.summary,
                    'link': article.link,
                    'source': article.source,
                    'published': article.published.isoformat(),
                    'image_url': article.image_url,
                    'relevance_score': article.relevance_score,
                    'categories': article.categories or []
                } for article in trending_articles
            ],
            'count': len(trending_articles),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting trending news: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch trending news'
        }), 500

@news_bp.route('/api/sources')
@access_required
def api_news_sources():
    """Get information about available news sources"""
    try:
        sources_info = []
        for source_id, config in news_service.news_sources.items():
            sources_info.append({
                'id': source_id,
                'name': config['name'],
                'category': config['category'],
                'priority': config['priority'],
                'base_url': config['base_url']
            })
        
        # Sort by priority and category
        sources_info.sort(key=lambda x: (x['category'], -x['priority']))
        
        return jsonify({
            'success': True,
            'sources': sources_info,
            'total_sources': len(sources_info),
            'categories': ['norwegian', 'international']
        })
        
    except Exception as e:
        logger.error(f"Error getting news sources: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch news sources'
        }), 500

@news_bp.route('/embed')
def news_embed():
    """Embeddable news widget for dashboard"""
    try:
        limit = request.args.get('limit', 5, type=int)
        category = request.args.get('category', 'norwegian')
        show_images = request.args.get('images', 'true').lower() == 'true'
        
        limit = min(max(limit, 1), 10)
        
        # Get news articles
        articles = get_latest_news_sync(limit=limit, category=category)
        
        return render_template('news/embed.html', 
                             articles=articles, 
                             category=category,
                             show_images=show_images,
                             datetime=datetime)
        
    except Exception as e:
        logger.error(f"Error in news embed: {e}")
        return render_template('news/embed.html', 
                             articles=[], 
                             category=category,
                             show_images=False,
                             datetime=datetime)

@news_bp.route('/<slug>')
def article_detail(slug):
    """Display specific news article"""
    try:
        # Define our news articles with consistent data
        articles_map = {
            'teknologi-marked-oppgang': {
                'title': 'Marked stiger på positiv teknologi-utvikling',
                'content': 'Teknologiaksjer opplevde sterk vekst i dag etter positive kvartalsrapporter fra flere store selskaper. Investorer viser økt tillit til teknologisektorens fremtidsutsikter, med særlig fokus på kunstig intelligens og bærekraftige teknologier. Børsene viser bred oppgang, og analytikere forventer fortsatt positiv utvikling.',
                'source': 'Finansavisen',
                'published': datetime.now().isoformat(),
                'symbol': 'TECH'
            },
            'energi-sektor-press': {
                'title': 'Energisektoren under press',
                'content': 'Olje- og gasspriser faller på grunn av global økonomisk usikkerhet. Energiselskaper opplever reduserte inntekter, og investorer er bekymret for fremtidige utbyteutbetalinger. Equinor og andre norske energiselskaper følges tett, da de spiller en viktig rolle i norsk økonomi.',
                'source': 'E24',
                'published': (datetime.now() - timedelta(hours=2)).isoformat(),
                'symbol': 'EQNR.OL'
            },
            'oslo-bors-stiger': {
                'title': 'Oslo Børs stiger på bred front',
                'content': 'Hovedindeksen på Oslo Børs stiger 1,2% i åpningen etter positive signaler fra USA. Investorer viser økt risikoappetitt, og flere sektorer bidrar til oppgangen. Finansaksjer og teknologiselskaper leder an, mens energisektoren holder seg stabil.',
                'source': 'Dagens Næringsliv',
                'published': datetime.now().isoformat(),
                'symbol': 'OSEBX'
            },
            'bitcoin-nye-hoyder': {
                'title': 'Bitcoin når nye høyder',
                'content': 'Kryptovalutaen Bitcoin har steget 5% i løpet av dagen og nærmer seg historiske toppnivåer. Økt institusjonell interesse og positive reguleringssignaler bidrar til oppgangen. Andre kryptovalutaer følger også opp med betydelige gevinster.',
                'source': 'CoinDesk',
                'published': (datetime.now() - timedelta(hours=2)).isoformat(),
                'symbol': 'BTC-USD'
            },
            'equinor-kvartalstall': {
                'title': 'Equinor presenterer sterke kvartalstall',
                'content': 'Energigiganten leverer bedre enn ventet resultat for fjerde kvartal. Høye olje- og gasspriser kombinert med operasjonell effektivitet gir sterke finansielle resultater. Selskapet øker utbyttet og annonserer nye investeringer i fornybar energi.',
                'source': 'E24',
                'published': (datetime.now() - timedelta(hours=1)).isoformat(),
                'symbol': 'EQNR.OL'
            },
            'dnb-solid-vekst': {
                'title': 'DNB Bank viser solid vekst',
                'content': 'Norges største bank rapporterer økt utlånsvolum og reduserte tap. Bankens digitale satsning gir resultater, og kundene tar i bruk nye tjenester i økende grad. Ledelsen er optimistisk for fortsatt vekst i det norske markedet.',
                'source': 'Finansavisen',
                'published': (datetime.now() - timedelta(hours=3)).isoformat(),
                'symbol': 'DNB.OL'
            },
            'tech-aksjer-wall-street': {
                'title': 'Tech-aksjer i vinden på Wall Street',
                'content': 'Store teknologiselskaper drar markedene oppover i USA. Apple, Microsoft og Google alle viser sterke resultater, og investorer satser på fortsatt digital transformasjon. Kunstig intelligens-selskaper opplever særlig stor interesse.',
                'source': 'CNBC',
                'published': (datetime.now() - timedelta(hours=4)).isoformat(),
                'symbol': 'TECH'
            },
            'sentralbank-rente-beslutning': {
                'title': 'Sentralbanken holder renten uendret',
                'content': 'Norges Bank besluttet å holde styringsrenten på dagens nivå. Sentralbanken viser til balansert økonomisk utvikling og stabil inflasjon. Markedet hadde ventet denne beslutningen, og responsens har vært dempet.',
                'source': 'DN',
                'published': (datetime.now() - timedelta(hours=4)).isoformat(),
                'symbol': 'NOK'
            },
            'krypto-volatilitet': {
                'title': 'Kryptovaluta marked volatilt',
                'content': 'Bitcoin og andre kryptovalutaer opplever store svingninger denne uken. Regulatoriske bekymringer møter optimisme rundt institusjonell adopsjon. Tradere anbefales forsiktighet i det volatile markedet.',
                'source': 'CryptoNews',
                'published': (datetime.now() - timedelta(hours=6)).isoformat(),
                'symbol': 'BTC-USD'
            }
        }
        
        # Get article or return 404
        article_data = articles_map.get(slug)
        if not article_data:
            from flask import abort
            abort(404)
        
        return render_template('news/article.html', article=article_data)
        
    except Exception as e:
        logger.error(f"Error loading news article {slug}: {e}")
        return render_template('error.html', error=f"Kunne ikke laste artikkel: {e}")
    except Exception as e:
        logger.error(f"Error loading news article {slug}: {e}")
        return render_template('error.html', error=f"Kunne ikke laste artikkel: {e}")
