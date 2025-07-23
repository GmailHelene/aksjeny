"""
Advanced News & Sentiment Analysis Blueprint
==========================================

Real-time news aggregation and AI-powered sentiment analysis
with market intelligence and impact scoring.
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from ..decorators import access_required
from ..services.news_aggregation_service import NewsAggregationService
from ..services.sentiment_analysis_service import SentimentAnalysisService
import logging
import json
from typing import List

logger = logging.getLogger(__name__)

news_intelligence = Blueprint('news_intelligence', __name__, url_prefix='/news-intelligence')

@news_intelligence.route('/')
@access_required
def news_dashboard():
    """Main news intelligence dashboard"""
    try:
        return render_template('news_intelligence/dashboard.html',
                             title='News Intelligence Dashboard')
    except Exception as e:
        logger.error(f"News dashboard error: {e}")
        return render_template('error.html', error=str(e)), 500

@news_intelligence.route('/sentiment-analysis')
@access_required
def sentiment_page():
    """Sentiment analysis interface"""
    try:
        return render_template('news_intelligence/sentiment.html',
                             title='AI Sentiment Analysis')
    except Exception as e:
        logger.error(f"Sentiment page error: {e}")
        return render_template('error.html', error=str(e)), 500

@news_intelligence.route('/api/real-time-news')
@access_required
def api_real_time_news():
    """API endpoint for real-time news collection"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        category = request.args.get('category', None)
        source = request.args.get('source', None)
        min_impact = request.args.get('min_impact', 0.0, type=float)
        
        # Collect news
        news_result = NewsAggregationService.collect_all_news()
        
        if not news_result['success']:
            return jsonify(news_result), 500
        
        # Filter articles based on parameters
        articles = news_result['articles']
        
        if category:
            articles = [a for a in articles if category in a.get('market_categories', [])]
        
        if source:
            articles = [a for a in articles if a.get('source') == source]
        
        if min_impact > 0:
            articles = [a for a in articles if a.get('market_impact_score', 0) >= min_impact]
        
        # Sort by relevance and age
        articles.sort(key=lambda x: (x.get('market_impact_score', 0), -x.get('age_hours', 24)), reverse=True)
        
        # Limit results
        articles = articles[:limit]
        
        return jsonify({
            'success': True,
            'total_articles': len(articles),
            'articles': articles,
            'filters_applied': {
                'category': category,
                'source': source,
                'min_impact': min_impact,
                'limit': limit
            },
            'source_stats': news_result.get('source_stats', {}),
            'timestamp': news_result['collection_time']
        })
        
    except Exception as e:
        logger.error(f"Real-time news API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_intelligence.route('/api/sentiment-analysis', methods=['POST'])
@access_required
def api_sentiment_analysis():
    """API endpoint for sentiment analysis"""
    try:
        data = request.get_json()
        
        # Get analysis type
        analysis_type = data.get('type', 'batch')  # 'single', 'batch', 'trends'
        
        if analysis_type == 'single':
            # Single article analysis
            article = data.get('article', {})
            if not article:
                return jsonify({
                    'success': False,
                    'error': 'Article data is required for single analysis'
                }), 400
            
            result = SentimentAnalysisService.analyze_article_sentiment(article)
            
        elif analysis_type == 'batch':
            # Batch analysis
            articles = data.get('articles', [])
            if not articles:
                return jsonify({
                    'success': False,
                    'error': 'Articles data is required for batch analysis'
                }), 400
            
            result = SentimentAnalysisService.analyze_batch_sentiment(articles)
            
        elif analysis_type == 'trends':
            # Sentiment trends
            timeframe_hours = data.get('timeframe_hours', 24)
            result = SentimentAnalysisService.get_sentiment_trends(timeframe_hours)
            
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid analysis type. Use: single, batch, or trends'
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Sentiment analysis API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_intelligence.route('/api/company-news/<symbol>')
@access_required
def api_company_news(symbol):
    """API endpoint for company-specific news and sentiment"""
    try:
        company_name = request.args.get('company_name', None)
        include_sentiment = request.args.get('include_sentiment', 'true').lower() == 'true'
        
        # Get company-specific news
        news_result = NewsAggregationService.get_company_specific_news(
            company_symbol=symbol,
            company_name=company_name
        )
        
        if not news_result['success']:
            return jsonify(news_result), 500
        
        response_data = news_result
        
        # Add sentiment analysis if requested
        if include_sentiment and news_result.get('articles'):
            sentiment_result = SentimentAnalysisService.get_company_sentiment(
                company_symbol=symbol,
                articles=news_result['articles']
            )
            
            if sentiment_result['success']:
                response_data['sentiment_analysis'] = sentiment_result
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Company news API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_intelligence.route('/api/market-impact')
@access_required
def api_market_impact():
    """API endpoint for market impact analysis"""
    try:
        # Get recent high-impact news
        news_result = NewsAggregationService.collect_all_news()
        
        if not news_result['success']:
            return jsonify(news_result), 500
        
        # Filter for high-impact articles
        high_impact_articles = [
            article for article in news_result['articles']
            if article.get('market_impact_score', 0) > 0.5
        ]
        
        # Sort by impact score
        high_impact_articles.sort(
            key=lambda x: x.get('market_impact_score', 0),
            reverse=True
        )
        
        # Analyze sentiment for high-impact articles
        if high_impact_articles:
            batch_sentiment = SentimentAnalysisService.analyze_batch_sentiment(
                high_impact_articles[:20]  # Top 20 high-impact articles
            )
        else:
            batch_sentiment = {'success': True, 'sentiment_summary': {'overall_mood': 'No high-impact news'}}
        
        # Market impact summary
        impact_summary = _calculate_market_impact_summary(high_impact_articles)
        
        return jsonify({
            'success': True,
            'high_impact_articles': high_impact_articles[:10],  # Top 10 for display
            'total_high_impact': len(high_impact_articles),
            'sentiment_analysis': batch_sentiment,
            'impact_summary': impact_summary,
            'timestamp': news_result['collection_time']
        })
        
    except Exception as e:
        logger.error(f"Market impact API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_intelligence.route('/api/trending-topics')
@access_required
def api_trending_topics():
    """API endpoint for trending topics analysis"""
    try:
        trending_result = NewsAggregationService.get_trending_topics()
        
        if not trending_result['success']:
            return jsonify(trending_result), 500
        
        # Enhance trending topics with sentiment
        enhanced_topics = []
        for topic in trending_result['trending_topics']:
            # Mock sentiment for trending topics (would use real analysis in production)
            topic_sentiment = _calculate_topic_sentiment(topic)
            topic['sentiment_analysis'] = topic_sentiment
            enhanced_topics.append(topic)
        
        return jsonify({
            'success': True,
            'trending_topics': enhanced_topics,
            'total_articles_analyzed': trending_result['total_articles_analyzed'],
            'analysis_time': trending_result['analysis_time']
        })
        
    except Exception as e:
        logger.error(f"Trending topics API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_intelligence.route('/api/news-alerts', methods=['POST'])
@access_required
def api_news_alerts():
    """API endpoint for intelligent news alerts"""
    try:
        data = request.get_json()
        
        # Alert configuration
        alert_config = {
            'keywords': data.get('keywords', []),
            'companies': data.get('companies', []),
            'sentiment_threshold': data.get('sentiment_threshold', 0.5),
            'impact_threshold': data.get('impact_threshold', 0.6),
            'categories': data.get('categories', [])
        }
        
        # Get recent news
        news_result = NewsAggregationService.collect_all_news()
        
        if not news_result['success']:
            return jsonify(news_result), 500
        
        # Filter articles based on alert criteria
        alert_articles = _filter_articles_for_alerts(news_result['articles'], alert_config)
        
        # Analyze sentiment for alert articles
        if alert_articles:
            alert_sentiment = SentimentAnalysisService.analyze_batch_sentiment(alert_articles)
        else:
            alert_sentiment = {'success': True, 'individual_results': []}
        
        # Generate alert recommendations
        alert_recommendations = _generate_alert_recommendations(alert_articles, alert_sentiment)
        
        return jsonify({
            'success': True,
            'alert_config': alert_config,
            'triggered_articles': len(alert_articles),
            'articles': alert_articles[:10],  # Top 10 alerts
            'sentiment_analysis': alert_sentiment,
            'recommendations': alert_recommendations,
            'timestamp': news_result['collection_time']
        })
        
    except Exception as e:
        logger.error(f"News alerts API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@news_intelligence.route('/api/news-summary')
@access_required
def api_news_summary():
    """API endpoint for AI-generated news summary"""
    try:
        timeframe = request.args.get('timeframe', '24h')  # 24h, 1w, 1m
        category = request.args.get('category', 'all')
        
        # Get news data
        news_result = NewsAggregationService.collect_all_news()
        
        if not news_result['success']:
            return jsonify(news_result), 500
        
        # Filter by timeframe and category
        filtered_articles = _filter_articles_by_timeframe_and_category(
            news_result['articles'], timeframe, category
        )
        
        # Generate intelligent summary
        summary = _generate_intelligent_news_summary(filtered_articles)
        
        # Sentiment overview
        if filtered_articles:
            sentiment_overview = SentimentAnalysisService.analyze_batch_sentiment(filtered_articles)
        else:
            sentiment_overview = {'success': True, 'sentiment_summary': {'overall_mood': 'No news available'}}
        
        return jsonify({
            'success': True,
            'timeframe': timeframe,
            'category': category,
            'articles_analyzed': len(filtered_articles),
            'summary': summary,
            'sentiment_overview': sentiment_overview,
            'timestamp': news_result['collection_time']
        })
        
    except Exception as e:
        logger.error(f"News summary API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions

def _calculate_market_impact_summary(articles: List[dict]) -> dict:
    """Calculate market impact summary metrics"""
    if not articles:
        return {'total_impact': 0, 'impact_distribution': {}, 'key_themes': []}
    
    total_impact = sum(article.get('market_impact_score', 0) for article in articles)
    avg_impact = total_impact / len(articles)
    
    # Impact distribution
    impact_distribution = {'high': 0, 'medium': 0, 'low': 0}
    for article in articles:
        impact = article.get('market_impact_score', 0)
        if impact > 0.7:
            impact_distribution['high'] += 1
        elif impact > 0.4:
            impact_distribution['medium'] += 1
        else:
            impact_distribution['low'] += 1
    
    # Key themes
    key_themes = []
    all_categories = []
    for article in articles:
        all_categories.extend(article.get('market_categories', []))
    
    # Count category frequency
    from collections import Counter
    category_counts = Counter(all_categories)
    key_themes = [{'theme': cat, 'frequency': count} for cat, count in category_counts.most_common(5)]
    
    return {
        'total_impact': round(total_impact, 2),
        'average_impact': round(avg_impact, 3),
        'impact_distribution': impact_distribution,
        'key_themes': key_themes
    }

def _calculate_topic_sentiment(topic: dict) -> dict:
    """Calculate sentiment for a trending topic"""
    # Mock sentiment calculation (would use real analysis in production)
    import random
    
    sentiment_score = random.uniform(-0.5, 0.5)
    sentiment_label = 'Positive' if sentiment_score > 0.1 else 'Negative' if sentiment_score < -0.1 else 'Neutral'
    
    return {
        'sentiment_score': round(sentiment_score, 3),
        'sentiment_label': sentiment_label,
        'confidence': round(random.uniform(0.6, 0.9), 3)
    }

def _filter_articles_for_alerts(articles: List[dict], alert_config: dict) -> List[dict]:
    """Filter articles based on alert configuration"""
    filtered = []
    
    for article in articles:
        # Check keywords
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        keyword_match = False
        if alert_config['keywords']:
            keyword_match = any(keyword.lower() in text for keyword in alert_config['keywords'])
        
        # Check companies
        company_match = False
        if alert_config['companies']:
            company_match = any(company.lower() in text for company in alert_config['companies'])
        
        # Check categories
        category_match = False
        if alert_config['categories']:
            article_categories = article.get('market_categories', [])
            category_match = any(cat in article_categories for cat in alert_config['categories'])
        
        # Check impact threshold
        impact_match = article.get('market_impact_score', 0) >= alert_config['impact_threshold']
        
        # Include if any criteria match
        if keyword_match or company_match or category_match or impact_match:
            filtered.append(article)
    
    return filtered

def _generate_alert_recommendations(articles: List[dict], sentiment_data: dict) -> List[str]:
    """Generate intelligent alert recommendations"""
    recommendations = []
    
    if not articles:
        recommendations.append("No articles match your alert criteria")
        return recommendations
    
    # High impact recommendations
    high_impact_count = sum(1 for a in articles if a.get('market_impact_score', 0) > 0.7)
    if high_impact_count > 0:
        recommendations.append(f"{high_impact_count} high-impact articles detected - review immediately")
    
    # Sentiment-based recommendations
    if sentiment_data.get('success') and sentiment_data.get('sentiment_summary'):
        mood = sentiment_data['sentiment_summary'].get('overall_mood', '')
        if 'Bearish' in mood:
            recommendations.append("Negative sentiment detected - monitor portfolio positions")
        elif 'Bullish' in mood:
            recommendations.append("Positive sentiment detected - consider investment opportunities")
    
    # Recency recommendations
    recent_articles = [a for a in articles if a.get('age_hours', 24) < 2]
    if recent_articles:
        recommendations.append(f"{len(recent_articles)} breaking news articles - stay updated")
    
    return recommendations

def _filter_articles_by_timeframe_and_category(articles: List[dict], timeframe: str, category: str) -> List[dict]:
    """Filter articles by timeframe and category"""
    # Timeframe filtering
    if timeframe == '24h':
        max_age = 24
    elif timeframe == '1w':
        max_age = 168  # 7 days * 24 hours
    elif timeframe == '1m':
        max_age = 720  # 30 days * 24 hours
    else:
        max_age = 24
    
    filtered = [a for a in articles if a.get('age_hours', 0) <= max_age]
    
    # Category filtering
    if category != 'all':
        filtered = [a for a in filtered if category in a.get('market_categories', [])]
    
    return filtered

def _generate_intelligent_news_summary(articles: List[dict]) -> dict:
    """Generate AI-powered news summary"""
    if not articles:
        return {
            'headline': 'No news available',
            'key_points': [],
            'market_outlook': 'Neutral'
        }
    
    # Count categories and themes
    from collections import Counter
    all_categories = []
    for article in articles:
        all_categories.extend(article.get('market_categories', []))
    
    category_counts = Counter(all_categories)
    top_categories = category_counts.most_common(3)
    
    # Generate summary points
    key_points = []
    for category, count in top_categories:
        key_points.append(f"{count} articles about {category}")
    
    # Calculate overall impact
    avg_impact = sum(a.get('market_impact_score', 0) for a in articles) / len(articles)
    
    # Generate headline
    if avg_impact > 0.6:
        headline = "High-impact market news detected"
    elif avg_impact > 0.3:
        headline = "Moderate market activity observed"
    else:
        headline = "Quiet market news period"
    
    # Market outlook
    if avg_impact > 0.5:
        market_outlook = "Active"
    elif avg_impact > 0.3:
        market_outlook = "Moderate"
    else:
        market_outlook = "Calm"
    
    return {
        'headline': headline,
        'key_points': key_points,
        'market_outlook': market_outlook,
        'total_articles': len(articles),
        'average_impact': round(avg_impact, 3),
        'top_categories': [{'category': cat, 'count': count} for cat, count in top_categories]
    }
