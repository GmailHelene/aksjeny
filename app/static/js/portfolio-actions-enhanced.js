/**
 * Enhanced Portfolio Actions with Error Handling and Toast Notifications
 * Handles adding stocks to portfolio, watchlist, and tips with proper authentication
 */

class PortfolioActionsManager {
    constructor() {
        this.initializeEventListeners();
        this.initializeToastContainer();
    }

    initializeEventListeners() {
        // Portfolio actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-portfolio') || e.target.closest('.add-to-portfolio')) {
                e.preventDefault();
                const button = e.target.closest('.add-to-portfolio') || e.target;
                this.addToPortfolio(button);
            }
        });

        // Watchlist actions  
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-watchlist') || e.target.closest('.add-to-watchlist')) {
                e.preventDefault();
                const button = e.target.closest('.add-to-watchlist') || e.target;
                this.addToWatchlist(button);
            }
        });

        // Tips actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-tips') || e.target.closest('.add-to-tips')) {
                e.preventDefault();
                const button = e.target.closest('.add-to-tips') || e.target;
                this.addToTips(button);
            }
        });
    }

    initializeToastContainer() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
    }

    async addToPortfolio(button) {
        const symbol = button.dataset.symbol;
        const name = button.dataset.name || symbol;
        
        if (!symbol) {
            this.showToast('Feil: Mangler aksjesymbol', 'error');
            return;
        }

        try {
            this.setButtonLoading(button, 'Legger til i portefølje...');

            const response = await fetch('/api/portfolio/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    name: name,
                    shares: 1,
                    price: parseFloat(button.dataset.price) || 0
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showToast(`${symbol} lagt til i porteføljen!`, 'success');
                this.setButtonSuccess(button, '<i class="bi bi-check-circle"></i> I portefølje');
                
                // Update portfolio counter if exists
                this.updatePortfolioCount(1);
            } else {
                throw new Error(data.message || 'Ukjent feil ved tillegging til portefølje');
            }
        } catch (error) {
            console.error('Portfolio add error:', error);
            this.showToast(`Feil: ${error.message}`, 'error');
            this.restoreButton(button, '<i class="bi bi-briefcase"></i> Legg til i portefølje');
        }
    }

    async addToWatchlist(button) {
        const symbol = button.dataset.symbol;
        const name = button.dataset.name || symbol;
        
        if (!symbol) {
            this.showToast('Feil: Mangler aksjesymbol', 'error');
            return;
        }

        try {
            this.setButtonLoading(button, 'Legger til i favoritter...');

            const response = await fetch('/api/watchlist/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    name: name
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showToast(`${symbol} lagt til i favoritter!`, 'success');
                this.setButtonSuccess(button, '<i class="bi bi-heart-fill"></i> I favoritter');
                
                // Update watchlist counter if exists
                this.updateWatchlistCount(1);
            } else {
                throw new Error(data.message || 'Ukjent feil ved tillegging til favoritter');
            }
        } catch (error) {
            console.error('Watchlist add error:', error);
            this.showToast(`Feil: ${error.message}`, 'error');
            this.restoreButton(button, '<i class="bi bi-heart"></i> Legg til i favoritter');
        }
    }

    async addToTips(button) {
        const symbol = button.dataset.symbol;
        const name = button.dataset.name || symbol;
        
        if (!symbol) {
            this.showToast('Feil: Mangler aksjesymbol', 'error');
            return;
        }

        try {
            this.setButtonLoading(button, 'Legger til i tips...');

            const response = await fetch('/api/tips/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    name: name,
                    reason: button.dataset.reason || 'Lagt til fra aksjedetaljer',
                    analyst_rating: button.dataset.rating || null
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.showToast(`${symbol} lagt til i tips!`, 'success');
                this.setButtonSuccess(button, '<i class="bi bi-lightbulb-fill"></i> I tips');
                
                // Update tips counter if exists
                this.updateTipsCount(1);
            } else {
                throw new Error(data.message || 'Ukjent feil ved tillegging til tips');
            }
        } catch (error) {
            console.error('Tips add error:', error);
            this.showToast(`Feil: ${error.message}`, 'error');
            this.restoreButton(button, '<i class="bi bi-lightbulb"></i> Legg til i tips');
        }
    }

    setButtonLoading(button, text) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>${text}`;
    }

    setButtonSuccess(button, text) {
        button.disabled = false;
        button.innerHTML = text;
        button.classList.remove('btn-outline-primary', 'btn-outline-warning', 'btn-outline-info');
        button.classList.add('btn-success');
    }

    restoreButton(button, text) {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || text;
    }

    updatePortfolioCount(increment) {
        const counter = document.querySelector('.portfolio-count');
        if (counter) {
            const current = parseInt(counter.textContent) || 0;
            counter.textContent = current + increment;
        }
    }

    updateWatchlistCount(increment) {
        const counter = document.querySelector('.watchlist-count');
        if (counter) {
            const current = parseInt(counter.textContent) || 0;
            counter.textContent = current + increment;
        }
    }

    updateTipsCount(increment) {
        const counter = document.querySelector('.tips-count');
        if (counter) {
            const current = parseInt(counter.textContent) || 0;
            counter.textContent = current + increment;
        }
    }

    getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
        toast.id = toastId;
        toast.setAttribute('role', 'alert');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        container.appendChild(toast);
        
        // Initialize Bootstrap toast
        if (typeof bootstrap !== 'undefined') {
            const bsToast = new bootstrap.Toast(toast, { 
                delay: type === 'error' ? 8000 : 5000,
                autohide: true
            });
            bsToast.show();
            
            // Remove from DOM after hiding
            toast.addEventListener('hidden.bs.toast', () => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            });
        } else {
            // Fallback without Bootstrap
            setTimeout(() => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            }, type === 'error' ? 8000 : 5000);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if user action buttons are present
    if (document.querySelector('.add-to-portfolio, .add-to-watchlist, .add-to-tips')) {
        window.portfolioActionsManager = new PortfolioActionsManager();
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PortfolioActionsManager;
}
