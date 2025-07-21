// JavaScript endpoint testing utility for Aksjeradar
// This script provides client-side testing and error handling for endpoints

class EndpointTester {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
        this.results = [];
    }

    async testEndpoint(url, method = 'GET', data = null) {
        const fullUrl = this.baseUrl + url;
        
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            };

            if (data && method !== 'GET') {
                options.body = JSON.stringify(data);
            }

            const response = await fetch(fullUrl, options);
            
            const result = {
                url: url,
                method: method,
                status: response.status,
                ok: response.ok,
                timestamp: new Date().toISOString()
            };

            this.results.push(result);
            return result;
            
        } catch (error) {
            const result = {
                url: url,
                method: method,
                status: 'ERROR',
                error: error.message,
                timestamp: new Date().toISOString()
            };
            
            this.results.push(result);
            return result;
        }
    }

    async testMultipleEndpoints(endpoints) {
        console.log('🧪 Testing multiple endpoints...');
        
        for (const endpoint of endpoints) {
            const result = await this.testEndpoint(endpoint.url, endpoint.method, endpoint.data);
            console.log(`${result.ok ? '✅' : '❌'} ${endpoint.url}: ${result.status}`);
        }
        
        return this.results;
    }

    generateReport() {
        const passed = this.results.filter(r => r.ok).length;
        const total = this.results.length;
        
        console.log(`\n📊 Test Results: ${passed}/${total} passed`);
        
        // Show failed tests
        const failed = this.results.filter(r => !r.ok);
        if (failed.length > 0) {
            console.log('\n❌ Failed tests:');
            failed.forEach(test => {
                console.log(`   ${test.url}: ${test.status} ${test.error || ''}`);
            });
        }
        
        return {
            passed: passed,
            total: total,
            failed: failed,
            results: this.results
        };
    }
}

// Common endpoint tests
const commonEndpoints = [
    { url: '/', method: 'GET' },
    { url: '/demo', method: 'GET' },
    { url: '/ai-explained', method: 'GET' },
    { url: '/pricing', method: 'GET' },  // Now expects HTML response
    { url: '/api/pricing/plans', method: 'GET' },  // JSON API endpoint
    { url: '/api/health', method: 'GET' },
    { url: '/api/version', method: 'GET' }
];

// Error handling utility
function handleApiError(error, context = '') {
    console.error(`API Error${context ? ' in ' + context : ''}:`, error);
    
    // Show user-friendly error message
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        return 'Network error - please check your connection';
    } else if (error.status === 404) {
        return 'Resource not found';
    } else if (error.status === 500) {
        return 'Server error - please try again later';
    } else {
        return 'An unexpected error occurred';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EndpointTester, commonEndpoints, handleApiError };
}

// Auto-run tests if this script is loaded directly
// Auto-run tests if this script is loaded directly (Node.js)
if (require.main === module) {
    const baseUrl = process.argv[2] || 'http://localhost:5000';
    const tester = new EndpointTester(baseUrl);
    tester.testMultipleEndpoints(commonEndpoints)
        .then(() => tester.generateReport())
        .catch(error => {
            console.error('Test suite failed:', error);
            process.exit(1);
        });
}