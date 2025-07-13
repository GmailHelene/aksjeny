## Test Plan for URL/Endpoint and Language Issues

### Objective
To ensure all URLs and API endpoints in the Aksjeradar application function correctly, display content in Norwegian as expected, and handle various user states (authenticated, unauthenticated, trial, subscribed) without errors or missing information.

### Scope
All routes identified in `route_analysis.md` from `main.py`, `admin.py`, `analysis.py`, and `api.py`.

### Testing Strategy

1.  **Automated Endpoint Testing (Python/Flask Test Client):**
    *   Develop Python scripts using Flask's `test_client` to simulate HTTP requests to all identified GET and POST endpoints.
    *   Verify HTTP status codes (200 OK, 302 Redirect, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error) are as expected.
    *   Check response content for expected data, especially for API endpoints (JSON structure and data validity).
    *   Test authentication and authorization for `login_required` and `access_required` routes.
    *   Simulate different user states (unauthenticated, authenticated, trial active, trial expired, subscribed) to verify access control.

2.  **Language and Content Verification (Manual/Automated where possible):**
    *   For all user-facing pages, verify that text content is in Norwegian and grammatically correct.
    *   Ensure no placeholder text like 'N/A' or 'null' is displayed where actual data should be.
    *   Check for missing images, broken links, or incorrect data display.
    *   Specifically test routes that handle dynamic content or data fetching (`/`, `/analysis/technical`, `/stocks/details/<ticker>`, API endpoints) to ensure data is populated correctly.

3.  **Redirect Logic Testing:**
    *   Verify all explicit redirects (`redirect(url_for(...))`) lead to the correct destination.
    *   Test implicit redirects or access control redirects (e.g., `access_required` decorator) for unauthenticated or unauthorized users.
    *   Focus on the `/demo` page and its interaction with trial status.

### Test Cases (Examples - will be expanded during implementation)

#### General
*   Access `/` as unauthenticated user: Should redirect to `/demo` if trial expired/not started, or show main page if trial active.
*   Access `/` as authenticated user (no subscription, trial active): Should show main page.
*   Access `/` as authenticated user (no subscription, trial expired): Should redirect to `/demo`.
*   Access `/` as authenticated user (subscribed): Should show main page.

#### Authentication & Authorization
*   Attempt to access `/admin` as non-admin user: Should redirect to `main.index` with error flash.
*   Attempt to access `/profile` as unauthenticated user: Should redirect to `main.login`.
*   Successful login: Verify redirect to `main.index` and session/cookie state.
*   Successful logout: Verify redirect to `main.index` and session/cookie cleared.

#### Data Endpoints
*   `GET /api/oslo_stocks`: Verify JSON response contains expected stock data and is not empty.
*   `GET /api/realtime/price/<ticker>`: Test with valid and invalid tickers. Verify price, change, volume, etc., are present and correctly formatted.
*   `POST /api/watchlist/add`: Test with authenticated and unauthenticated users. Verify successful addition and error handling.

#### Language & Content
*   Navigate to `/pricing`: Verify all pricing details are in Norwegian and correctly formatted.
*   Navigate to `/stocks/details/EQNR.OL`: Verify stock details are displayed, no N/A values, and all text is Norwegian.

### Tools
*   Python `unittest` or `pytest` for automated testing.
*   Flask `test_client` for simulating requests.
*   Manual browser testing for visual and interactive elements.
*   `curl` or `Postman` for quick API endpoint checks.

### Reporting
*   Log all test results, including passed/failed status and any errors.
*   Document steps to reproduce any identified bugs.
*   Provide screenshots for visual issues.



### Testing New Features and Future Improvements

Many routes and code comments indicate features that are either new, in development, or have been recently refactored. This section outlines the testing approach for these.

#### Access Control and Trial Management
*   **Objective:** Verify the `@access_required` decorator and the new trial management system (`_check_trial_access`, `_get_device_fingerprint`) function correctly for all user states (unauthenticated, authenticated, trial active, trial expired, subscribed, exempt).
*   **Test Cases:**
    *   Access a protected route (`/stocks/details/AAPL`) as an unauthenticated user: Should redirect to `/demo` if no trial or trial expired. Should allow access if trial is active.
    *   Access a protected route as an authenticated user with active subscription: Should allow access.
    *   Access a protected route as an authenticated user with expired trial and no subscription: Should redirect to `/demo`.
    *   Access a protected route as an exempt user: Should always allow access.
    *   Verify that `/demo` page does NOT start a new trial.
    *   Test `_update_trial_cookie` functionality.
    *   Test `_handle_no_access` for both AJAX and non-AJAX requests.

#### Referral System
*   **Objective:** Verify the referral system (`/referrals`, `/send-referral`, `/api/user/referral-code`, `/profile`, `/invite-friend`) functions correctly, including code generation, sending invitations, and tracking referrals/discounts.
*   **Test Cases:**
    *   Generate a referral code for a new user.
    *   Send a referral invitation via email (mock email sending if actual sending is not possible).
    *   Register a new user using a referral code and verify the referral is tracked.
    *   Verify referral discounts are applied correctly during subscription checkout.
    *   Check referral statistics on the `/referrals` and `/profile` pages.

#### Stripe Integration
*   **Objective:** Verify the Stripe integration for subscriptions (`/subscription`, `/create-checkout-session`, `/subscribe/<plan>`, `/payment/success`, `/payment/cancel`, `/webhook/stripe`) works end-to-end.
*   **Test Cases:**
    *   Navigate to `/subscription` and verify plans are displayed correctly (both real and fallback).
    *   Initiate a checkout session for different plans (monthly, yearly, lifetime).
    *   Simulate successful and cancelled payments and verify user subscription status updates.
    *   Test the Stripe webhook handler (`/webhook/stripe`) for `checkout.session.completed`, `customer.subscription.updated`, and `customer.subscription.deleted` events.
    *   Verify `handle_successful_subscription`, `handle_subscription_update`, and `handle_subscription_deleted` functions correctly update user data.

#### PWA and Offline Support
*   **Objective:** Verify PWA features (`/service-worker.js`, `/manifest.json`, `/offline`, `/offline.html`, `/pwa-test`) are correctly implemented.
*   **Test Cases:**
    *   Verify `service-worker.js` and `manifest.json` are served correctly.
    *   Test offline page access.
    *   Check PWA installation prompts (manual browser check).

#### Debug Routes (for development/testing only)
*   **Objective:** Verify debug routes provide correct information and perform intended actions (e.g., session reset, user info display).
*   **Test Cases:**
    *   Access `/debug/reset-session` and verify session/cookies are cleared.
    *   Access `/debug/status` and `/debug/user-info` and verify accurate debug information is displayed.
    *   Test `/admin/create-exempt-users` and `/admin/reset-user/<int:user_id>` (with caution).
    *   Test `/test-email` (mock email sending).

#### Language Switching
*   **Objective:** Verify language switching functionality (`/language/<lang_code>`, `/set-language/<language>`, `/api/language/switch`) works as expected.
*   **Test Cases:**
    *   Switch language via UI elements (if available) and verify content changes.
    *   Test API endpoint for language switching.
    *   Verify language preference persists for authenticated users.

#### General Content and Display
*   **Objective:** Ensure all user-facing content is in Norwegian, grammatically correct, and free of placeholders (N/A, null, etc.).
*   **Test Cases:**
    *   Review all `.html` templates for hardcoded English text or placeholders.
    *   Verify dynamic data (stock prices, analysis results) is displayed correctly and in Norwegian where applicable.
    *   Check all flash messages for correct Norwegian translation and context.

This expanded test plan will guide the testing process in Phase 3 and 4.

