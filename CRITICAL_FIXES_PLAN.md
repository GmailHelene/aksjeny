# Critical Fixes Plan for Aksjeradar

## PRIORITY 1 - CRITICAL NAVIGATION & ROUTING ISSUES

### ✅ COMPLETED
1. Fixed sentiment.html template structure and duplicated content
2. Fixed analysis.py import error (added demo_access import)
3. Enhanced navigation with proper dropdown menus instead of # links

### 🚧 IN PROGRESS 
4. Fix homepage for premium users (remove pricing section, add market data tables)
5. Fix mobile navigation padding issues
6. Create missing critical templates

## PRIORITY 2 - MISSING TEMPLATES

### Analysis Templates (CRITICAL)
- [x] sentiment.html (FIXED)
- [ ] fundamental.html (needs completion)
- [ ] ai_form.html (needs creation)
- [ ] ai.html (needs creation)
- [ ] technical.html (needs proper stock selection)
- [ ] advanced.html (needs creation)
- [ ] warren-buffet.html vs warren_buffett.html (consolidate)
- [ ] benjamin-graham.html (needs creation)

### Portfolio Templates
- [x] view.html (FIXED)
- [ ] create.html (needs creation)
- [ ] transactions.html (needs creation)
- [ ] tips.html (needs creation)
- [ ] watchlist.html (needs creation)
- [ ] advanced.html (needs creation)

### Market Templates
- [ ] market/overview.html (needs creation)
- [ ] market_intel/insider_trading.html (needs creation)

### Features Templates
- [ ] features/ai_predictions.html (needs creation)
- [ ] features/market_news_sentiment.html (needs creation)
- [ ] features/analyst_recommendations.html (needs creation)
- [ ] features/notifications.html (needs creation)
- [ ] features/social_sentiment.html (needs creation)
- [ ] features/technical_analysis.html (needs creation)

### Pro Tools Templates
- [ ] pro/alerts.html (needs creation)
- [ ] pro/export.html (needs creation)
- [ ] pro/portfolio_analyzer.html (needs creation)
- [ ] pro/screener.html (needs creation)

### Resources Templates
- [ ] resources/analysis_tools.html (needs creation)
- [ ] resources/guides.html (needs creation)
- [ ] resources/tool_comparison.html (needs creation)

### SEO Templates
- [ ] seo/blog_index.html (needs creation)
- [ ] seo/blog_post.html (needs creation)
- [ ] seo/investment_guide.html (needs creation)
- [ ] seo/investment_guides.html (needs creation)

### Stocks Templates
- [ ] stocks/compare_form.html (needs creation)
- [ ] stocks/compare.html (needs creation)
- [ ] stocks/details.html vs detail.html (consolidate)

### External Data Templates
- [ ] external_data/comprehensive_analysis.html (needs creation)

## PRIORITY 3 - FUNCTIONAL FIXES

### Homepage Issues
- [ ] Remove premium user pricing section visibility
- [ ] Add market data tables for premium users (Oslo Børs, Global, Crypto, Currency)
- [ ] Move user welcome message to profile page

### Navigation Issues
- [x] Fix # links in main navigation (COMPLETED)
- [ ] Fix mobile navigation padding for logged-in users
- [ ] Fix overlay issues on analysis pages

### Route Issues
- [ ] Fix /analysis/ redirect loop (too many redirects)
- [ ] Fix /warren-buffett Method Not Allowed
- [ ] Fix /benjamin-graham reload without analysis
- [ ] Fix screener and sentiment strange characters issue
- [ ] Fix news article 404 errors

### Data Issues
- [ ] Fix portfolio loading errors
- [ ] Fix stock data loading for Oslo Børs
- [ ] Fix global stocks redirect issue
- [ ] Fix crypto "no stocks available" error
- [ ] Fix currency rates not showing
- [ ] Fix financial dashboard tab functionality

### Styling Issues
- [ ] Fix pricing banner "Mest populær" cropping
- [ ] Fix mobile menu padding for logged-in users
- [ ] Remove duplicate nav overlays on analysis pages

## PRIORITY 4 - CODE CLEANUP

### Duplicate Files
- [ ] Consolidate warren-buffet.html vs warren_buffett.html
- [ ] Consolidate benjamin_graham.html variants
- [ ] Remove unused duplicate templates
- [ ] Clean up unused route files

### Database Issues
- [ ] Fix profile page 500 error
- [ ] Fix portfolio data loading
- [ ] Fix stock data services

## IMPLEMENTATION STRATEGY

1. **Phase 1**: Fix critical navigation and routing (CURRENT)
2. **Phase 2**: Create missing essential templates
3. **Phase 3**: Fix functional issues and data loading
4. **Phase 4**: Code cleanup and optimization
5. **Phase 5**: Testing and validation

## NOTES
- This is a comprehensive refactoring that requires systematic approach
- Priority should be on user-facing critical functionality
- Testing after each phase is essential
- Some issues may be interconnected and require coordinated fixes
