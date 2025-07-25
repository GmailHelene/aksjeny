# Aksjeradar Health Check Report

## Overview

Health check performed on: 2025-07-13 01:51:34

- **Issues found:** 85
- **Fixes applied:** 26

## Issues



- Blueprint api is not imported in app.py
- Blueprint api might not be registered in app.py
- Blueprint seo_content is not imported in app.py
- Blueprint seo_content might not be registered in app.py
- Blueprint admin is not imported in app.py
- Blueprint admin might not be registered in app.py
- Blueprint stocks is not imported in app.py
- Blueprint stocks might not be registered in app.py
- Blueprint analysis is not imported in app.py
- Blueprint analysis might not be registered in app.py
- Blueprint portfolio_advanced is not imported in app.py
- Blueprint portfolio_advanced might not be registered in app.py
- Blueprint external_data is not imported in app.py
- Blueprint external_data might not be registered in app.py
- Blueprint investment_guides is not imported in app.py
- Blueprint investment_guides might not be registered in app.py
- Blueprint pricing is not imported in app.py
- Blueprint pricing might not be registered in app.py
- Blueprint websocket is not imported in app.py
- Blueprint websocket might not be registered in app.py
- Blueprint market_intel is not imported in app.py
- Blueprint market_intel might not be registered in app.py
- Blueprint portfolio is not imported in app.py
- Blueprint portfolio might not be registered in app.py
- Blueprint resources is not imported in app.py
- Blueprint resources might not be registered in app.py
- Blueprint search_results is not imported in app.py
- Blueprint search_results might not be registered in app.py
- Blueprint features is not imported in app.py
- Blueprint features might not be registered in app.py
- Blueprint notifications is not imported in app.py
- Blueprint notifications might not be registered in app.py
- Blueprint search is not imported in app.py
- Blueprint search might not be registered in app.py
- Blueprint additional is not imported in app.py
- Blueprint additional might not be registered in app.py
- Blueprint social_sentiment is not imported in app.py
- Blueprint social_sentiment might not be registered in app.py
- Blueprint news is not imported in app.py
- Blueprint news might not be registered in app.py
- Blueprint blog is not imported in app.py
- Blueprint blog might not be registered in app.py
- Blueprint health is not imported in app.py
- Blueprint health might not be registered in app.py
- Blueprint market_data is not imported in app.py
- Blueprint market_data might not be registered in app.py
- Blueprint main is not imported in app.py
- Blueprint main might not be registered in app.py
- Blueprint backtest is not imported in app.py
- Blueprint backtest might not be registered in app.py
- Blueprint stripe_routes is not imported in app.py
- Blueprint stripe_routes might not be registered in app.py
- Blueprint realtime_api is not imported in app.py
- Blueprint realtime_api might not be registered in app.py
- Blueprint watchlist_advanced is not imported in app.py
- Blueprint watchlist_advanced might not be registered in app.py
- Template missing CSRF protection: templates/portfolio.html
- Template missing CSRF protection: templates/profile.html
- Template missing CSRF protection: templates/stocks/compare_form.html
- Template missing CSRF protection: templates/stocks/compare.html
- Template missing CSRF protection: templates/stocks/search.html
- Template missing CSRF protection: templates/stocks/index.html
- Template missing CSRF protection: templates/search/search.html
- Template missing CSRF protection: templates/features/social_sentiment.html
- Template missing CSRF protection: templates/features/analyst_recommendations.html
- Template missing CSRF protection: templates/features/ai_predictions.html
- Template missing CSRF protection: templates/market_intel/insider_trading.html
- Template missing CSRF protection: templates/backtest/index.html
- Template missing CSRF protection: templates/seo/blog_post.html
- Template missing CSRF protection: templates/seo/blog_index.html
- Template missing CSRF protection: templates/portfolio/view.html
- Template missing CSRF protection: templates/portfolio/advanced.html
- Template missing CSRF protection: templates/watchlist/index.html
- Template missing CSRF protection: templates/notifications/settings.html
- Template missing CSRF protection: templates/analysis/short_select.html
- Template missing CSRF protection: templates/analysis/short.html
- Template missing CSRF protection: templates/analysis/graham_select.html
- Template missing CSRF protection: templates/analysis/ai.html
- Template missing CSRF protection: templates/analysis/ai_form.html
- Template missing CSRF protection: templates/analysis/graham.html
- Template missing CSRF protection: templates/analysis/recommendation_select.html
- Database file not found at expected location: /workspaces/aksjeny/app.db
- Failed to initialize database: Traceback (most recent call last):
  File "/workspaces/aksjeny/init_db.py", line 2, in <module>
    from app import create_app
  File "/workspaces/aksjeny/app/__init__.py", line 2, in <module>
    from config import config
ModuleNotFoundError: No module named 'config'

- Missing dependency: email-validator
- Missing dependency: python-dotenv

## Fixes Applied



- Added CSRF token to templates/portfolio.html
- Added CSRF token to templates/profile.html
- Added CSRF token to templates/stocks/compare_form.html
- Added CSRF token to templates/stocks/compare.html
- Added CSRF token to templates/stocks/search.html
- Added CSRF token to templates/stocks/index.html
- Added CSRF token to templates/search/search.html
- Added CSRF token to templates/features/social_sentiment.html
- Added CSRF token to templates/features/analyst_recommendations.html
- Added CSRF token to templates/features/ai_predictions.html
- Added CSRF token to templates/market_intel/insider_trading.html
- Added CSRF token to templates/backtest/index.html
- Added CSRF token to templates/seo/blog_post.html
- Added CSRF token to templates/seo/blog_index.html
- Added CSRF token to templates/portfolio/view.html
- Added CSRF token to templates/portfolio/advanced.html
- Added CSRF token to templates/watchlist/index.html
- Added CSRF token to templates/notifications/settings.html
- Added CSRF token to templates/analysis/short_select.html
- Added CSRF token to templates/analysis/short.html
- Added CSRF token to templates/analysis/graham_select.html
- Added CSRF token to templates/analysis/ai.html
- Added CSRF token to templates/analysis/ai_form.html
- Added CSRF token to templates/analysis/graham.html
- Added CSRF token to templates/analysis/recommendation_select.html
- Installed missing packages: email-validator python-dotenv

## Next Steps

Some issues were found and fixed automatically. Manual review is recommended for the remaining issues.
