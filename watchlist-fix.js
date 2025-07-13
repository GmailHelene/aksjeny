/**
 * Watchlist State Management to prevent reload loops
 */

class WatchlistStateManager {
    constructor() {
        this.isLoading = false;
        this.lastUpdateTime = 0;
        this.updateCooldown = 5000; // 5 seconds between updates
        this.navigationInProgress = false;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Prevent multiple rapid reloads
        window.addEventListener('beforeunload', () => {
            this.navigationInProgress = true;
        });

        // Handle page visibility changes to prevent unnecessary reloads
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoRefresh();
            } else {
                this.resumeAutoRefresh();
            }
        });

        // Override any existing watchlist refresh functions
        this.overrideRefreshFunctions();
    }

    overrideRefreshFunctions() {
        // Safely wrap reload function
        const originalReload = window.location.reload.bind(window.location);
        window.safeReload = (...args) => {
            if (this.shouldAllowReload()) {
                console.log('WatchlistStateManager: Allowing page reload');
                originalReload(...args);
            } else {
                console.log('WatchlistStateManager: Preventing unnecessary reload');
            }
        };

        // Ensure setTimeout-based refresh loops are safely overridden
        const originalSetTimeout = window.setTimeout;
        window.setTimeout = (callback, delay, ...args) => {
            const callbackStr = callback.toString();
            if ((callbackStr.includes('reload') || callbackStr.includes('location.href')) && 
                !this.shouldAllowReload()) {
                console.log('Preventing reload in setTimeout');
            } else {
                originalSetTimeout(callback, delay, ...args);
            }
        };

        // Intercept location.href changes
        let locationHref = window.location.href;
        Object.defineProperty(window, 'location', {
            get: function() {
                return new Proxy(window.location, {
                    set: (target, property, value) => {
                        if (property === 'href' && value === locationHref) {
                            // Prevent reload to same URL
                            console.log('WatchlistStateManager: Preventing reload to same URL');
                            return true;
                        }
                        target[property] = value;
                        return true;
                    }
                });
            },
            configurable: true
        });
    }

    shouldAllowReload() {
        const now = Date.now();
        
        // Don't allow reload if we're already loading
        if (this.isLoading) {
            return false;
        }

        // Don't allow reload if we're navigating
        if (this.navigationInProgress) {
            return false;
        }

        // Check cooldown period
        if (now - this.lastUpdateTime < this.updateCooldown) {
            return false;
        }

        this.lastUpdateTime = now;
        return true;
    }

    pauseAutoRefresh() {
        this.isLoading = true;
        console.log('WatchlistStateManager: Auto-refresh paused');
    }

    resumeAutoRefresh() {
        // Wait a bit before resuming to prevent immediate reload
        setTimeout(() => {
            this.isLoading = false;
            console.log('WatchlistStateManager: Auto-refresh resumed');
        }, 2000);
    }

    // Provide safe methods for watchlist updates
    async safeUpdateWatchlist(watchlistId) {
        if (!this.shouldAllowReload()) {
            console.log('WatchlistStateManager: Update blocked by cooldown');
            return false;
        }

        this.isLoading = true;

        try {
            // Use AJAX instead of page reload
            const response = await fetch(`/watchlist/api/refresh/${watchlistId}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateWatchlistDOM(data);
                return true;
            } else {
                throw new Error('Failed to update watchlist');
            }
        } catch (error) {
            console.error('WatchlistStateManager: Update failed:', error);
            return false;
        } finally {
            this.isLoading = false;
        }
    }

    updateWatchlistDOM(data) {
        // Update specific parts of the watchlist without full page reload
        const watchlistContainer = document.querySelector('[data-watchlist-content]');
        if (watchlistContainer && data.html) {
            watchlistContainer.innerHTML = data.html;
        }

        // Update any price displays
        if (data.prices) {
            Object.keys(data.prices).forEach(symbol => {
                const priceElements = document.querySelectorAll(`[data-symbol="${symbol}"] .price`);
                priceElements.forEach(element => {
                    element.textContent = data.prices[symbol];
                });
            });
        }
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
}

// Initialize the state manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.watchlistStateManager = new WatchlistStateManager();
    console.log('WatchlistStateManager: Initialized');
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WatchlistStateManager;
}
