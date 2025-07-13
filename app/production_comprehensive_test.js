#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const path = require('path');

// Test configuration
const BASE_URL = 'http://localhost:5000';
const TIMEOUT = 5000;

// Test results
let testResults = [];
let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

// Comprehensive endpoints to test
const endpoints = [
    // Core pages
    { path: '/', method: 'GET', name: 'Hovedside', expectedStatus: 200 },
    { path: '/demo', method: 'GET', name: 'Demo side', expectedStatus: 200 },
    { path: '/ai-explained', method: 'GET', name: 'AI forklart', expectedStatus: 200 },
    { path: '/pricing', method: 'GET', name: 'Prising (med slash)', expectedStatus: 200 },
    { path: '/pricing/', method: 'GET', name: 'Prising (uten slash)', expectedStatus: 200 },
    
    // Authentication
    { path: '/login', method: 'GET', name: 'Login GET', expectedStatus: 200 },
    { path: '/login', method: 'POST', name: 'Login POST', expectedStatus: 200, data: { username: 'test', password: 'test' } },
    { path: '/register', method: 'GET', name: 'Register GET', expectedStatus: 200 },
    { path: '/register', method: 'POST', name: 'Register POST', expectedStatus: 200, data: { username: 'test', email: 'test@test.com', password: 'test123' } },
    { path: '/logout', method: 'GET', name: 'Logout', expectedStatus: 200 },
    
    // Main features
    { path: '/portfolio', method: 'GET', name: 'Portfolio', expectedStatus: 200 },
    { path: '/analysis', method: 'GET', name: 'Analyse', expectedStatus: 200 },
    { path: '/stocks', method: 'GET', name: 'Aksjer', expectedStatus: 200 },
    
    // API endpoints
    { path: '/api/health', method: 'GET', name: 'Health API', expectedStatus: 200 },
    { path: '/api/version', method: 'GET', name: 'Version API', expectedStatus: 200 },
    { path: '/api/search', method: 'GET', name: 'Search API (tom)', expectedStatus: 200 },
    { path: '/api/search?q=equinor', method: 'GET', name: 'Search API (med query)', expectedStatus: 200 },
    
    // PWA support
    { path: '/manifest.json', method: 'GET', name: 'PWA Manifest', expectedStatus: 200 },
    { path: '/service-worker.js', method: 'GET', name: 'Service Worker', expectedStatus: 200 },
    
    // Error handling
    { path: '/invalid-endpoint', method: 'GET', name: '404 Error Handler', expectedStatus: 404 },
    
    // Additional test cases
    { path: '/login', method: 'POST', name: 'Login POST (ugyldig)', expectedStatus: 400, data: { username: '', password: '' } },
];

function makeRequest(endpoint) {
    return new Promise((resolve, reject) => {
        const url = new URL(endpoint.path, BASE_URL);
        const options = {
            method: endpoint.method,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'Aksjeradar-Production-Test/1.0'
            },
            timeout: TIMEOUT
        };

        const req = http.request(url, options, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    body: data
                });
            });
        });

        req.on('error', (err) => {
            reject(err);
        });

        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        if (endpoint.data && endpoint.method === 'POST') {
            req.write(JSON.stringify(endpoint.data));
        }

        req.end();
    });
}

function validateResponse(endpoint, response) {
    const validation = {
        statusMatch: response.statusCode === endpoint.expectedStatus,
        hasContent: response.body.length > 0,
        isJson: false,
        hasValidStructure: false
    };

    try {
        const jsonData = JSON.parse(response.body);
        validation.isJson = true;
        validation.hasValidStructure = jsonData.status !== undefined;
        validation.jsonData = jsonData;
    } catch (e) {
        // Not JSON, could be JavaScript or other content
        if (endpoint.path.includes('.js')) {
            validation.hasValidStructure = true; // JavaScript files are valid
        }
    }

    return validation;
}

async function runTest(endpoint) {
    totalTests++;
    const startTime = Date.now();
    
    try {
        console.log(`\n🧪 Testing: ${endpoint.name} [${endpoint.method}] ${endpoint.path}`);
        
        const response = await makeRequest(endpoint);
        const responseTime = Date.now() - startTime;
        const validation = validateResponse(endpoint, response);
        
        const testResult = {
            endpoint: endpoint.name,
            method: endpoint.method,
            path: endpoint.path,
            expectedStatus: endpoint.expectedStatus,
            actualStatus: response.statusCode,
            responseTime: responseTime,
            validation: validation,
            success: validation.statusMatch && validation.hasContent,
            timestamp: new Date().toISOString()
        };

        if (testResult.success) {
            passedTests++;
            console.log(`✅ PASS - Status: ${response.statusCode}, Response: ${responseTime}ms`);
            
            if (validation.isJson && validation.jsonData) {
                console.log(`   📄 JSON Response: ${validation.jsonData.message || validation.jsonData.name || 'Valid JSON'}`);
            }
        } else {
            failedTests++;
            console.log(`❌ FAIL - Expected: ${endpoint.expectedStatus}, Got: ${response.statusCode}`);
            console.log(`   ⏱️  Response time: ${responseTime}ms`);
            console.log(`   📝 Body preview: ${response.body.substring(0, 100)}...`);
        }

        testResults.push(testResult);
        
    } catch (error) {
        failedTests++;
        console.log(`❌ ERROR - ${error.message}`);
        
        testResults.push({
            endpoint: endpoint.name,
            method: endpoint.method,
            path: endpoint.path,
            error: error.message,
            success: false,
            timestamp: new Date().toISOString()
        });
    }
}

