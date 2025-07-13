// Enhanced Navigation Handler for Aksjeradar
// Fixes hanging issues and improves back button handling

(function() {
    'use strict';
    
    // Configuration
    const CONFIG = {
        MAX_LOAD_TIME: 10000, // 10 seconds
        RETRY_DELAY: 1000,
        MAX_RETRIES: 3
    };
    
    // State management
    let navigationState = {
        isNavigating: false,
        currentPage: window.location.pathname,
        loadStartTime: null,
        abortController: null
    };
    
    // Enhanced navigation handling
    class NavigationManager {
        constructor() {
            this.init();
        }
        
        init() {
            this.setupEventListeners();
            this.setupBackButtonHandling();
            this.setupPageLoadHandling();
            this.setupErrorHandling();
        }
        
        setupEventListeners() {
            // Enhanced popstate handling
            window.addEventListener('popstate', (event) => {
                console.log('Popstate event triggered');
                this.handleBackNavigation(event);
            });
            
            // Enhanced pageshow handling
            window.addEventListener('pageshow', (event) => {
                console.log('Pageshow event triggered, persisted:', event.persisted);
                if (event.persisted) {
                    this.handlePageRestore();
                }
            });
            
            // Enhanced beforeunload handling
            window.addEventListener('beforeunload', (event) => {
                this.handlePageUnload();
            });
            
            // Page visibility change handling
            document.addEventListener('visibilitychange', () => {
                if (document.visibilityState === 'visible') {
                    this.handlePageVisible();
                }
            });
        }
        
        setupBackButtonHandling() {
            // Prevent hanging on back button
            history.replaceState({
                timestamp: Date.now(),
                page: window.location.pathname,
                scrollPosition: window.scrollY
            }, '', window.location.href);
        }
        
        setupPageLoadHandling() {
            navigationState.loadStartTime = performance.now();
            
            // Set maximum load time
            const loadTimeout = setTimeout(() => {
                if (navigationState.isNavigating) {
                    console.warn('Page load taking too long, forcing completion');
                    this.forcePageLoadComplete();
                }
            }, CONFIG.MAX_LOAD_TIME);
            
            // Clear timeout when page loads
            window.addEventListener('load', () => {
                clearTimeout(loadTimeout);
                this.handlePageLoadComplete();
            });
        }
        
        setupErrorHandling() {
            // Enhanced error handling for navigation issues
            window.addEventListener('error', (event) => {
                if (this.isNavigationError(event)) {
                    console.warn('Navigation error detected:', event.message);
                    this.handleNavigationError(event);
                }
            });
            
            // Unhandled promise rejections
            window.addEventListener('unhandledrejection', (event) => {
                console.warn('Unhandled promise rejection during navigation:', event.reason);
                if (navigationState.isNavigating) {
                    this.recoverFromNavigationError();
                }
            });
        }
        
        handleBackNavigation(event) {
            const state = event.state || {};
            const currentPath = window.location.pathname;
            
            // Special handling for stock detail pages
            if (this.isStockDetailPage(navigationState.currentPage) && 
                !this.isStockDetailPage(currentPath)) {
                console.log('Navigating back from stock detail page');
                this.handleStockDetailBackNavigation();
                return;
            }
            
            // General back navigation handling
            this.cleanupCurrentPage();
            this.restorePageState(state);
        }
        
        handlePageRestore() {
            console.log('Page restored from bfcache');
            
            // Re-initialize components that might have been broken
            this.reinitializeComponents();
            
            // Refresh dynamic content if needed
            this.refreshDynamicContent();
            
            // Restore scroll position
            if (history.state && history.state.scrollPosition) {
                window.scrollTo(0, history.state.scrollPosition);
            }
        }
        
        handlePageUnload() {
            // Save current state
            if (history.state) {
                history.replaceState({
                    ...history.state,
                    scrollPosition: window.scrollY,
                    timestamp: Date.now()
                }, '', window.location.href);
            }
            
            // Cleanup
            this.cleanupCurrentPage();
        }
        
        handlePageVisible() {
            // Page became visible again, check if we need to refresh
            if (history.state && history.state.timestamp) {
                const timeDiff = Date.now() - history.state.timestamp;
                if (timeDiff > 300000) { // 5 minutes
                    console.log('Page was hidden for too long, refreshing dynamic content');
                    this.refreshDynamicContent();
                }
            }
        }
        
        handlePageLoadComplete() {
            const loadTime = performance.now() - navigationState.loadStartTime;
            console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
            
            navigationState.isNavigating = false;
            document.body.classList.add('page-loaded');
            
            // Initialize page-specific features
            this.initializePageFeatures();
        }
        
        forcePageLoadComplete() {
            console.warn('Forcing page load completion due to timeout');
            navigationState.isNavigating = false;
            
            // Cancel any pending requests
            if (navigationState.abortController) {
                navigationState.abortController.abort();
            }
            
            // Mark page as loaded
            document.body.classList.add('page-loaded', 'force-loaded');
        }
        
        isNavigationError(event) {
            const message = event.message || '';
            return message.includes('Navigation') ||
                   message.includes('Loading') ||
                   message.includes('fetch') ||
                   message.includes('network');
        }
        
        handleNavigationError(event) {
            console.error('Navigation error:', event);
            
            // Try to recover
            setTimeout(() => {
                this.recoverFromNavigationError();
            }, CONFIG.RETRY_DELAY);
        }
        
        recoverFromNavigationError() {
            // Reset navigation state
            navigationState.isNavigating = false;
            
            // Re-enable UI elements
            this.enableUserInterface();
            
            // Show user-friendly message
            this.showRecoveryMessage();
        }
        
        isStockDetailPage(path) {
            return path && path.includes('/stocks/details/');
        }
        
        handleStockDetailBackNavigation() {
            // Clear stock-specific data
            if (window.stockChart) {
                window.stockChart = null;
            }
            
            // Clear any stock-specific intervals
            this.clearStockIntervals();
            
            // Force a clean navigation
            setTimeout(() => {
                if (document.referrer && !this.isStockDetailPage(document.referrer)) {
                    window.location.reload();
                }
            }, 100);
        }
        
        cleanupCurrentPage() {
            // Cancel any ongoing requests
            if (navigationState.abortController) {
                navigationState.abortController.abort();
                navigationState.abortController = null;
            }
            
            // Clear timers
            this.clearAllTimers();
            
            // Clear event listeners
            this.removeStaleEventListeners();
        }
        
        restorePageState(state) {
            if (state.scrollPosition) {
                window.scrollTo(0, state.scrollPosition);
            }
        }
        
        reinitializeComponents() {
            // Re-initialize Bootstrap components
            if (typeof bootstrap !== 'undefined') {
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            }
            
            // Re-initialize other components as needed
            this.initializePageFeatures();
        }
        
        refreshDynamicContent() {
            // Refresh any dynamic content that might be stale
            const dynamicElements = document.querySelectorAll('[data-dynamic-content]');
            dynamicElements.forEach(element => {
                if (element.dataset.refreshUrl) {
                    this.refreshElement(element);
                }
            });
        }
        
        refreshElement(element) {
            const url = element.dataset.refreshUrl;
            if (!url) return;
            
            fetch(url, {
                signal: this.getAbortSignal()
            })
            .then(response => response.text())
            .then(html => {
                element.innerHTML = html;
            })
            .catch(error => {
                console.warn('Failed to refresh element:', error);
            });
        }
        
        initializePageFeatures() {
            // Page-specific initialization
            if (this.isStockDetailPage(window.location.pathname)) {
                this.initializeStockPage();
            }
            
            // General features
            this.initializeNavigation();
            this.initializeForms();
        }
        
        initializeStockPage() {
            // Create new abort controller for stock page
            navigationState.abortController = new AbortController();
            
            // Initialize stock-specific features
            console.log('Initializing stock page features');
        }
        
        initializeNavigation() {
            // Enhanced link handling
            const links = document.querySelectorAll('a[href]');
            links.forEach(link => {
                if (!link.hasAttribute('data-nav-enhanced')) {
                    this.enhanceLink(link);
                    link.setAttribute('data-nav-enhanced', 'true');
                }
            });
        }
        
        enhanceLink(link) {
            link.addEventListener('click', (e) => {
                if (!link.target || link.target === '_self') {
                    navigationState.isNavigating = true;
                    navigationState.loadStartTime = performance.now();
                    
                    // Visual feedback
                    link.style.opacity = '0.7';
                    
                    // Reset after timeout
                    setTimeout(() => {
                        link.style.opacity = '';
                        navigationState.isNavigating = false;
                    }, 5000);
                }
            });
        }
        
        initializeForms() {
            // Enhanced form handling
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                if (!form.hasAttribute('data-form-enhanced')) {
                    this.enhanceForm(form);
                    form.setAttribute('data-form-enhanced', 'true');
                }
            });
        }
        
        enhanceForm(form) {
            form.addEventListener('submit', (e) => {
                const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitButton) {
                    submitButton.disabled = true;
                    setTimeout(() => {
                        submitButton.disabled = false;
                    }, 3000);
                }
            });
        }
        
        clearAllTimers() {
            // Clear intervals and timeouts
            for (let i = 1; i < 99999; i++) {
                window.clearTimeout(i);
                window.clearInterval(i);
            }
        }
        
        clearStockIntervals() {
            // Clear stock-specific intervals
            if (window.stockUpdateInterval) {
                clearInterval(window.stockUpdateInterval);
                window.stockUpdateInterval = null;
            }
        }
        
        removeStaleEventListeners() {
            // Remove duplicate handlers
            const handledElements = document.querySelectorAll('[data-nav-enhanced], [data-form-enhanced]');
            handledElements.forEach(el => {
                if (el.dataset.navEnhanced) {
                    el.removeAttribute('data-nav-enhanced');
                }
                if (el.dataset.formEnhanced) {
                    el.removeAttribute('data-form-enhanced');
                }
            });
        }
        
        enableUserInterface() {
            // Re-enable disabled UI elements
            const disabledElements = document.querySelectorAll('[disabled]');
            disabledElements.forEach(el => {
                if (!el.hasAttribute('data-permanently-disabled')) {
                    el.disabled = false;
                }
            });
            
            // Reset opacity
            const fadedElements = document.querySelectorAll('[style*="opacity"]');
            fadedElements.forEach(el => {
                if (!el.hasAttribute('data-permanent-opacity')) {
                    el.style.opacity = '';
                }
            });
        }
        
        showRecoveryMessage() {
            const message = document.createElement('div');
            message.className = 'alert alert-info alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x';
            message.style.zIndex = '9999';
            message.innerHTML = `
                <i class="fas fa-info-circle me-2"></i>
                Siden ble gjenopprettet etter en navigasjonsfeil.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.body.appendChild(message);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 5000);
        }
        
        getAbortSignal() {
            if (!navigationState.abortController) {
                navigationState.abortController = new AbortController();
            }
            return navigationState.abortController.signal;
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            new NavigationManager();
        });
    } else {
        new NavigationManager();
    }
    
    // Export for global access
    window.NavigationManager = NavigationManager;
})();
