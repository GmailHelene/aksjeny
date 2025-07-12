#!/usr/bin/env python3
"""
Test script for enhanced news functionality
Tests the new comprehensive financial news sources and API endpoints
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.news_service import news_service, get_latest_news_sync
import requests
import json

def test_news_sources():
    """Test news source configuration"""
    print("🔍 Testing News Sources Configuration")
    print("=" * 50)
    
    norwegian_sources = []
    international_sources = []
    
    for source_id, config in news_service.news_sources.items():
        if config['category'] == 'norwegian':
            norwegian_sources.append(config['name'])
        else:
            international_sources.append(config['name'])
    
    print(f"📰 Norwegian Sources ({len(norwegian_sources)}):")
    for source in norwegian_sources:
        print(f"  • {source}")
    
    print(f"\n🌍 International Sources ({len(international_sources)}):")
    for source in international_sources:
        print(f"  • {source}")
    
    print(f"\n📊 Total Sources: {len(news_service.news_sources)}")
    
def test_sync_news_fetch():
    """Test synchronous news fetching"""
    print("\n🔄 Testing Synchronous News Fetch")
    print("=" * 50)
    
    try:
        # Test Norwegian news
        print("Fetching Norwegian news...")
        norwegian_news = get_latest_news_sync(limit=5, category='norwegian')
        print(f"✅ Retrieved {len(norwegian_news)} Norwegian articles")
        
        # Test International news
        print("Fetching international news...")
        international_news = get_latest_news_sync(limit=5, category='international')
        print(f"✅ Retrieved {len(international_news)} international articles")
        
        # Test company news
        print("Fetching Equinor news...")
        company_news = get_latest_news_sync(limit=3)
        print(f"✅ Retrieved {len(company_news)} general articles")
        
        if norwegian_news:
            print(f"\n📰 Sample Norwegian Article:")
            article = norwegian_news[0]
            print(f"  Title: {article.title[:80]}...")
            print(f"  Source: {article.source}")
            print(f"  Categories: {', '.join(article.categories) if article.categories else 'None'}")
            print(f"  Relevance: {article.relevance_score:.1f}")
        
        if international_news:
            print(f"\n🌍 Sample International Article:")
            article = international_news[0]
            print(f"  Title: {article.title[:80]}...")
            print(f"  Source: {article.source}")
            print(f"  Categories: {', '.join(article.categories) if article.categories else 'None'}")
            print(f"  Relevance: {article.relevance_score:.1f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_async_news_fetch():
    """Test asynchronous news fetching"""
    print("\n⚡ Testing Async News Fetch")
    print("=" * 50)
    
    try:
        # Test latest news
        print("Fetching latest news asynchronously...")
        latest_news = await news_service.get_latest_news(limit=10)
        print(f"✅ Retrieved {len(latest_news)} latest articles")
        
        # Test market summary
        print("Fetching market summary...")
        market_summary = await news_service.get_market_summary_news()
        
        total_articles = sum(len(articles) for articles in market_summary.values())
        print(f"✅ Retrieved {total_articles} categorized articles")
        
        for category, articles in market_summary.items():
            if articles:
                print(f"  {category}: {len(articles)} articles")
        
        # Test company news
        print("Fetching Equinor company news...")
        company_news = await news_service.get_company_news('EQNR.OL', limit=5)
        print(f"✅ Retrieved {len(company_news)} Equinor-related articles")
        
        if latest_news:
            print(f"\n📈 Top Article by Relevance:")
            article = max(latest_news, key=lambda x: x.relevance_score)
            print(f"  Title: {article.title}")
            print(f"  Source: {article.source}")
            print(f"  Relevance: {article.relevance_score:.1f}")
            print(f"  Published: {article.published}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_keyword_categorization():
    """Test keyword-based categorization"""
    print("\n🏷️  Testing Keyword Categorization")
    print("=" * 50)
    
    test_articles = [
        ("Equinor rapporterer sterke resultater for tredje kvartal", "Equinor oil results"),
        ("Oslo Børs stiger på sterke olje- og gasspriser", "Oslo stock exchange up"),
        ("DNB Bank lanserer ny digital tjeneste", "DNB banking digital service"),
        ("Bitcoin når nye høyder i markedet", "Bitcoin cryptocurrency reaches high"),
        ("Telenor investerer i 5G-teknologi", "Telenor 5G technology investment"),
        ("Norsk Hydro øker aluminiumsproduksjon", "Norsk Hydro aluminum production increase")
    ]
    
    for title, summary in test_articles:
        relevance = news_service._calculate_relevance(title, summary)
        categories = news_service._categorize_article(title, summary)
        
        print(f"📝 Article: {title[:50]}...")
        print(f"   Relevance: {relevance:.1f}")
        print(f"   Categories: {', '.join(categories)}")
        print()

def test_api_endpoints():
    """Test API endpoints if running locally"""
    print("\n🌐 Testing API Endpoints (if server is running)")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    endpoints = [
        "/news/api/latest?limit=5",
        "/news/api/market-summary",
        "/news/api/trending?limit=5",
        "/news/api/sources"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: {response.status_code} - Success")
                if 'articles' in data:
                    print(f"   Articles: {len(data['articles'])}")
                elif 'sources' in data:
                    print(f"   Sources: {len(data['sources'])}")
            else:
                print(f"⚠️  {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"🔌 {endpoint}: Server not running or not accessible")

def main():
    """Run all tests"""
    print("🚀 Enhanced News System Test Suite")
    print("=" * 60)
    
    # Test configuration
    test_news_sources()
    
    # Test synchronous functionality
    test_sync_news_fetch()
    
    # Test asynchronous functionality
    print("\nRunning async tests...")
    asyncio.run(test_async_news_fetch())
    
    # Test categorization
    test_keyword_categorization()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n✨ Test Suite Complete!")
    print("=" * 60)
    print("Enhanced news system ready with:")
    print("• Multiple Norwegian and international sources")
    print("• Advanced relevance scoring")
    print("• Comprehensive categorization")
    print("• Async/sync compatibility")
    print("• RESTful API endpoints")

if __name__ == "__main__":
    main()
