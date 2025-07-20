/**
 * Portfolio functionality for Aksjeradar
 */

// Portfolio management functions
function addStock(ticker, shares, price) {
    // Add stock to portfolio
    console.log(`Adding ${shares} shares of ${ticker} at ${price}`);
    // Implementation would go here
}

function removeStock(ticker) {
    // Remove stock from portfolio
    console.log(`Removing ${ticker} from portfolio`);
    // Implementation would go here
}

function updatePortfolio() {
    // Update portfolio display
    console.log('Updating portfolio...');
    // Implementation would go here
}

// Initialize portfolio functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Portfolio functionality loaded');
    
    // Add event listeners for portfolio actions
    const addButtons = document.querySelectorAll('.add-stock-btn');
    addButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const ticker = this.dataset.ticker;
            // Handle add stock
        });
    });
    
    const removeButtons = document.querySelectorAll('.remove-stock-btn');
    removeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const ticker = this.dataset.ticker;
            removeStock(ticker);
        });
    });
});
