#!/usr/bin/env node

const http = require('http');
const fs = require('fs');

// Test configuration
const BASE_URL = 'http://localhost:5000';
const TIMEOUT = 10000;

// Test results
let testResults = [];
let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function makeRequest(endpoint, data = null, headers = {}) {
    return new Promise((resolve, reject) => {
        const url = new URL(endpoint.path, BASE_URL);
        const options = {
            method: endpoint.method,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'Aksjeradar-Full-Test/1.0',
                ...headers
            },
            timeout: TIMEOUT
        };

        const req = http.request(url, options, (res) => {
            let responseData = '';
            res.on('data', (chunk) => {
                responseData += chunk;
            });
            
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    body: responseData,
                    cookies: res.headers['set-cookie'] || []
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

        if (data && (endpoint.method === 'POST' || endpoint.method === 'PUT')) {
            req.write(JSON.stringify(data));
        }

        req.end();
    });
}

function extractSessionCookie(cookies) {
    if (!cookies || !Array.isArray(cookies)) return null;
    
    for (const cookie of cookies) {
        if (cookie.includes('session=')) {
            return cookie.split(';')[0];
        }
    }
    return null;
}

function buildCookieString(cookies) {
    if (!cookies || !Array.isArray(cookies)) return '';
    
    return cookies.map(cookie => cookie.split(';')[0]).join('; ');
}

async function runTest(endpoint, sessionCookies = null, userData = null) {
    totalTests++;
    const startTime = Date.now();
    
    try {
        console.log(`\n🧪 Testing: ${endpoint.name} [${endpoint.method}] ${endpoint.path}`);
        
        const headers = {};
        if (sessionCookies) {
            headers['Cookie'] = Array.isArray(sessionCookies) ? buildCookieString(sessionCookies) : sessionCookies;
        }
        
        const response = await makeRequest(endpoint, userData, headers);
        const responseTime = Date.now() - startTime;
        
        const testResult = {
            endpoint: endpoint.name,
            method: endpoint.method,
            path: endpoint.path,
            expectedStatus: endpoint.expectedStatus,
            actualStatus: response.statusCode,
            responseTime: responseTime,
            success: response.statusCode === endpoint.expectedStatus,
            timestamp: new Date().toISOString(),
            sessionCookies: response.cookies
        };

        if (testResult.success) {
            passedTests++;
            console.log(`✅ PASS - Status: ${response.statusCode}, Response: ${responseTime}ms`);
            
            try {
                const jsonData = JSON.parse(response.body);
                if (jsonData.message) {
                    console.log(`   📄 Response: ${jsonData.message}`);
                }
            } catch (e) {
                // Not JSON, that's fine
            }
        } else {
            failedTests++;
            console.log(`❌ FAIL - Expected: ${endpoint.expectedStatus}, Got: ${response.statusCode}`);
            console.log(`   ⏱️  Response time: ${responseTime}ms`);
            console.log(`   📝 Body preview: ${response.body.substring(0, 200)}...`);
        }

        testResults.push(testResult);
        return testResult;
        
    } catch (error) {
        failedTests++;
        console.log(`❌ ERROR - ${error.message}`);
        
        const errorResult = {
            endpoint: endpoint.name,
            method: endpoint.method,
            path: endpoint.path,
            error: error.message,
            success: false,
            timestamp: new Date().toISOString()
        };
        
        testResults.push(errorResult);
        return errorResult;
    }
}

async function runFullTestSuite() {
    console.log('🚀 AKSJERADAR FULL USER TEST SUITE');
    console.log('==================================');
    console.log(`🎯 Target: ${BASE_URL}`);
    console.log(`⏱️  Timeout: ${TIMEOUT}ms`);
    console.log('📊 Testing: Anonymous, Basic, Pro, and Admin users');
    
    const overallStartTime = Date.now();
    
    // ===== PHASE 1: ANONYMOUS USER TESTS =====
    console.log('\n🌐 PHASE 1: ANONYMOUS USER TESTS');
    console.log('=================================');
    
    const anonymousEndpoints = [
        { path: '/', method: 'GET', name: 'Hovedside (Anonymous)', expectedStatus: 200 },
        { path: '/demo', method: 'GET', name: 'Demo (Anonymous)', expectedStatus: 200 },
        { path: '/ai-explained', method: 'GET', name: 'AI Explained (Anonymous)', expectedStatus: 200 },
        { path: '/pricing', method: 'GET', name: 'Pricing (Anonymous)', expectedStatus: 200 },
        { path: '/login', method: 'GET', name: 'Login Page (Anonymous)', expectedStatus: 200 },
        { path: '/register', method: 'GET', name: 'Register Page (Anonymous)', expectedStatus: 200 },
        { path: '/api/health', method: 'GET', name: 'Health API (Anonymous)', expectedStatus: 200 },
        { path: '/api/version', method: 'GET', name: 'Version API (Anonymous)', expectedStatus: 200 },
        { path: '/api/search', method: 'GET', name: 'Search API (Anonymous)', expectedStatus: 200 },
        { path: '/manifest.json', method: 'GET', name: 'PWA Manifest (Anonymous)', expectedStatus: 200 },
        { path: '/service-worker.js', method: 'GET', name: 'Service Worker (Anonymous)', expectedStatus: 200 }
    ];
    
    // Test anonymous endpoints
    for (const endpoint of anonymousEndpoints) {
        await runTest(endpoint);
        await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    // Test premium endpoints without authentication (should fail)
    const premiumTestsAnonymous = [
        { path: '/premium/dashboard', method: 'GET', name: 'Premium Dashboard (Anonymous)', expectedStatus: 302 },
        { path: '/premium/ai-predictions', method: 'GET', name: 'AI Predictions (Anonymous)', expectedStatus: 302 },
        { path: '/premium/advanced-charts', method: 'GET', name: 'Advanced Charts (Anonymous)', expectedStatus: 302 },
        { path: '/api/premium/alerts', method: 'GET', name: 'Premium Alerts (Anonymous)', expectedStatus: 302 }
    ];
    
    for (const endpoint of premiumTestsAnonymous) {
        await runTest(endpoint);
        await new Promise(resolve => setTimeout(resolve, 50));
    }
    
    // ===== PHASE 2: CREATE AND TEST BASIC USER =====
    console.log('\n💰 PHASE 2: BASIC USER TESTS');
    console.log('=============================');
    
    // Create Basic user
    console.log('Creating Basic user...');
    const createBasicResult = await runTest(
        { path: '/test/create-premium-user', method: 'POST', name: 'Create Basic User', expectedStatus: 200 },
        null,
        { username: 'basic_user', email: 'basic@test.com', password: 'test123', subscription_type: 'basic' }
    );
    
    // Login Basic user
    console.log('Logging in Basic user...');
    const loginBasicResult = await runTest(
        { path: '/test/login-user', method: 'POST', name: 'Login Basic User', expectedStatus: 200 },
        null,
        { username: 'basic_user', password: 'test123' }
    );
    
    const basicSessionCookies = loginBasicResult.sessionCookies;
    
    if (basicSessionCookies && basicSessionCookies.length > 0) {
        console.log('✅ Basic user authenticated, testing premium features...');
        
        // Test current user info
        await runTest(
            { path: '/test/current-user', method: 'GET', name: 'Current User Info (Basic)', expectedStatus: 200 },
            basicSessionCookies
        );
        
        // Test premium endpoints for Basic user
        const basicUserEndpoints = [
            { path: '/premium/dashboard', method: 'GET', name: 'Premium Dashboard (Basic)', expectedStatus: 200 },
            { path: '/premium/ai-predictions', method: 'GET', name: 'AI Predictions (Basic)', expectedStatus: 200 },
            { path: '/premium/advanced-charts', method: 'GET', name: 'Advanced Charts (Basic)', expectedStatus: 200 },
            { path: '/premium/portfolio-optimizer', method: 'GET', name: 'Portfolio Optimizer (Basic)', expectedStatus: 200 },
            { path: '/api/premium/alerts', method: 'GET', name: 'Premium Alerts (Basic)', expectedStatus: 200 },
            { path: '/api/premium/realtime/EQNR.OL', method: 'GET', name: 'Real-time Data (Basic)', expectedStatus: 200 },
            { path: '/api/premium/backtesting', method: 'POST', name: 'Backtesting (Basic)', expectedStatus: 403 } // Should fail - Pro only
        ];
        
        for (const endpoint of basicUserEndpoints) {
            await runTest(endpoint, basicSessionCookies);
            await new Promise(resolve => setTimeout(resolve, 50));
        }
    }
    
    // ===== PHASE 3: CREATE AND TEST PRO USER =====
    console.log('\n🎯 PHASE 3: PRO USER TESTS');
    console.log('===========================');
    
    // Create Pro user
    console.log('Creating Pro user...');
    const createProResult = await runTest(
        { path: '/test/create-premium-user', method: 'POST', name: 'Create Pro User', expectedStatus: 200 },
        null,
        { username: 'pro_user', email: 'pro@test.com', password: 'test123', subscription_type: 'pro' }
    );
    
    // Login Pro user
    console.log('Logging in Pro user...');
    const loginProResult = await runTest(
        { path: '/test/login-user', method: 'POST', name: 'Login Pro User', expectedStatus: 200 },
        null,
        { username: 'pro_user', password: 'test123' }
    );
    
    const proSessionCookies = loginProResult.sessionCookies;
    
    if (proSessionCookies && proSessionCookies.length > 0) {
        console.log('✅ Pro user authenticated, testing all premium features...');
        
        // Test current user info
        await runTest(
            { path: '/test/current-user', method: 'GET', name: 'Current User Info (Pro)', expectedStatus: 200 },
            proSessionCookies
        );
        
        // Test ALL premium endpoints for Pro user
        const proUserEndpoints = [
            { path: '/premium/dashboard', method: 'GET', name: 'Premium Dashboard (Pro)', expectedStatus: 200 },
            { path: '/premium/ai-predictions', method: 'GET', name: 'AI Predictions (Pro)', expectedStatus: 200 },
            { path: '/premium/advanced-charts', method: 'GET', name: 'Advanced Charts (Pro)', expectedStatus: 200 },
            { path: '/premium/portfolio-optimizer', method: 'GET', name: 'Portfolio Optimizer (Pro)', expectedStatus: 200 },
            { path: '/api/premium/alerts', method: 'GET', name: 'Premium Alerts (Pro)', expectedStatus: 200 },
            { path: '/api/premium/realtime/EQNR.OL', method: 'GET', name: 'Real-time Data (Pro)', expectedStatus: 200 },
            { path: '/api/premium/backtesting', method: 'POST', name: 'Backtesting (Pro)', expectedStatus: 200 } // Should work - Pro only
        ];
        
        for (const endpoint of proUserEndpoints) {
            await runTest(endpoint, proSessionCookies);
            await new Promise(resolve => setTimeout(resolve, 50));
        }
    }
    
    // ===== PHASE 4: CREATE AND TEST FREE USER =====
    console.log('\n🆓 PHASE 4: FREE USER TESTS');
    console.log('============================');
    
    // Create Free user (no subscription)
    console.log('Creating Free user...');
    const createFreeResult = await runTest(
        { path: '/test/create-premium-user', method: 'POST', name: 'Create Free User', expectedStatus: 200 },
        null,
        { username: 'free_user', email: 'free@test.com', password: 'test123', subscription_type: 'free' }
    );
    
    // Login Free user
    console.log('Logging in Free user...');
    const loginFreeResult = await runTest(
        { path: '/test/login-user', method: 'POST', name: 'Login Free User', expectedStatus: 200 },
        null,
        { username: 'free_user', password: 'test123' }
    );
    
    const freeSessionCookies = loginFreeResult.sessionCookies;
    
    if (freeSessionCookies && freeSessionCookies.length > 0) {
        console.log('✅ Free user authenticated, testing access restrictions...');
        
        // Test current user info
        await runTest(
            { path: '/test/current-user', method: 'GET', name: 'Current User Info (Free)', expectedStatus: 200 },
            freeSessionCookies
        );
        
        // Test premium endpoints for Free user (should all fail with 403)
        const freeUserEndpoints = [
            { path: '/premium/dashboard', method: 'GET', name: 'Premium Dashboard (Free)', expectedStatus: 302 },
            { path: '/premium/ai-predictions', method: 'GET', name: 'AI Predictions (Free)', expectedStatus: 302 },
            { path: '/premium/advanced-charts', method: 'GET', name: 'Advanced Charts (Free)', expectedStatus: 302 },
            { path: '/premium/portfolio-optimizer', method: 'GET', name: 'Portfolio Optimizer (Free)', expectedStatus: 302 },
            { path: '/api/premium/alerts', method: 'GET', name: 'Premium Alerts (Free)', expectedStatus: 302 },
            { path: '/api/premium/realtime/EQNR.OL', method: 'GET', name: 'Real-time Data (Free)', expectedStatus: 302 },
            { path: '/api/premium/backtesting', method: 'POST', name: 'Backtesting (Free)', expectedStatus: 302 }
        ];
        
        for (const endpoint of freeUserEndpoints) {
            await runTest(endpoint, freeSessionCookies);
            await new Promise(resolve => setTimeout(resolve, 50));
        }
    }
    
    // ===== GENERATE COMPREHENSIVE REPORT =====
    const overallTime = Date.now() - overallStartTime;
    const avgResponseTime = testResults
        .filter(r => r.responseTime)
        .reduce((acc, r) => acc + r.responseTime, 0) / testResults.filter(r => r.responseTime).length;
    
    console.log('\n📋 COMPREHENSIVE FULL-USER TEST REPORT');
    console.log('=======================================');
    console.log(`📊 Total Tests: ${totalTests}`);
    console.log(`✅ Passed: ${passedTests}`);
    console.log(`❌ Failed: ${failedTests}`);
    console.log(`📈 Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
    console.log(`⏱️  Average Response Time: ${avgResponseTime.toFixed(1)}ms`);
    console.log(`🕐 Total Test Time: ${overallTime}ms`);
    
    // Group results by user type
    const groupedResults = {
        anonymous: testResults.filter(r => r.endpoint.includes('(Anonymous)')),
        basic: testResults.filter(r => r.endpoint.includes('(Basic)')),
        pro: testResults.filter(r => r.endpoint.includes('(Pro)')),
        free: testResults.filter(r => r.endpoint.includes('(Free)')),
        system: testResults.filter(r => r.endpoint.includes('Create') || r.endpoint.includes('Login') || r.endpoint.includes('Current User'))
    };
    
    console.log('\n📝 DETAILED RESULTS BY USER TYPE');
    console.log('=================================');
    
    Object.entries(groupedResults).forEach(([userType, results]) => {
        if (results.length > 0) {
            const userPassed = results.filter(r => r.success).length;
            const userTotal = results.length;
            console.log(`\n👤 ${userType.toUpperCase()}: ${userPassed}/${userTotal} passed`);
            
            results.forEach(result => {
                const status = result.success ? '✅' : '❌';
                const time = result.responseTime ? `${result.responseTime}ms` : 'N/A';
                console.log(`   ${status} ${result.endpoint} (${time})`);
            });
        }
    });
    
    // Security and access control assessment
    console.log('\n🔐 SECURITY & ACCESS CONTROL ASSESSMENT');
    console.log('========================================');
    
    const securityTests = {
        anonymous_blocked: testResults.filter(r => 
            r.endpoint.includes('Premium') && r.endpoint.includes('(Anonymous)') && (r.actualStatus === 401 || r.actualStatus === 302)
        ).length,
        free_blocked: testResults.filter(r => 
            r.endpoint.includes('Premium') && r.endpoint.includes('(Free)') && (r.actualStatus === 403 || r.actualStatus === 302)
        ).length,
        basic_access: testResults.filter(r => 
            r.endpoint.includes('Premium') && r.endpoint.includes('(Basic)') && r.actualStatus === 200
        ).length,
        pro_access: testResults.filter(r => 
            r.endpoint.includes('Premium') && r.endpoint.includes('(Pro)') && r.actualStatus === 200
        ).length,
        pro_exclusive: testResults.filter(r => 
            r.endpoint.includes('Backtesting') && r.endpoint.includes('(Pro)') && r.actualStatus === 200
        ).length
    };
    
    console.log(`🚫 Anonymous users blocked from premium: ${securityTests.anonymous_blocked} tests`);
    console.log(`🔒 Free users blocked from premium: ${securityTests.free_blocked} tests`);
    console.log(`💰 Basic users can access premium: ${securityTests.basic_access} tests`);
    console.log(`🎯 Pro users can access all features: ${securityTests.pro_access} tests`);
    console.log(`⭐ Pro-exclusive features working: ${securityTests.pro_exclusive} tests`);
    
    // Final assessment
    const successRate = (passedTests / totalTests) * 100;
    console.log('\n🎯 FINAL ASSESSMENT');
    console.log('===================');
    
    if (successRate >= 95) {
        console.log('🎉 EXCELLENT! All user types and premium features working perfectly!');
        console.log('✅ Anonymous users can access public content');
        console.log('✅ Free users properly blocked from premium');
        console.log('✅ Basic users can access premium features');
        console.log('✅ Pro users can access all features including exclusive ones');
        console.log('✅ Security and access control working correctly');
        console.log('🚀 Ready for production deployment!');
    } else if (successRate >= 85) {
        console.log('✅ GOOD! Most features working, minor issues to address');
    } else {
        console.log('⚠️  NEEDS WORK! Significant issues with user access or premium features');
    }
    
    // Save detailed report
    const detailedReport = {
        summary: {
            totalTests,
            passedTests,
            failedTests,
            successRate,
            avgResponseTime,
            overallTime,
            timestamp: new Date().toISOString()
        },
        results: testResults,
        groupedResults,
        securityAssessment: securityTests
    };
    
    fs.writeFileSync('full_user_test_report.json', JSON.stringify(detailedReport, null, 2));
    console.log('\n💾 Detailed report saved to: full_user_test_report.json');
}

// Run the full test suite
runFullTestSuite().catch(console.error);
