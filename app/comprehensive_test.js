#!/usr/bin/env node
/**
 * Omfattende endepunkt-test for Aksjeradar
 */

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

            const startTime = Date.now();
            const response = await fetch(fullUrl, options);
            const responseTime = Date.now() - startTime;
            
            const result = {
                url: url,
                method: method,
                status: response.status,
                ok: response.ok,
                responseTime: responseTime,
                timestamp: new Date().toISOString()
            };

            // Try to parse JSON response
            try {
                const jsonData = await response.json();
                result.data = jsonData;
            } catch (e) {
                result.contentType = response.headers.get('content-type');
            }

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
        console.log('=====================================');
        
        for (const endpoint of endpoints) {
            const result = await this.testEndpoint(endpoint.url, endpoint.method, endpoint.data);
            
            const status = result.ok ? '✅' : '❌';
            const timeStr = result.responseTime ? ` (${result.responseTime}ms)` : '';
            
            console.log(`${status} ${endpoint.method || 'GET'} ${endpoint.url}: ${result.status}${timeStr}`);
            
            // Show some response data if available
            if (result.data && result.data.message) {
                console.log(`   📝 ${result.data.message}`);
            }
            
            if (result.error) {
                console.log(`   ❗ Error: ${result.error}`);
            }
        }
        
        return this.results;
    }

    generateReport() {
        const passed = this.results.filter(r => r.ok).length;
        const total = this.results.length;
        
        console.log('\\n=====================================');
        console.log(`📊 Test Results: ${passed}/${total} passed`);
        
        // Calculate average response time
        const responseTimes = this.results.filter(r => r.responseTime).map(r => r.responseTime);
        if (responseTimes.length > 0) {
            const avgTime = responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length;
            console.log(`⏱️  Average response time: ${avgTime.toFixed(1)}ms`);
        }
        
        // Show failed tests
        const failed = this.results.filter(r => !r.ok);
        if (failed.length > 0) {
            console.log('\\n❌ Failed tests:');
            failed.forEach(test => {
                console.log(`   ${test.url}: ${test.status} ${test.error || ''}`);
            });
        }
        
        // Show successful tests with details
        const successful = this.results.filter(r => r.ok);
        if (successful.length > 0) {
            console.log('\\n✅ Successful tests:');
            successful.forEach(test => {
                const timeStr = test.responseTime ? ` (${test.responseTime}ms)` : '';
                console.log(`   ${test.url}: ${test.status}${timeStr}`);
            });
        }
        
        return {
            passed: passed,
            total: total,
            failed: failed,
            successful: successful,
            results: this.results
        };
    }
}

// Comprehensive endpoint tests
const comprehensiveEndpoints = [
    // Basic pages
    { url: '/', method: 'GET' },
    { url: '/demo', method: 'GET' },
    { url: '/ai-explained', method: 'GET' },
    { url: '/pricing', method: 'GET' },
    { url: '/pricing/', method: 'GET' },
    
    // Authentication
    { url: '/login', method: 'GET' },
    { url: '/login', method: 'POST', data: { username: 'test', password: 'test' } },
    { url: '/register', method: 'GET' },
    { url: '/register', method: 'POST', data: { username: 'test', email: 'test@test.com', password: 'test' } },
    { url: '/logout', method: 'GET' },
    
    // Application pages
    { url: '/portfolio', method: 'GET' },
    { url: '/analysis', method: 'GET' },
    { url: '/stocks', method: 'GET' },
    
    // API endpoints
    { url: '/api/health', method: 'GET' },
    { url: '/api/version', method: 'GET' },
    
    // Error tests
    { url: '/nonexistent', method: 'GET' },
];

// Error handling utility
function handleApiError(error, context = '') {
    console.error(`API Error ${context}:`, error);
    
    if (error.response) {
        console.error(`Status: ${error.response.status}`);
        console.error(`Data:`, error.response.data);
    } else if (error.request) {
        console.error('No response received:', error.request);
    } else {
        console.error('Error message:', error.message);
    }
}

// Auto-run tests if this script is loaded directly (Node.js)
if (require.main === module) {
    const baseUrl = process.argv[2] || 'http://localhost:5000';
    console.log(`🎯 Testing Aksjeradar endpoints at: ${baseUrl}`);
    console.log('=====================================');
    
    const tester = new EndpointTester(baseUrl);
    tester.testMultipleEndpoints(comprehensiveEndpoints)
        .then(() => {
            const report = tester.generateReport();
            
            console.log('\\n📈 Test Summary:');
            console.log(`   Success rate: ${((report.passed / report.total) * 100).toFixed(1)}%`);
            
            if (report.passed === report.total) {
                console.log('\\n🎉 All tests passed! Aksjeradar is working correctly.');
            } else {
                console.log('\\n⚠️  Some tests failed. Check the details above.');
            }
            
            process.exit(report.passed === report.total ? 0 : 1);
        })
        .catch(error => {
            console.error('Test suite failed:', error);
            process.exit(1);
        });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EndpointTester, comprehensiveEndpoints, handleApiError };
}
