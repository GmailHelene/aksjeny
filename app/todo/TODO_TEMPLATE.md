# Aksjeradar TODO Template & File Structure

## 1. Main TODO and Progress Files
- `/workspaces/aksjeradarny/PRIORITIZED_TODO_LIST.md` - The main prioritized list of completed and outstanding issues
- `/workspaces/aksjeradarny/TODO.md` - General TODOs and developer notes
- `/workspaces/aksjeradarny/TODO_TRACKER.md` - Tracker for critical, medium, and completed tasks

## 2. Analysis Pages & Navigation
- `/workspaces/aksjeradarny/app/routes/analysis.py` - All analysis-related endpoints, error handling, and navigation logic
- `/workspaces/aksjeradarny/app/templates/analysis/graham.html` - Graham analysis template
- `/workspaces/aksjeradarny/app/templates/analysis/buffett.html` - Warren Buffett analysis template
- `/workspaces/aksjeradarny/app/templates/analysis/short.html` - Short analysis template
- `/workspaces/aksjeradarny/app/templates/analysis/_menu.html` - Analysis menu/navigation
- `/workspaces/aksjeradarny/app/templates/base.html` - Main navigation bar
- `/workspaces/aksjeradarny/app/services/ai_service.py` - AI logic for analysis

## 3. Data Display, Error Handling, and Translations
- `/workspaces/aksjeradarny/app/templates/analysis/*.html` - All analysis templates
- `/workspaces/aksjeradarny/app/templates/analysis/market_overview.html` - Market analysis
- `/workspaces/aksjeradarny/app/templates/analysis/technical.html` - Technical analysis

## 4. Portfolio Management
- `/workspaces/aksjeradarny/app/routes/portfolio.py` - Portfolio value calculations, transactions
- `/workspaces/aksjeradarny/app/templates/portfolio/*.html` - Portfolio templates

## 5. Real-time Data Integration
- `/workspaces/aksjeradarny/app/services/data_service.py` - Yahoo Finance API integration
- `/workspaces/aksjeradarny/app/services/ai_service.py` - Real-time data logic

## 6. User Experience & Loading States
- `/workspaces/aksjeradarny/app/templates/analysis/*.html` - Skeleton loaders, error boundaries
- `/workspaces/aksjeradarny/app/static/` - JS/CSS for loaders

## 7. Mobile Optimization
- `/workspaces/aksjeradarny/app/templates/analysis/_menu.html` - Mobile navigation
- `/workspaces/aksjeradarny/app/templates/analysis/*.html` - Responsive design

## 8. Access Control & Routing
- `/workspaces/aksjeradarny/app/utils/access_control.py` - Route protection logic
- `/workspaces/aksjeradarny/app/routes/stocks.py` - Stock endpoints

## 9. Subscription Flow
- `/workspaces/aksjeradarny/app/routes/subscription.py` - Subscription logic
- `/workspaces/aksjeradarny/app/templates/subscription/` - Subscription templates

## 10. Contrast, Accessibility, and Text Issues
- `/workspaces/aksjeradarny/app/templates/subscription/hero.html` - Hero section
- `/workspaces/aksjeradarny/app/templates/auth/register.html` - Registration
- `/workspaces/aksjeradarny/app/templates/auth/login.html` - Login

## 11. Data Quality & Performance
- `/workspaces/aksjeradarny/app/services/data_service.py` - Data validation
- `/workspaces/aksjeradarny/app/services/analysis_service.py` - Calculation optimization

## 12. Automated and Manual Test Files
- `/workspaces/aksjeradarny/styling_fixes_test.py`
- `/workspaces/aksjeradarny/comprehensive_critical_issues_test.py`
- `/workspaces/aksjeradarny/fix_verification_test.py`
- `/workspaces/aksjeradarny/complete_system_test.py`
- `/workspaces/aksjeradarny/comprehensive_test_suite.py`

## 13. JS Error Fixes and Real-time Service
- `/workspaces/aksjeradarny/app/static/js/enhanced-realtime.js`
- `/workspaces/aksjeradarny/app/static/js/realtime-data.js`
- `/workspaces/aksjeradarny/app/static/js/pwa-install.js`
- `/workspaces/aksjeradarny/app/static/js/onboarding-system.js`
- `/workspaces/aksjeradarny/app/static/js/watchlist-fix.js`
- `/workspaces/aksjeradarny/app/static/js/navigation-fix.js`
- `/workspaces/aksjeradarny/app/static/js/trial-timer.js`
- `/workspaces/aksjeradarny/app/routes/api.py` - API endpoints

## Usage:
To address specific issues, search for keywords in these files. To verify fixes, check the relevant function, template block, or test case in these locations.