/**
 * Advanced Performance Optimization Service
 */
class PerformanceOptimizer {
    constructor() {
        this.imageObserver = null;
        this.intersectionObserver = null;
        this.prefetchQueue = new Set();
        this.init();
    }

    init() {
        this.setupLazyLoading();
        this.setupIntersectionObserver();
        this.setupPrefetching();
        this.optimizeScrolling();
        this.setupPerformanceMonitoring();
    }

    setupLazyLoading() {
        // Lazy load images
        this.imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        this.imageObserver.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.01
        });

        // Observe all lazy images
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.classList.add('lazy');
            this.imageObserver.observe(img);
        });
    }

    setupIntersectionObserver() {
        // Progressive content loading
        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const loadAction = element.dataset.loadAction;
                    
                    if (loadAction) {
                        this.executeLoadAction(loadAction, element);
                        this.intersectionObserver.unobserve(element);
                    }
                }
            });
        }, {
            rootMargin: '100px 0px',
            threshold: 0.1
        });
    }

    setupPrefetching() {
        // Prefetch critical resources on hover
        document.addEventListener('mouseover', (e) => {
            const link = e.target.closest('a[href]');
            if (link && this.shouldPrefetch(link.href)) {
                this.prefetchPage(link.href);
            }
        });

        // Prefetch on mobile touch start
        document.addEventListener('touchstart', (e) => {
            const link = e.target.closest('a[href]');
            if (link && this.shouldPrefetch(link.href)) {
                this.prefetchPage(link.href);
            }
        });
    }

    shouldPrefetch(url) {
        // Don't prefetch external links or already prefetched
        return url.startsWith('/') && 
               !this.prefetchQueue.has(url) && 
               !url.includes('#') &&
               !url.includes('logout');
    }

    prefetchPage(url) {
        if (this.prefetchQueue.has(url)) return;
        
        this.prefetchQueue.add(url);
        
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
        
        console.log(`Prefetched: ${url}`);
    }

    executeLoadAction(action, element) {
        switch (action) {
            case 'load-stock-chart':
                this.loadStockChart(element);
                break;
            case 'load-news-feed':
                this.loadNewsFeed(element);
                break;
            case 'load-portfolio-data':
                this.loadPortfolioData(element);
                break;
            default:
                console.warn(`Unknown load action: ${action}`);
        }
    }

    async loadStockChart(element) {
        const ticker = element.dataset.ticker;
        if (!ticker) return;

        try {
            element.innerHTML = loadingManager.skeletonTemplates.get('chart');
            
            const response = await fetch(`/api/stocks/${ticker}/chart`);
            const data = await response.json();
            
            // Render chart with the data
            this.renderChart(element, data);
        } catch (error) {
            console.error('Error loading chart:', error);
            element.innerHTML = '<p class="text-muted">Feil ved lasting av diagram</p>';
        }
    }

    async loadNewsFeed(element) {
        try {
            loadingManager.showSkeleton(element.id, 'news-item', 3);
            
            const response = await fetch('/api/news/latest');
            const data = await response.json();
            
            this.renderNewsFeed(element, data);
        } catch (error) {
            console.error('Error loading news:', error);
            element.innerHTML = '<p class="text-muted">Feil ved lasting av nyheter</p>';
        }
    }

    optimizeScrolling() {
        let ticking = false;
        let lastScrollY = 0;

        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    const currentScrollY = window.scrollY;
                    
                    // Show/hide header on scroll
                    const header = document.querySelector('.navbar');
                    if (header) {
                        if (currentScrollY > lastScrollY && currentScrollY > 100) {
                            header.style.transform = 'translateY(-100%)';
                        } else {
                            header.style.transform = 'translateY(0)';
                        }
                    }
                    
                    lastScrollY = currentScrollY;
                    ticking = false;
                });
                ticking = true;
            }
        };

        // Add smooth scrolling transition to header
        const header = document.querySelector('.navbar');
        if (header) {
            header.style.transition = 'transform 0.3s ease';
        }

        window.addEventListener('scroll', handleScroll, { passive: true });
    }

    setupPerformanceMonitoring() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                const loadTime = perfData.loadEventEnd - perfData.fetchStart;
                
                console.log(`Page load time: ${loadTime}ms`);
                
                // Send to analytics if needed
                this.reportPerformanceMetrics({
                    loadTime,
                    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.fetchStart,
                    firstPaint: this.getFirstPaint(),
                    page: window.location.pathname
                });
            }, 0);
        });
    }

    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? firstPaint.startTime : null;
    }

    reportPerformanceMetrics(metrics) {
        // Report to backend for monitoring
        if (metrics.loadTime > 3000) {
            console.warn('Slow page load detected:', metrics);
        }
    }

    // Debounce function for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle function for performance
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Optimize table rendering for large datasets
    virtualizeTable(tableId, data, renderRow, itemHeight = 50) {
        const container = document.getElementById(tableId);
        if (!container) return;

        const visibleItems = Math.ceil(container.clientHeight / itemHeight) + 5;
        let startIndex = 0;

        const render = () => {
            const endIndex = Math.min(startIndex + visibleItems, data.length);
            const visibleData = data.slice(startIndex, endIndex);
            
            container.innerHTML = visibleData.map((item, index) => 
                renderRow(item, startIndex + index)
            ).join('');
        };

        const handleScroll = this.throttle(() => {
            const scrollTop = container.scrollTop;
            const newStartIndex = Math.floor(scrollTop / itemHeight);
            
            if (newStartIndex !== startIndex) {
                startIndex = newStartIndex;
                render();
            }
        }, 16);

        container.addEventListener('scroll', handleScroll);
        render();
    }
}

// Initialize performance optimizer
const performanceOptimizer = new PerformanceOptimizer();

// Export for use in other modules
window.performanceOptimizer = performanceOptimizer;
