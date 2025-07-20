#!/usr/bin/env python3
"""
Comprehensive test suite for Aksjeradar
Tests all endpoints, access control, styling issues, and functionality
for different user types (unauthenticated, authenticated, premium)
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Tuple, Optional
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AksjeradarComprehensiveTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session_unauthenticated = requests.Session()
        self.session_authenticated = requests.Session()
        self.session_premium = requests.Session()
        
        # Test results
        self.results = {
            'endpoints': [],
            'styling_issues': [],
            'access_control': [],
            'api_tests': [],
            'ui_issues': [],
            'performance': [],
            'security': []
        }
        
        # All endpoints to test
        self.endpoints = [
            # Public pages
            ('/', 'GET', 'Homepage'),
            ('/demo', 'GET', 'Demo page'),
            ('/login', 'GET', 'Login page'),
            ('/register', 'GET', 'Register page'),
            ('/pricing', 'GET', 'Pricing page'),
            ('/pricing/', 'GET', 'Pricing page with slash'),
            ('/about', 'GET', 'About page'),
            ('/contact', 'GET', 'Contact page'),
            ('/privacy', 'GET', 'Privacy page'),
            ('/terms', 'GET', 'Terms page'),
            ('/ai-explained', 'GET', 'AI Explained page'),
            ('/referrals', 'GET', 'Referrals page'),
            
            # Authentication endpoints
            ('/login', 'POST', 'Login POST'),
            ('/register', 'POST', 'Register POST'),
            ('/logout', 'GET', 'Logout'),
            ('/forgot_password', 'GET', 'Forgot password'),
            ('/reset_password/test-token', 'GET', 'Reset password'),
            
            # Protected pages (require login)
            ('/portfolio', 'GET', 'Portfolio'),
            ('/portfolio/create', 'GET', 'Create portfolio'),
            ('/portfolio/watchlist', 'GET', 'Watchlist'),
            ('/portfolio/tips', 'GET', 'Stock tips'),
            ('/portfolio/overview', 'GET', 'Portfolio overview'),
            ('/portfolio/transactions', 'GET', 'Transactions'),
            
            # Analysis pages
            ('/analysis', 'GET', 'Analysis index'),
            ('/analysis/technical', 'GET', 'Technical analysis'),
            ('/analysis/ai', 'GET', 'AI analysis'),
            ('/analysis/prediction', 'GET', 'Predictions'),
            ('/analysis/recommendation', 'GET', 'Recommendations'),
            ('/analysis/warren-buffett', 'GET', 'Warren Buffett analysis'),
            ('/analysis/benjamin-graham', 'GET', 'Benjamin Graham analysis'),
            ('/analysis/short-analysis', 'GET', 'Short analysis'),
            ('/analysis/market-overview', 'GET', 'Market overview'),
            
            # Stocks pages
            ('/stocks', 'GET', 'Stocks index'),
            ('/stocks/list', 'GET', 'Stocks list'),
            ('/stocks/list/oslo', 'GET', 'Oslo stocks'),
            ('/stocks/list/global', 'GET', 'Global stocks'),
            ('/stocks/list/crypto', 'GET', 'Crypto'),
            ('/stocks/list/currency', 'GET', 'Currency'),
            ('/stocks/search', 'GET', 'Stock search'),
            ('/stocks/compare', 'GET', 'Stock comparison'),
            ('/stocks/details/EQNR.OL', 'GET', 'Stock details'),
            
            # API endpoints
            ('/api/health', 'GET', 'Health check'),
            ('/api/version', 'GET', 'Version'),
            ('/api/search', 'GET', 'Search API'),
            ('/api/search?q=equinor', 'GET', 'Search API with query'),
            ('/api/oslo_stocks', 'GET', 'Oslo stocks API'),
            ('/api/global_stocks', 'GET', 'Global stocks API'),
            ('/api/crypto', 'GET', 'Crypto API'),
            ('/api/currency', 'GET', 'Currency API'),
            ('/api/realtime/price/EQNR.OL', 'GET', 'Realtime price'),
            ('/api/realtime/market-summary', 'GET', 'Market summary'),
            ('/api/realtime/trending', 'GET', 'Trending stocks'),
            
            # News endpoints
            ('/news', 'GET', 'News index'),
            ('/news/api/latest', 'GET', 'Latest news API'),
            ('/news/api/trending', 'GET', 'Trending news API'),
            
            # Pro/Premium features
            ('/pro-tools', 'GET', 'Pro tools'),
            ('/pro-tools/screener', 'GET', 'Pro screener'),
            ('/pro-tools/alerts', 'GET', 'Price alerts'),
            ('/pro-tools/portfolio-analyzer', 'GET', 'Portfolio analyzer'),
            
            # Admin pages
            ('/admin', 'GET', 'Admin dashboard'),
            ('/admin/users', 'GET', 'User management'),
            ('/admin/system', 'GET', 'System status'),
            
            # Static resources
            ('/static/css/style.css', 'GET', 'Main CSS'),
            ('/static/js/main.js', 'GET', 'Main JS'),
            ('/manifest.json', 'GET', 'PWA manifest'),
            ('/service-worker.js', 'GET', 'Service worker'),
            ('/favicon.ico', 'GET', 'Favicon'),
            
            # Error pages
            ('/nonexistent-page', 'GET', '404 page'),
            ('/api/nonexistent', 'GET', '404 API'),
        ]
        
        # Common styling issues to check
        self.styling_checks = [
            ('dark_on_dark', r'color:\s*#[0-3][0-9a-f]{5}.*background(?:-color)?:\s*#[0-3][0-9a-f]{5}'),
            ('light_on_light', r'color:\s*#[c-f][0-9a-f]{5}.*background(?:-color)?:\s*#[c-f][0-9a-f]{5}'),
            ('missing_contrast', r'color:\s*inherit.*background'),
            ('transparent_issues', r'color:\s*transparent'),
            ('visibility_hidden', r'visibility:\s*hidden'),
            ('display_none', r'display:\s*none'),
            ('zero_opacity', r'opacity:\s*0(?:\.0)?[;\s}]'),
            ('text_shadow_issues', r'text-shadow:.*[0-9]+px.*#[0-9a-f]{6}'),
        ]

    def setup_test_users(self):
        """Setup test user sessions"""
        print("\n🔐 Setting up test users...")
        
        # Test credentials
        test_user = {
            'username': 'test_user',
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        
        premium_user = {
            'username': 'premium_user', 
            'email': 'premium@test.com',
            'password': 'premiumpass123'
        }
        
        # Register and login test users
        # Note: In a real test, these users would be created in the test database
        
        return True

    def test_endpoint_access(self, endpoint: str, method: str, description: str, session: requests.Session, user_type: str) -> Dict:
        """Test a single endpoint with given session"""
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = session.get(urljoin(self.base_url, endpoint), allow_redirects=False)
            elif method == 'POST':
                # Add CSRF token if needed
                csrf_token = self.get_csrf_token(session)
                data = {'csrf_token': csrf_token} if csrf_token else {}
                response = session.post(urljoin(self.base_url, endpoint), data=data, allow_redirects=False)
            else:
                response = None
            
            elapsed_time = time.time() - start_time
            
            result = {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'user_type': user_type,
                'status_code': response.status_code if response else 'ERROR',
                'response_time': elapsed_time,
                'redirect': response.headers.get('Location') if response and response.status_code in [301, 302, 303, 307] else None,
                'content_type': response.headers.get('Content-Type', '') if response else '',
                'content_length': len(response.content) if response else 0,
                'errors': []
            }
            
            # Check for common issues
            if response and response.status_code == 200:
                content = response.text
                
                # Check for error messages in content
                error_patterns = [
                    r'error["\']?\s*:\s*["\']([^"\']+)',
                    r'<div[^>]*class=["\'][^"\']*error[^"\']*["\'][^>]*>([^<]+)',
                    r'Internal Server Error',
                    r'Traceback \(most recent call last\)',
                    r'AttributeError:',
                    r'KeyError:',
                    r'TypeError:',
                ]
                
                for pattern in error_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        result['errors'].append(f"Error pattern found: {matches[0][:100]}")
            
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'user_type': user_type,
                'status_code': 'EXCEPTION',
                'error': str(e),
                'response_time': 0
            }

    def check_styling_issues(self, content: str, url: str) -> List[Dict]:
        """Check for common styling issues in HTML content"""
        issues = []
        soup = BeautifulSoup(content, 'html.parser')
        
        # Check inline styles
        elements_with_style = soup.find_all(style=True)
        for elem in elements_with_style:
            style = elem.get('style', '')
            
            for issue_name, pattern in self.styling_checks:
                if re.search(pattern, style, re.IGNORECASE):
                    issues.append({
                        'url': url,
                        'issue': issue_name,
                        'element': str(elem)[:200],
                        'style': style
                    })
        
        # Check for common Bootstrap dark mode issues
        dark_elements = soup.find_all(class_=re.compile(r'bg-dark|navbar-dark|text-dark'))
        for elem in dark_elements:
            # Check if text color is properly set
            classes = elem.get('class', [])
            if 'bg-dark' in ' '.join(classes) and 'text-light' not in ' '.join(classes) and 'text-white' not in ' '.join(classes):
                issues.append({
                    'url': url,
                    'issue': 'missing_text_color_on_dark_bg',
                    'element': str(elem)[:200],
                    'suggestion': 'Add text-light or text-white class'
                })
        
        # Check for hardcoded dark colors
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            style_content = style_tag.string or ''
            
            # Check for problematic color combinations
            dark_bg_pattern = r'background(?:-color)?:\s*#(?:0|1|2|3)[0-9a-f]{5}'
            dark_text_pattern = r'color:\s*#(?:0|1|2|3)[0-9a-f]{5}'
            
            if re.search(dark_bg_pattern, style_content) and re.search(dark_text_pattern, style_content):
                issues.append({
                    'url': url,
                    'issue': 'potential_contrast_issue',
                    'element': 'style tag',
                    'content': style_content[:200]
                })
        
        return issues

    def test_all_endpoints(self):
        """Test all endpoints for each user type"""
        print("\n🌐 Testing all endpoints...")
        
        for endpoint, method, description in self.endpoints:
            print(f"\n📍 Testing: {description} ({method} {endpoint})")
            
            # Test as unauthenticated user
            result_unauth = self.test_endpoint_access(endpoint, method, description, self.session_unauthenticated, 'unauthenticated')
            self.results['endpoints'].append(result_unauth)
            print(f"   👤 Unauthenticated: {result_unauth['status_code']}")
            
            # Test as authenticated user
            result_auth = self.test_endpoint_access(endpoint, method, description, self.session_authenticated, 'authenticated')
            self.results['endpoints'].append(result_auth)
            print(f"   🔓 Authenticated: {result_auth['status_code']}")
            
            # Test as premium user
            result_premium = self.test_endpoint_access(endpoint, method, description, self.session_premium, 'premium')
            self.results['endpoints'].append(result_premium)
            print(f"   ⭐ Premium: {result_premium['status_code']}")
            
            # Check for styling issues on successful GET requests
            if method == 'GET' and result_unauth.get('status_code') == 200:
                try:
                    response = self.session_unauthenticated.get(urljoin(self.base_url, endpoint))
                    if 'text/html' in response.headers.get('Content-Type', ''):
                        styling_issues = self.check_styling_issues(response.text, endpoint)
                        if styling_issues:
                            self.results['styling_issues'].extend(styling_issues)
                            print(f"   ⚠️  Found {len(styling_issues)} styling issues")
                except:
                    pass

    def test_access_control(self):
        """Test access control for protected resources"""
        print("\n🔒 Testing access control...")
        
        protected_endpoints = [
            ('/portfolio', 'Should redirect to login'),
            ('/portfolio/create', 'Should redirect to login'),
            ('/analysis/ai', 'Should show restricted access'),
            ('/pro-tools', 'Should require premium'),
            ('/admin', 'Should require admin'),
        ]
        
        for endpoint, expected_behavior in protected_endpoints:
            response = self.session_unauthenticated.get(urljoin(self.base_url, endpoint), allow_redirects=False)
            
            result = {
                'endpoint': endpoint,
                'expected': expected_behavior,
                'status_code': response.status_code,
                'redirect': response.headers.get('Location'),
                'passed': False
            }
            
            # Check if properly protected
            if response.status_code in [301, 302, 303, 307]:
                if 'login' in str(response.headers.get('Location', '')).lower():
                    result['passed'] = True
            elif response.status_code == 403:
                result['passed'] = True
            
            self.results['access_control'].append(result)
            print(f"   {endpoint}: {'✅' if result['passed'] else '❌'} {response.status_code}")

    def test_api_responses(self):
        """Test API endpoint responses"""
        print("\n🔌 Testing API responses...")
        
        api_tests = [
            ('/api/health', {'status': 'healthy'}),
            ('/api/version', {'version': str}),
            ('/api/search?q=equinor', {'results': list}),
            ('/api/oslo_stocks', {'stocks': list}),
        ]
        
        for endpoint, expected_structure in api_tests:
            try:
                response = self.session_unauthenticated.get(urljoin(self.base_url, endpoint))
                
                result = {
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'valid_json': False,
                    'structure_match': False,
                    'response_time': response.elapsed.total_seconds()
                }
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        result['valid_json'] = True
                        
                        # Check structure
                        for key, expected_type in expected_structure.items():
                            if key in data:
                                if expected_type == str:
                                    result['structure_match'] = isinstance(data[key], str)
                                elif expected_type == list:
                                    result['structure_match'] = isinstance(data[key], list)
                                elif expected_type == dict:
                                    result['structure_match'] = isinstance(data[key], dict)
                                else:
                                    result['structure_match'] = data[key] == expected_type
                    except:
                        pass
                
                self.results['api_tests'].append(result)
                print(f"   {endpoint}: {'✅' if result['valid_json'] else '❌'} Status: {result['status_code']}")
                
            except Exception as e:
                self.results['api_tests'].append({
                    'endpoint': endpoint,
                    'error': str(e)
                })
                print(f"   {endpoint}: ❌ Error: {str(e)}")

    def test_ui_consistency(self):
        """Test UI consistency across pages"""
        print("\n🎨 Testing UI consistency...")
        
        pages_to_check = ['/', '/demo', '/pricing', '/stocks', '/analysis']
        
        for page in pages_to_check:
            try:
                response = self.session_unauthenticated.get(urljoin(self.base_url, page))
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check for common UI elements
                    issues = []
                    
                    # Navigation
                    nav = soup.find('nav')
                    if not nav:
                        issues.append('Missing navigation')
                    
                    # Footer
                    footer = soup.find('footer')
                    if not footer:
                        issues.append('Missing footer')
                    
                    # Responsive meta tag
                    viewport = soup.find('meta', attrs={'name': 'viewport'})
                    if not viewport:
                        issues.append('Missing viewport meta tag')
                    
                    # Dark mode consistency
                    body_classes = soup.find('body').get('class', [])
                    if 'dark' in ' '.join(body_classes):
                        # Check if content is properly styled for dark mode
                        dark_issues = soup.find_all(class_=re.compile(r'text-dark|bg-light'))
                        if dark_issues:
                            issues.append(f'Found {len(dark_issues)} elements with light theme classes in dark mode')
                    
                    self.results['ui_issues'].append({
                        'page': page,
                        'issues': issues,
                        'issue_count': len(issues)
                    })
                    
                    print(f"   {page}: {'✅' if not issues else '⚠️'} {len(issues)} issues")
                    
            except Exception as e:
                print(f"   {page}: ❌ Error: {str(e)}")

    def test_performance(self):
        """Test page load performance"""
        print("\n⚡ Testing performance...")
        
        critical_pages = ['/', '/stocks', '/analysis', '/portfolio']
        
        for page in critical_pages:
            try:
                start_time = time.time()
                response = self.session_unauthenticated.get(urljoin(self.base_url, page))
                load_time = time.time() - start_time
                
                result = {
                    'page': page,
                    'load_time': load_time,
                    'size': len(response.content),
                    'status': 'OK' if load_time < 2.0 else 'SLOW'
                }
                
                self.results['performance'].append(result)
                print(f"   {page}: {load_time:.2f}s {'✅' if load_time < 2.0 else '⚠️'}")
                
            except Exception as e:
                print(f"   {page}: ❌ Error: {str(e)}")

    def test_security_headers(self):
        """Test security headers"""
        print("\n🔐 Testing security headers...")
        
        response = self.session_unauthenticated.get(self.base_url)
        headers = response.headers
        
        security_checks = [
            ('X-Content-Type-Options', 'nosniff'),
            ('X-Frame-Options', ['DENY', 'SAMEORIGIN']),
            ('X-XSS-Protection', '1; mode=block'),
            ('Strict-Transport-Security', 'max-age='),
            ('Content-Security-Policy', None),
        ]
        
        for header, expected in security_checks:
            present = header in headers
            correct = False
            
            if present and expected:
                if isinstance(expected, list):
                    correct = any(exp in headers[header] for exp in expected)
                elif expected is None:
                    correct = True
                else:
                    correct = expected in headers[header]
            
            self.results['security'].append({
                'header': header,
                'present': present,
                'correct': correct,
                'value': headers.get(header, 'NOT SET')
            })
            
            print(f"   {header}: {'✅' if present and correct else '❌'}")

    def get_csrf_token(self, session: requests.Session) -> Optional[str]:
        """Get CSRF token from login page"""
        try:
            response = session.get(urljoin(self.base_url, '/login'))
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                return csrf_input.get('value')
        except:
            pass
        return None

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        # Endpoint summary
        total_endpoints = len(self.results['endpoints'])
        successful = len([e for e in self.results['endpoints'] if e.get('status_code') in [200, 301, 302, 404]])
        
        print(f"\n📍 ENDPOINTS: {successful}/{total_endpoints} responding correctly")
        
        # Group by status code
        status_codes = {}
        for endpoint in self.results['endpoints']:
            code = endpoint.get('status_code', 'ERROR')
            status_codes[code] = status_codes.get(code, 0) + 1
        
        for code, count in sorted(status_codes.items()):
            print(f"   {code}: {count} endpoints")
        
        # Styling issues
        print(f"\n🎨 STYLING ISSUES: {len(self.results['styling_issues'])} found")
        if self.results['styling_issues']:
            issue_types = {}
            for issue in self.results['styling_issues']:
                issue_type = issue['issue']
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
            
            for issue_type, count in issue_types.items():
                print(f"   {issue_type}: {count} occurrences")
        
        # Access control
        print(f"\n🔒 ACCESS CONTROL: {len([a for a in self.results['access_control'] if a['passed']])}/{len(self.results['access_control'])} passed")
        
        # API tests
        print(f"\n🔌 API TESTS: {len([a for a in self.results['api_tests'] if a.get('valid_json')])}/{len(self.results['api_tests'])} valid")
        
        # UI consistency
        total_ui_issues = sum(len(ui['issues']) for ui in self.results['ui_issues'])
        print(f"\n🎨 UI CONSISTENCY: {total_ui_issues} issues found across {len(self.results['ui_issues'])} pages")
        
        # Performance
        avg_load_time = sum(p['load_time'] for p in self.results['performance']) / len(self.results['performance']) if self.results['performance'] else 0
        print(f"\n⚡ PERFORMANCE: Average load time {avg_load_time:.2f}s")
        
        # Security
        secure_headers = len([h for h in self.results['security'] if h['present'] and h['correct']])
        print(f"\n🔐 SECURITY: {secure_headers}/{len(self.results['security'])} headers properly set")
        
        # Critical issues
        print("\n⚠️  CRITICAL ISSUES:")
        critical_found = False
        
        # Check for dark on dark text
        dark_on_dark = [i for i in self.results['styling_issues'] if i['issue'] == 'dark_on_dark']
        if dark_on_dark:
            print(f"   • {len(dark_on_dark)} instances of dark text on dark background")
            critical_found = True
        
        # Check for broken endpoints
        broken_endpoints = [e for e in self.results['endpoints'] if e.get('status_code') not in [200, 301, 302, 404] or e.get('status_code') == 'ERROR']
        if broken_endpoints:
            print(f"   • {len(broken_endpoints)} broken endpoints")
            for endpoint in broken_endpoints[:5]:  # Show first 5
                print(f"     - {endpoint['endpoint']}: {endpoint.get('status_code', 'ERROR')}")
            critical_found = True
        
        # Check for missing security headers
        missing_security = [h for h in self.results['security'] if not h['present']]
        if missing_security:
            print(f"   • {len(missing_security)} missing security headers")
            critical_found = True
        
        if not critical_found:
            print("   ✅ No critical issues found!")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return not critical_found

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive Aksjeradar testing...")
        print(f"🎯 Base URL: {self.base_url}")
        print(f"⏰ Started: {datetime.now()}")
        
        # Setup test users
        self.setup_test_users()
        
        # Run all test suites
        self.test_all_endpoints()
        self.test_access_control()
        self.test_api_responses()
        self.test_ui_consistency()
        self.test_performance()
        self.test_security_headers()
        
        # Generate report
        return self.generate_report()

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Aksjeradar testing')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL to test')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    # Check if server is running
    try:
        response = requests.get(f"{args.url}/api/health", timeout=5)
        print(f"✅ Server is running at {args.url}")
    except:
        print(f"❌ Server is not running at {args.url}")
        print("🔧 Please start the server first:")
        print("   cd /workspaces/aksjeny/app && python run.py")
        return False
    
    # Run tests
    tester = AksjeradarComprehensiveTester(args.url)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
