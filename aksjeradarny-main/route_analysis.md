## Route Analysis

### `main.py`

*   `/` (GET): Landing page.
*   `/demo` (GET): Demo page for non-registered users.
*   `/ai-explained` (GET): AI explanation page.
*   `/pricing` (GET): Pricing page.
*   `/pricing/` (GET): Pricing page (duplicate of `/pricing`).
*   `/search` (GET): Search results page.
*   `/login` (GET, POST): User login.
*   `/logout` (GET): User logout.
*   `/register` (GET, POST): User registration.
*   `/share-target` (GET): Handles content shared to the app.
*   `/service-worker.js` (GET): Serves the service worker.
*   `/manifest.json` (GET): Serves the manifest.json file.
*   `/version` (GET): Returns the application version.
*   `/privacy` (GET): Displays the privacy policy.
*   `/privacy-policy` (GET): Returns a static privacy policy HTML file.
*   `/subscription` (GET): Shows subscription options.
*   `/start-trial` (POST): Starts a free trial for the current user.
*   `/purchase_subscription` (POST): Handles subscription purchase (dummy implementation).
*   `/create-checkout-session` (POST): Creates a Stripe checkout session.
*   `/subscribe/<plan>` (GET): Subscribes a user to a plan.
*   `/payment/success` (GET): Payment success page.
*   `/payment/cancel` (GET): Payment cancellation page.
*   `/webhook/stripe` (POST): Handles Stripe webhook events.
*   `/trial-expired` (GET): Trial expired page.
*   `/contact` (GET): Contact page.
*   `/contact/submit` (POST): Handles contact form submission.
*   `/api/search` (GET): API endpoint for stock search.
*   `/api/oslo_stocks` (GET): API endpoint for Oslo Børs overview.
*   `/api/global_stocks` (GET): API endpoint for global stocks overview.
*   `/api/realtime/price/<ticker>` (GET): API endpoint for real-time stock price data.
*   `/api/realtime/batch-updates` (POST): Handles batch real-time updates for multiple tickers.
*   `/offline` (GET): Offline page.
*   `/currency` (GET): Currency rates page.
*   `/api/watchlist/add` (POST): Adds a stock to the user's watchlist.
*   `/api/portfolio/add` (POST): Adds a stock to the user's portfolio.
*   `/offline.html` (GET): Serves the offline HTML page.
*   `/favicon.ico` (GET): Serves the favicon.
*   `/restricted_access.html` (GET): Legacy restricted access route.
*   `/restricted_access` (GET): Legacy restricted access route.
*   `/prediction` (GET): Redirects to the analysis prediction page.
*   `/forgot_password` (GET, POST): Forgot password page.
*   `/reset_password/<token>` (GET, POST): Resets the user's password.
*   `/pwa-test` (GET): PWA functionality test page.
*   `/admin/create-exempt-users` (GET): Admin route to create exempt users.
*   `/debug/reset-session` (GET): Resets the session and cookies for debugging.
*   `/debug/status` (GET): Displays debug information.
*   `/test-email` (GET): Tests email functionality.
*   `/admin/user-management` (GET): Admin page for user management.
*   `/admin/reset-user/<int:user_id>` (GET): Resets a user's trial and subscription status.
*   `/check-trial` (GET): Debug route to check trial status.
*   `/admin/clean-trials` (GET): Cleans up expired trial sessions.
*   `/debug/user-info` (GET): Debug route to check user and trial status.
*   `/referrals` (GET): Referral dashboard.
*   `/send-referral` (POST): Sends a referral invitation.
*   `/api/user/referral-code` (GET): API endpoint to get the user's referral code.
*   `/debug/test-reset` (GET): Debug endpoint to test password reset functionality.
*   `/profile` (GET): User profile page.
*   `/invite-friend` (POST): Sends an invitation email to a friend.
*   `/debug/csrf` (GET, POST): Debug endpoint to test CSRF tokens.
*   `/demo/ping` (GET): Simple ping route for health checks.
*   `/demo/echo` (GET, POST): Echoes back posted data for testing.
*   `/demo/user` (GET): Returns current user info for demo purposes.
*   `/auth` (GET): Combined login and registration page.
*   `/language/<lang_code>` (GET): Sets the user's language preference.
*   `/set-language/<language>` (GET): Sets the application language.
*   `/api/language/switch` (POST): API endpoint for switching language.
*   `/stocks/details/<ticker>` (GET): Displays details for a specific stock.
*   `/analysis/market-overview` (GET): Displays the market overview.
*   `/api/feedback` (POST): Receives user feedback.

### `admin.py`

*   `/admin` (GET): Admin dashboard.
*   `/admin/performance` (GET): Displays performance statistics.
*   `/admin/api/performance` (GET): API for performance statistics.
*   `/admin/api/errors` (GET): API for error log.
*   `/admin/users` (GET): User management page.
*   `/admin/system` (GET): System status page.

### `analysis.py`

*   `/analysis/` (GET): Analysis landing page.
*   `/analysis/technical` (GET): Technical analysis view.
*   `/analysis/technical/<path:ticker>` (GET): Technical analysis for a specific ticker.
*   `/analysis/prediction` (GET, POST): Price predictions for multiple stocks.
*   `/analysis/recommendation` (GET): Stock recommendation.
*   `/analysis/ai` (GET, POST): AI analysis view.
*   `/analysis/api/analysis/indicators` (GET): Technical indicators for a stock.
*   `/analysis/api/analysis/signals` (GET): Trading signals for a stock.
*   `/analysis/api/market-summary` (GET): AI-generated market summary.
*   `/analysis/downloads/<path:filename>` (GET): Download exported files.
*   `/analysis/market-overview` (GET): Market overview with analysis data.
*   `/analysis/warren-buffett` (GET, POST): Warren Buffett analysis.
*   `/analysis/benjamin-graham` (GET, POST): Benjamin Graham analysis.
*   `/analysis/short-analysis` (GET, POST): Short analysis.
*   `/analysis/fundamental` (GET): Fundamental analysis page.
*   `/analysis/sentiment` (GET): Sentiment analysis page.
*   `/analysis/screener` (GET): Stock screener page.

### `api.py`

*   `/api/crypto` (GET): API endpoint for crypto overview.
*   `/api/currency` (GET): API endpoint for currency overview.
*   `/api/health` (GET): Health check endpoint.
*   `/api/search` (GET): Search for stocks.
*   `/api/stocks/search` (GET): API endpoint for stock search.
*   `/api/stock/<symbol>` (GET): Get stock data for a specific symbol.
*   `/api/stock/<symbol>/price` (GET): Get current price for a stock.
*   `/api/stock/<symbol>/analysis` (GET): Get AI analysis for a stock.
*   `/api/market/overview` (GET): Get market overview data.
*   `/api/market-data` (GET): API endpoint for market data.
*   `/api/user/watchlist` (GET): Get user's watchlist.
*   `/api/user/portfolio` (GET): Get user's portfolio.
*   `/api/feedback` (POST): Receives user feedback.
*   `/api/realtime/price/<ticker>` (GET): Get real-time price for a ticker.
*   `/api/realtime/batch-updates` (POST): Get batch updates for multiple tickers.


