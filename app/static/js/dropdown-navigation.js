/**
 * Enhanced Dropdown Navigation for Aksjeradar
 * Fixes PC navigation issues where dropdown toggles interfere with navigation
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDropdownNavigation();
});

/**
 * Enhanced Dropdown Navigation for Aksjeradar
 * Improved PC navigation with clear visual indicators and easier access
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDropdownNavigation();
});

function initializeDropdownNavigation() {
    console.log('Initializing enhanced dropdown navigation...');
    
    // Get all dropdown toggles
    const dropdownToggles = document.querySelectorAll('.navbar-nav .dropdown-toggle');
    
    dropdownToggles.forEach(function(toggle) {
        const parentLi = toggle.closest('li.dropdown');
        
        // Enhanced click handling for PC and mobile
        toggle.addEventListener('click', function(e) {
            // On mobile, let Bootstrap handle it normally
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const dropdown = bootstrap.Dropdown.getOrCreateInstance(this);
                
                if (this.getAttribute('aria-expanded') === 'true') {
                    dropdown.hide();
                } else {
                    hideAllDropdowns();
                    dropdown.show();
                }
                return;
            }
            
            // On PC: Enhanced click detection with visual feedback
            const rect = this.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const linkWidth = rect.width;
            
            // Check if clicking on the dropdown arrow (last 40px for easier access)
            if (clickX > linkWidth - 40) {
                e.preventDefault();
                e.stopPropagation();
                
                const dropdown = bootstrap.Dropdown.getOrCreateInstance(this);
                
                if (this.getAttribute('aria-expanded') === 'true') {
                    dropdown.hide();
                } else {
                    hideAllDropdowns();
                    dropdown.show();
                }
                
                // Add visual feedback
                this.classList.add('dropdown-clicked');
                setTimeout(() => this.classList.remove('dropdown-clicked'), 200);
            }
            // If clicking on the main link area, navigate to main page
        });
        
        // Double-click functionality for direct navigation on PC
        if (window.innerWidth > 768) {
            toggle.addEventListener('dblclick', function(e) {
                e.preventDefault();
                navigateToMainPage(this.id);
            });
        }
        
        // Enhanced hover functionality for PC
        if (window.innerWidth > 768) {
            let hoverTimeout;
            
            parentLi.addEventListener('mouseenter', function() {
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    hideAllDropdowns();
                    const dropdown = bootstrap.Dropdown.getOrCreateInstance(toggle);
                    dropdown.show();
                    
                    // Add visual indicator
                    toggle.classList.add('dropdown-hovering');
                }, 100); // Small delay to prevent accidental triggers
            });
            
            parentLi.addEventListener('mouseleave', function(e) {
                clearTimeout(hoverTimeout);
                
                // Check if we're not moving to a child element
                if (!this.contains(e.relatedTarget)) {
                    const dropdown = bootstrap.Dropdown.getOrCreateInstance(toggle);
                    dropdown.hide();
                    
                    // Remove visual indicator
                    toggle.classList.remove('dropdown-hovering');
                }
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar-nav')) {
            hideAllDropdowns();
        }
    });
    
    // Handle window resize - reinitialize if needed
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            hideAllDropdowns();
        }
    });
    
    // Add keyboard shortcuts for better accessibility
    document.addEventListener('keydown', function(e) {
        // Alt + number keys for quick navigation
        if (e.altKey && !e.ctrlKey && !e.shiftKey) {
            switch(e.key) {
                case '1':
                    e.preventDefault();
                    window.location.href = '/stocks/';
                    break;
                case '2':
                    e.preventDefault();
                    window.location.href = '/analysis/';
                    break;
                case '3':
                    e.preventDefault();
                    window.location.href = '/portfolio/';
                    break;
                case '4':
                    e.preventDefault();
                    window.location.href = '/news/';
                    break;
                case '5':
                    e.preventDefault();
                    window.location.href = '/pricing/pricing';
                    break;
            }
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

// Add enhanced visual feedback and styling
const style = document.createElement('style');
style.textContent = `
    /* Enhanced PC Navigation Styles */
    @media (min-width: 769px) {
        .navbar-nav .dropdown-toggle {
            position: relative;
            padding-right: 40px !important;
            transition: all 0.2s ease;
        }
        
        .navbar-nav .dropdown-toggle::after {
            content: "▼";
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 12px;
            border: none !important;
            width: auto !important;
            height: auto !important;
            background: rgba(255,255,255,0.3);
            padding: 4px 8px;
            border-radius: 12px;
            transition: all 0.2s ease;
        }
        
        .navbar-nav .dropdown-toggle:hover::after {
            background: rgba(255,255,255,0.5);
            transform: translateY(-50%) scale(1.1);
        }
        
        .navbar-nav .dropdown-toggle.dropdown-clicked::after,
        .navbar-nav .dropdown-toggle[aria-expanded="true"]::after {
            content: "▲";
            background: rgba(255,255,255,0.7);
            transform: translateY(-50%) scale(1.1);
        }
        
        .navbar-nav .dropdown-toggle.dropdown-hovering {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }
        
        .navbar-nav .dropdown-menu {
            margin-top: 0;
            border-top: 3px solid #007bff;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
            border-radius: 0 0 8px 8px;
        }
        
        /* Visual indicator for clickable dropdown area */
        .navbar-nav .dropdown-toggle:hover {
            background: linear-gradient(90deg, transparent 0%, transparent 60%, rgba(255,255,255,0.1) 60%, rgba(255,255,255,0.2) 100%);
            border-radius: 4px;
        }
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .navbar-nav .dropdown-toggle::after {
            margin-left: 8px;
        }
        
        .navbar-collapse {
            background: rgba(0,0,0,0.05);
            margin-top: 10px;
            border-radius: 8px;
            padding: 10px;
        }
        
        .navbar-nav .dropdown-menu {
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border: none;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
    }
    
    /* Remove any problematic scrollbar styles */
    .navbar-nav {
        overflow: visible !important;
    }
    
    .navbar-collapse {
        overflow: visible !important;
    }
    
    /* Keyboard shortcut help tooltip */
    .navbar-brand::after {
        content: "💡 Tips: Alt+1-5 for hurtignavigering";
        position: absolute;
        bottom: -25px;
        left: 0;
        font-size: 11px;
        opacity: 0;
        transition: opacity 0.3s;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        white-space: nowrap;
        z-index: 1000;
    }
    
    .navbar-brand:hover::after {
        opacity: 1;
    }
    
    @media (max-width: 768px) {
        .navbar-brand::after {
            display: none;
        }
    }
`;
document.head.appendChild(style);

console.log('Enhanced dropdown navigation initialization complete');

// Add help notification for PC users
if (window.innerWidth > 768) {
    // Show a brief help notification after page load
    setTimeout(() => {
        const helpDiv = document.createElement('div');
        helpDiv.innerHTML = `
            <div style="position: fixed; top: 20px; right: 20px; background: #007bff; color: white; padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999; font-size: 14px; max-width: 300px;">
                <div style="font-weight: bold; margin-bottom: 5px;">🎯 Navigasjonstips:</div>
                <div style="font-size: 12px;">
                    • Klikk på pilene (▼) for å åpne menyer<br>
                    • Klikk på teksten for direkte navigering<br>
                    • Bruk Alt+1-5 for hurtignavigering
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="position: absolute; top: 5px; right: 8px; background: none; border: none; color: white; font-size: 16px; cursor: pointer;">×</button>
            </div>
        `;
        document.body.appendChild(helpDiv);
        
        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (helpDiv.parentElement) {
                helpDiv.remove();
            }
        }, 8000);
    }, 2000);
}
