// Apply number formatting to analysis templates
function formatNumber(value) {
    return new Intl.NumberFormat('en-US', { style: 'decimal', minimumFractionDigits: 2 }).format(value);
}

// Example usage in analysis template
const formattedValue = formatNumber(rawValue); // filepath: /workspaces/aksjeradarny/analysisTemplate.js