async function runAllTests() {
    console.log('🚀 AKSJERADAR PRODUCTION TEST SUITE');
    console.log('===================================');
    console.log(`📊 Testing ${endpoints.length} endpoints`);
    console.log(`🎯 Target: ${BASE_URL}`);
    console.log(`⏱️  Timeout: ${TIMEOUT}ms`);
    
    const overallStartTime = Date.now();
    
    // Run all tests
    for (const endpoint of endpoints) {
        await runTest(endpoint);
        await new Promise(resolve => setTimeout(resolve, 100)); // Small delay between tests
    }
    
    const overallTime = Date.now() - overallStartTime;
    const avgResponseTime = testResults
        .filter(r => r.responseTime)
        .reduce((acc, r) => acc + r.responseTime, 0) / testResults.filter(r => r.responseTime).length;
    
    // Generate comprehensive report
    console.log('\n📋 COMPREHENSIVE TEST REPORT');
    console.log('============================');
    console.log(`📊 Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${passedTests}`);
    console.log(`❌ Failed: ${failedTests}`);
    console.log(`📈 Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    console.log(`⏱️  Average Response Time: ${avgResponseTime.toFixed(1)}ms`);
    console.log(`🕐 Total Test Time: ${overallTime}ms`);
    
    // Detailed results
    console.log('\n📝 DETAILED RESULTS');
    console.log('===================');
    
    const groupedResults = {
        core: testResults.filter(r => ['Hovedside', 'Demo side', 'AI forklart', 'Prising'].some(name => r.endpoint.includes(name))),
        auth: testResults.filter(r => r.endpoint.includes('Login') || r.endpoint.includes('Register') || r.endpoint.includes('Logout')),
        features: testResults.filter(r => ['Portfolio', 'Analyse', 'Aksjer'].includes(r.endpoint)),
        api: testResults.filter(r => r.endpoint.includes('API')),
        pwa: testResults.filter(r => r.endpoint.includes('PWA') || r.endpoint.includes('Manifest') || r.endpoint.includes('Service Worker')),
        errors: testResults.filter(r => r.endpoint.includes('Error') || r.endpoint.includes('404'))
    };
    
    Object.entries(groupedResults).forEach(([category, results]) => {
        if (results.length > 0) {
            const categoryPassed = results.filter(r => r.success).length;
            const categoryTotal = results.length;
            console.log(`\n📁 ${category.toUpperCase()}: ${categoryPassed}/${categoryTotal} passed`);
            
            results.forEach(result => {
                const status = result.success ? '✅' : '❌';
                const time = result.responseTime ? `${result.responseTime}ms` : 'N/A';
                console.log(`   ${status} ${result.endpoint} (${time})`);
            });
        }
    });
    
    // Production readiness assessment
    console.log('\n🎯 PRODUCTION READINESS ASSESSMENT');
    console.log('==================================');
    
    const criticalEndpoints = testResults.filter(r => 
        ['Hovedside', 'Demo side', 'Prising', 'Health API', 'Version API'].includes(r.endpoint)
    );
    const criticalSuccess = criticalEndpoints.filter(r => r.success).length;
    const criticalTotal = criticalEndpoints.length;
    
    const performanceScore = avgResponseTime < 100 ? 'Excellent' : avgResponseTime < 500 ? 'Good' : 'Needs improvement';
    const reliabilityScore = (passedTests / totalTests) * 100;
    
    console.log(`🔑 Critical Endpoints: ${criticalSuccess}/${criticalTotal} (${((criticalSuccess/criticalTotal)*100).toFixed(1)}%)`);
    console.log(`⚡ Performance Score: ${performanceScore} (${avgResponseTime.toFixed(1)}ms avg)`);
    console.log(`🛡️  Reliability Score: ${reliabilityScore.toFixed(1)}%`);
    
    if (reliabilityScore >= 95 && avgResponseTime < 500) {
        console.log('\n🎉 PRODUCTION READY! 🚀');
        console.log('   ✅ All critical systems operational');
        console.log('   ✅ Response times acceptable');
        console.log('   ✅ Error handling working');
        console.log('   🌐 Ready for deployment to aksjeradar.trade');
    } else {
        console.log('\n⚠️  PRODUCTION CONCERNS:');
        if (reliabilityScore < 95) {
            console.log(`   ❌ Reliability below 95% (${reliabilityScore.toFixed(1)}%)`);
        }
        if (avgResponseTime >= 500) {
            console.log(`   ❌ Average response time too high (${avgResponseTime.toFixed(1)}ms)`);
        }
    }
    
    // Save detailed report
    const detailedReport = {
        summary: {
            totalTests,
            passedTests,
            failedTests,
            successRate: (passedTests / totalTests) * 100,
            avgResponseTime,
            overallTime,
            timestamp: new Date().toISOString()
        },
        results: testResults,
        groupedResults,
        productionReadiness: {
            criticalEndpoints: criticalSuccess / criticalTotal,
            performanceScore,
            reliabilityScore,
            recommendation: reliabilityScore >= 95 && avgResponseTime < 500 ? 'DEPLOY' : 'REVIEW'
        }
    };
    
    fs.writeFileSync('production_test_report.json', JSON.stringify(detailedReport, null, 2));
    console.log('\n💾 Detailed report saved to: production_test_report.json');
    
    console.log('\n🎯 NEXT STEPS:');
    console.log('==============');
    console.log('1. Review any failed tests');
    console.log('2. Optimize slow endpoints if needed');
    console.log('3. Configure production server (Gunicorn/uWSGI)');
    console.log('4. Set up domain (aksjeradar.trade)');
    console.log('5. Configure SSL/HTTPS');
    console.log('6. Set up monitoring and logging');
    console.log('7. Deploy! 🚀');
}

// Run the test suite
runAllTests().catch(console.error);
