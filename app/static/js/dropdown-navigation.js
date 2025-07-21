/**
 * Enhanced Dropdown Navigation for Aksjeradar
 * Fixes PC navigation issues where dropdown toggles interfere with navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDropdownNavigation();
});

function initializeDropdownNavigation() {
    console.log('Initializing dropdown navigation...');
    
    // Get all dropdown toggles
    const dropdownToggles = document.querySelectorAll('.navbar-nav .dropdown-toggle');
    
    dropdownToggles.forEach(function(toggle) {
        // Make sure dropdowns work on click
        toggle.addEventListener('click', function(e) {
            const dropdown = bootstrap.Dropdown.getOrCreateInstance(this);
            
            // On mobile, let Bootstrap handle it normally
            if (window.innerWidth <= 768) {
                return;
            }
            
            // On PC, prevent default href navigation and show dropdown
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle the dropdown
            if (this.getAttribute('aria-expanded') === 'true') {
                dropdown.hide();
            } else {
                // Hide other dropdowns first
                hideAllDropdowns();
                dropdown.show();
            }
        });
        
        // Add hover functionality on PC
        if (window.innerWidth > 768) {
            const parentLi = toggle.closest('li.dropdown');
            
            parentLi.addEventListener('mouseenter', function() {
                hideAllDropdowns();
                const dropdown = bootstrap.Dropdown.getOrCreateInstance(toggle);
                dropdown.show();
            });
            
            parentLi.addEventListener('mouseleave', function(e) {
                // Check if we're not moving to a child element
                if (!this.contains(e.relatedTarget)) {
                    const dropdown = bootstrap.Dropdown.getOrCreateInstance(toggle);
                    dropdown.hide();
                }
            });
        }
    });
    
    // Add double-click navigation to main sections on PC
    dropdownToggles.forEach(function(toggle) {
        toggle.addEventListener('dblclick', function(e) {
            if (window.innerWidth > 768) {
                navigateToMainPage(this.id);
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar-nav')) {
            hideAllDropdowns();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            hideAllDropdowns();
        }
    });
}

function hideAllDropdowns() {
    const dropdownToggles = document.querySelectorAll('.navbar-nav .dropdown-toggle');
    dropdownToggles.forEach(function(toggle) {
        const dropdown = bootstrap.Dropdown.getInstance(toggle);
        if (dropdown) {
            dropdown.hide();
        }
    });
}

function navigateToMainPage(dropdownId) {
    const navigationMap = {
        'stocksDropdown': '/stocks/',
        'analysisDropdown': '/analysis/',
        'portfolioDropdown': '/portfolio/',
        'newsDropdown': '/news/',
        'pricingDropdown': '/pricing/pricing'
    };
    
    const url = navigationMap[dropdownId];
    if (url) {
        window.location.href = url;
    }
}

// Accessibility improvements
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        hideAllDropdowns();
    }
    
    // Arrow key navigation within dropdowns
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        const activeDropdown = document.querySelector('.dropdown-menu.show');
        if (activeDropdown) {
            e.preventDefault();
            const items = activeDropdown.querySelectorAll('.dropdown-item:not(.disabled)');
            const currentIndex = Array.from(items).indexOf(document.activeElement);
            
            let nextIndex;
            if (e.key === 'ArrowDown') {
                nextIndex = (currentIndex + 1) % items.length;
            } else {
                nextIndex = (currentIndex - 1 + items.length) % items.length;
            }
            
            items[nextIndex].focus();
        }
    }
});

// Add visual feedback for dropdown states
const style = document.createElement('style');
style.textContent = `
    .navbar-nav .dropdown-toggle:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    .navbar-nav .dropdown-toggle[aria-expanded="true"] {
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
    }
    
    @media (min-width: 768px) {
        .navbar-nav .dropdown-menu {
            margin-top: 0;
            border-top: 3px solid #007bff;
        }
        
        .navbar-nav .dropdown:hover .dropdown-menu {
            display: block;
        }
    }
    
    /* Add loading indicator for navigation */
    .nav-loading::after {
        content: "";
        width: 12px;
        height: 12px;
        border: 2px solid transparent;
        border-top: 2px solid #ffffff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-left: 8px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// Add tooltip for double-click functionality on PC
if (window.innerWidth > 768) {
    const tooltipStyle = document.createElement('style');
    tooltipStyle.textContent = `
        .navbar-nav .dropdown-toggle::after {
            content: " (dobbeltklikk for å gå direkte til siden)";
            font-size: 0.7em;
            opacity: 0;
            transition: opacity 0.3s;
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            white-space: nowrap;
            z-index: 1000;
            margin-left: 10px;
            margin-top: -5px;
        }
        
        .navbar-nav .dropdown-toggle:hover::after {
            opacity: 1;
        }
    `;
    // Don't add this tooltip on mobile to avoid clutter
    if (window.innerWidth > 768) {
        document.head.appendChild(tooltipStyle);
    }
}

console.log('Dropdown navigation initialization complete');
