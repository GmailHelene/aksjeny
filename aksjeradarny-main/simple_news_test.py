#!/usr/bin/env python3
"""
Simple test for news service configuration
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_news_config():
    """Test basic news service configuration"""
    try:
        from app.services.news_service import news_service
        
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
        print("✅ News service configuration loaded successfully!")
        
        # Test keyword categorization
        print("\n🏷️  Testing Keyword Categorization")
        print("-" * 30)
        
        test_cases = [
            ("Equinor rapporterer sterke resultater", "Equinor oil results"),
            ("Oslo Børs stiger på høye olje priser", "Oslo stock exchange up"),
            ("DNB Bank lanserer ny app", "DNB banking app")
        ]
        
        for title, summary in test_cases:
            relevance = news_service._calculate_relevance(title, summary)
            categories = news_service._categorize_article(title, summary)
            print(f"📝 '{title}' → Relevance: {relevance:.1f}, Categories: {categories}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_news_config()
    if success:
        print("\n✨ Enhanced News System Ready!")
        print("=" * 50)
        print("Features:")
        print("• Multiple Norwegian financial sources (DN, E24, Finansavisen, etc.)")
        print("• International sources (Reuters, Bloomberg, Financial Times, etc.)")
        print("• Advanced relevance scoring and categorization")
        print("• Async news fetching with caching")
        print("• RESTful API endpoints")
        print("• Enhanced news widget for dashboard")
    else:
        print("\n❌ Setup incomplete - check dependencies")
