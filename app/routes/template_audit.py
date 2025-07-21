# Step 1: Audit existing templates

# Check for duplicates and inconsistencies in template names

# Step 2: Identify missing templates

# List of templates to check

analysis_templates = [
    'Advanced.html',
    'fundamental.html',
    'ai_form.html',
    'ai_html.html',
    'analysis_nav.html',
    'buffet_select.html',
    'currency_overview.html',
    'insider_trading.html',
    'recommendation_select.html',
    'recommendation.html',
    'screener.html',
    'sentiment.html',
    'short_select.html',
    'short-analysis.html',
    'short.html',
    'technical_html.html',
    'warren_buffet.html',
    'warren-buffet.html'
]

external_data_templates = [
    'comprehensive_analysis.html'
]

features_templates = [
    'ai_predictions.html',
    'market_news_sentiment.html',
    'analyst_recommendations.html',
    'Notifications.html',
    'social_sentiment.html',
    'technical_analysis.html'
]

market_templates = [
    'overview.html'
]

market_intel_templates = [
    'insider_trading.html'
]

portfolio_templates = [
    'Advanced.html',
    'create.html',
    'tips.html',
    'transactions.html',
    'view.html',
    'watchlist.html'
]

pro_templates = [
    'alerts.html',
    'export.html',
    'portfolio_analyzer.html',
    'screener.html'
]

resources_templates = [
    'analysis_tools.html',
    'guides.html',
    'tool_comparison.html'
]

stocks_templates = [
    'compare_form.html',
    'compare.html',
    'details.html',
    'detail.html'
]

seo_templates = [
    'blog_index.html',
    'blog_post.html',
    'investment_guide.html',
    'investment_guides.html'
]

# Step 3: Check for duplicates and inconsistencies

# Create a function to check for duplicates

def check_duplicates(templates):
    return set([t for t in templates if templates.count(t) > 1])

# Check each template category for duplicates

analysis_duplicates = check_duplicates(analysis_templates)
external_data_duplicates = check_duplicates(external_data_templates)
features_duplicates = check_duplicates(features_templates)
market_duplicates = check_duplicates(market_templates)
market_intel_duplicates = check_duplicates(market_intel_templates)
portfolio_duplicates = check_duplicates(portfolio_templates)
pro_duplicates = check_duplicates(pro_templates)
resources_duplicates = check_duplicates(resources_templates)
stocks_duplicates = check_duplicates(stocks_templates)
seo_duplicates = check_duplicates(seo_templates)

# Step 4: Log the results

logger.info(f"Analysis duplicates: {analysis_duplicates}")
logger.info(f"External Data duplicates: {external_data_duplicates}")
logger.info(f"Features duplicates: {features_duplicates}")
logger.info(f"Market duplicates: {market_duplicates}")
logger.info(f"Market Intel duplicates: {market_intel_duplicates}")
logger.info(f"Portfolio duplicates: {portfolio_duplicates}")
logger.info(f"Pro duplicates: {pro_duplicates}")
logger.info(f"Resources duplicates: {resources_duplicates}")
logger.info(f"Stocks duplicates: {stocks_duplicates}")
logger.info(f"SEO duplicates: {seo_duplicates}")

# Step 5: Clean up templates based on findings

# This will involve renaming, removing, or consolidating templates as necessary.
