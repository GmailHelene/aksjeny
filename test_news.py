#!/usr/bin/env python3
"""Test news service directly"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.services.news_service import get_latest_news_sync

def test_news():
    print("Testing news service...")
    try:
        articles = get_latest_news_sync(limit=5)
        print(f"Got {len(articles)} articles")
        for i, article in enumerate(articles[:3], 1):
            print(f"{i}. {article.title} - {article.source}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news()
