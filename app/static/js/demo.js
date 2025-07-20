/**
 * Demo functionality for Aksjeradar
 */
function showDemo(section) {
    // Hide all demo sections
    document.querySelectorAll('.demo-section').forEach(el => {
        el.style.display = 'none';
    });
    
    // Show the selected section
    const targetSection = document.getElementById(section + '-demo');
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Update active tab
    document.querySelectorAll('.demo-nav .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const activeTab = document.querySelector(`.demo-nav .btn[onclick="showDemo('${section}')"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
}

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Show first demo section by default
    showDemo('stocks');
    
    // Add any other demo initialization here
    console.log('Demo functionality loaded');
});
