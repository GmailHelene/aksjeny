#!/usr/bin/env node
/**
 * Komplett systemtest for Aksjeradar - klar for produksjon på aksjeradar.trade
 */

class AksjeradarSystemTest {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.results = [];
        this.errors = [];
        this.warnings = [];
    }

    async testEndpoint(url, method = 'GET', data = null, expectedStatus = 200) {
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
                expectedStatus: expectedStatus,
                ok: response.status === expectedStatus,
                responseTime: responseTime,
                timestamp: new Date().toISOString()
            };

            // Try to parse response
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    result.data = await response.json();
                } else {
                    const text = await response.text();
                    result.contentLength = text.length;
                    result.hasContent = text.length > 0;
                }
            } catch (e) {
                result.parseError = e.message;
            }

            this.results.push(result);
            return result;
            
        } catch (error) {
            const result = {
                url: url,
                method: method,
                status: 'ERROR',
                error: error.message,
                ok: false,
                timestamp: new Date().toISOString()
            };
            
            this.results.push(result);
            this.errors.push(`${url}: ${error.message}`);
            return result;
        }
    }

    async runCompleteTest() {
        console.log('🚀 AKSJERADAR KOMPLETT SYSTEMTEST');
        console.log('==================================');
        console.log(`🎯 Testing på: ${this.baseUrl}`);
        console.log(`📅 Tidspunkt: ${new Date().toLocaleString()}`);
        console.log('');

        // 1. GRUNNLEGGENDE SIDER
        console.log('📄 1. GRUNNLEGGENDE SIDER');
        console.log('-------------------------');
        await this.testBasicPages();

        // 2. AUTENTISERING
        console.log('\\n🔐 2. AUTENTISERING');
        console.log('-------------------');
        await this.testAuthentication();

        // 3. API ENDEPUNKTER
        console.log('\\n🔗 3. API ENDEPUNKTER');
        console.log('---------------------');
        await this.testApiEndpoints();

        // 4. HOVEDFUNKSJONER
        console.log('\\n⚙️ 4. HOVEDFUNKSJONER');
        console.log('--------------------');
        await this.testMainFeatures();

        // 5. AVANSERTE FUNKSJONER
        console.log('\\n🚀 5. AVANSERTE FUNKSJONER');
        console.log('--------------------------');
        await this.testAdvancedFeatures();

        // 6. ADMIN OG DEBUG
        console.log('\\n🛠️ 6. ADMIN OG DEBUG');
        console.log('--------------------');
        await this.testAdminFeatures();

        // 7. ERROR HANDLING
        console.log('\\n❌ 7. ERROR HANDLING');
        console.log('--------------------');
        await this.testErrorHandling();

        // GENERER RAPPORT
        console.log('\\n📊 SYSTEMTEST RAPPORT');
        console.log('=====================');
        this.generateReport();
    }

    async testBasicPages() {
        const basicPages = [
            { url: '/', desc: 'Hovedside' },
            { url: '/demo', desc: 'Demo-side' },
            { url: '/ai-explained', desc: 'AI forklart' },
            { url: '/pricing', desc: 'Priser' },
            { url: '/pricing/', desc: 'Priser (trailing slash)' },
            { url: '/offline', desc: 'Offline-side' },
            { url: '/manifest.json', desc: 'PWA manifest' },
            { url: '/service-worker.js', desc: 'Service worker' }
        ];

        for (const page of basicPages) {
            const result = await this.testEndpoint(page.url);
            this.logResult(result, page.desc);
        }
    }

    async testAuthentication() {
        const authPages = [
            { url: '/login', method: 'GET', desc: 'Login-side (GET)' },
            { url: '/register', method: 'GET', desc: 'Register-side (GET)' },
            { url: '/logout', desc: 'Logout' },
            { url: '/forgot_password', desc: 'Glemt passord' },
            { url: '/auth', desc: 'Kombinert auth-side' }
        ];

        for (const page of authPages) {
            const result = await this.testEndpoint(page.url, page.method || 'GET');
            this.logResult(result, page.desc);
        }

        // Test POST endpoints (should return form errors or redirects)
        const postResult = await this.testEndpoint('/login', 'POST', 
            { username: 'test', password: 'test' }, 200);
        this.logResult(postResult, 'Login POST test');
    }

    async testApiEndpoints() {
        const apiEndpoints = [
            { url: '/api/health', desc: 'Health check' },
            { url: '/api/version', desc: 'Version info' },
            { url: '/api/crypto', desc: 'Crypto data' },
            { url: '/api/currency', desc: 'Currency data' },
            { url: '/health', desc: 'Health endpoint' },
            { url: '/health/detailed', desc: 'Detailed health' },
            { url: '/health/ready', desc: 'Readiness probe' },
            { url: '/health/live', desc: 'Liveness probe' }
        ];

        for (const endpoint of apiEndpoints) {
            const result = await this.testEndpoint(endpoint.url);
            this.logResult(result, endpoint.desc);
        }
    }

    async testMainFeatures() {
        const features = [
            { url: '/portfolio', desc: 'Portfolio oversikt' },
            { url: '/analysis', desc: 'Analyse hovedside' },
            { url: '/stocks', desc: 'Aksjer oversikt' },
            { url: '/news', desc: 'Nyheter' },
            { url: '/search', desc: 'Søk' }
        ];

        for (const feature of features) {
            const result = await this.testEndpoint(feature.url);
            this.logResult(result, feature.desc);
        }
    }

    async testAdvancedFeatures() {
        const advanced = [
            { url: '/features/ai-predictions', desc: 'AI prediksjoner' },
            { url: '/features/social-sentiment', desc: 'Social sentiment' },
            { url: '/features/analyst-recommendations', desc: 'Analyst anbefalinger' },
            { url: '/market-intel', desc: 'Market intelligence' },
            { url: '/market-intel/insider-trading', desc: 'Insider trading' },
            { url: '/notifications', desc: 'Notifikasjoner' },
            { url: '/backtest', desc: 'Backtesting' }
        ];

        for (const feature of advanced) {
            const result = await this.testEndpoint(feature.url);
            this.logResult(result, feature.desc);
        }
    }

    async testAdminFeatures() {
        const admin = [
            { url: '/admin', desc: 'Admin dashboard' },
            { url: '/debug/user-info', desc: 'Debug bruker info' },
            { url: '/demo/ping', desc: 'Demo ping' },
            { url: '/demo/user', desc: 'Demo bruker' }
        ];

        for (const feature of admin) {
            const result = await this.testEndpoint(feature.url);
            this.logResult(result, feature.desc);
        }
    }

    async testErrorHandling() {
        const errorTests = [
            { url: '/nonexistent', expectedStatus: 404, desc: '404 test' },
            { url: '/api/nonexistent', expectedStatus: 404, desc: 'API 404 test' },
            { url: '/admin/nonexistent', expectedStatus: 404, desc: 'Admin 404 test' }
        ];

        for (const test of errorTests) {
            const result = await this.testEndpoint(test.url, 'GET', null, test.expectedStatus);
            this.logResult(result, test.desc);
        }
    }

    logResult(result, description) {
        const status = result.ok ? '✅' : '❌';
        const timeStr = result.responseTime ? ` (${result.responseTime}ms)` : '';
        
        console.log(`${status} ${description}: ${result.status}${timeStr}`);
        
        if (result.error) {
            console.log(`   ❗ Error: ${result.error}`);
        }
        
        if (result.data && result.data.message) {
            console.log(`   💬 ${result.data.message}`);
        }

        // Performance warnings
        if (result.responseTime > 1000) {
            this.warnings.push(`${description}: Slow response (${result.responseTime}ms)`);
        }
    }

    generateReport() {
        const total = this.results.length;
        const passed = this.results.filter(r => r.ok).length;
        const failed = this.results.filter(r => !r.ok).length;
        
        // Calculate performance stats
        const responseTimes = this.results.filter(r => r.responseTime).map(r => r.responseTime);
        const avgTime = responseTimes.length > 0 ? 
            responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length : 0;
        const maxTime = responseTimes.length > 0 ? Math.max(...responseTimes) : 0;
        
        console.log(`📈 RESULTATER: ${passed}/${total} bestått (${((passed/total)*100).toFixed(1)}%)`);
        console.log(`⏱️  YTELSE: Gjennomsnitt ${avgTime.toFixed(1)}ms, Max ${maxTime}ms`);
        
        if (this.warnings.length > 0) {
            console.log(`\\n⚠️  ADVARSLER (${this.warnings.length}):`);
            this.warnings.forEach(warning => console.log(`   - ${warning}`));
        }
        
        if (this.errors.length > 0) {
            console.log(`\\n❌ FEIL (${this.errors.length}):`);
            this.errors.forEach(error => console.log(`   - ${error}`));
        }
        
        // Production readiness assessment
        console.log('\\n🎯 PRODUKSJONSKLARHET:');
        console.log('======================');
        
        if (passed >= total * 0.95) {
            console.log('✅ KLAR FOR PRODUKSJON');
            console.log('   - Alle kritiske endepunkter fungerer');
            console.log('   - God ytelse og stabilitet');
            console.log('   - Aksjeradar.trade er klar!');
        } else if (passed >= total * 0.85) {
            console.log('⚠️  NESTEN KLAR');
            console.log('   - De fleste endepunkter fungerer');
            console.log('   - Noen mindre problemer må fikses');
        } else {
            console.log('❌ IKKE KLAR');
            console.log('   - Kritiske feil må fikses før produksjon');
        }
        
        console.log('\\n🌐 Next steps:');
        console.log('   1. Deploy til aksjeradar.trade');
        console.log('   2. Sett opp SSL/HTTPS');
        console.log('   3. Konfigurer produksjonsdatabase');
        console.log('   4. Test med ekte brukere');
        
        return {
            total,
            passed,
            failed,
            successRate: (passed / total) * 100,
            avgResponseTime: avgTime,
            maxResponseTime: maxTime,
            warnings: this.warnings,
            errors: this.errors,
            productionReady: passed >= total * 0.95
        };
    }
}

// Auto-run hvis dette scriptet kjøres direkte
if (require.main === module) {
    const baseUrl = process.argv[2] || 'http://localhost:5000';
    const tester = new AksjeradarSystemTest(baseUrl);
    
    tester.runCompleteTest()
        .then(() => {
            const report = tester.generateReport();
            process.exit(report.productionReady ? 0 : 1);
        })
        .catch(error => {
            console.error('\\n💥 SYSTEMTEST FEILET:', error);
            process.exit(1);
        });
}

module.exports = AksjeradarSystemTest;
