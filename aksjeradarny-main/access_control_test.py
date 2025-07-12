#!/usr/bin/env python3
"""
Access Control and Demo Logic Testing for Aksjeradar
Tests redirect/demo logic and access control decorators
"""

import requests
import sys
import json
import time
from urllib.parse import urljoin
from typing import List, Dict, Tuple
import re

class AccessControlTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Aksjeradar-AccessControl-Tester/1.0'
        })
        self.results = []
        
    def test_endpoint_access_control(self, endpoint: str, 
                                   description: str = "",
                                   should_require_auth: bool = True,
                                   should_allow_demo: bool = True,
                                   should_allow_trial: bool = True) -> Dict:
        """Test access control for a specific endpoint"""
        
        print(f"🔐 Testing access control for: {endpoint}")
        if description:
            print(f"    📝 {description}")
            
        results = {
            'endpoint': endpoint,
            'description': description,
            'should_require_auth': should_require_auth,
            'should_allow_demo': should_allow_demo,
            'should_allow_trial': should_allow_trial,
            'tests': {}
        }
        
        # Test 1: No authentication
        print("    🚫 Testing without authentication...")
        no_auth_result = self.test_no_auth_access(endpoint)
        results['tests']['no_auth'] = no_auth_result
        
        # Test 2: Demo user access
        if should_allow_demo:
            print("    🎭 Testing demo user access...")
            demo_result = self.test_demo_user_access(endpoint)
            results['tests']['demo_user'] = demo_result
        
        # Test 3: Trial user access
        if should_allow_trial:
            print("    ⏱️ Testing trial user access...")
            trial_result = self.test_trial_user_access(endpoint)
            results['tests']['trial_user'] = trial_result
            
        # Test 4: Expired trial user access
        print("    ⏰ Testing expired trial user access...")
        expired_trial_result = self.test_expired_trial_access(endpoint)
        results['tests']['expired_trial'] = expired_trial_result
        
        # Test 5: Premium user access
        print("    💎 Testing premium user access...")
        premium_result = self.test_premium_user_access(endpoint)
        results['tests']['premium_user'] = premium_result
        
        # Analyze results
        results['analysis'] = self.analyze_access_control_results(results)
        
        self.results.append(results)
        return results
        
    def test_no_auth_access(self, endpoint: str) -> Dict:
        """Test access without authentication"""
        try:
            response = self.session.get(
                urljoin(self.base_url, endpoint),
                allow_redirects=False,
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'redirected': response.status_code in [301, 302, 303, 307, 308],
                'redirect_location': response.headers.get('Location', ''),
                'has_login_redirect': '/login' in response.headers.get('Location', ''),
                'content_snippet': response.text[:200] if response.text else '',
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'status_code': None,
                'redirected': False,
                'success': False,
                'error': str(e)
            }
            
    def test_demo_user_access(self, endpoint: str) -> Dict:
        """Test access with demo user simulation"""
        # Try various methods to simulate demo user
        test_methods = [
            # Method 1: Session-based demo flag
            {'cookies': {'demo_user': 'true'}},
            # Method 2: Header-based demo flag
            {'headers': {'X-Demo-User': 'true'}},
            # Method 3: URL parameter
            {'params': {'demo': '1'}},
            # Method 4: Demo user credentials (if we know them)
            {'auth': ('demo@aksjeradar.no', 'demo123')},
        ]
        
        best_result = None
        
        for method in test_methods:
            try:
                kwargs = {
                    'url': urljoin(self.base_url, endpoint),
                    'allow_redirects': True,
                    'timeout': 10
                }
                kwargs.update(method)
                
                response = self.session.get(**kwargs)
                
                result = {
                    'method': str(method),
                    'status_code': response.status_code,
                    'final_url': response.url,
                    'redirected': len(response.history) > 0,
                    'content_snippet': response.text[:200] if response.text else '',
                    'has_demo_indicators': self.check_for_demo_indicators(response.text),
                    'has_restriction_message': self.check_for_restriction_message(response.text),
                    'success': True,
                    'error': None
                }
                
                # Choose the best result (200 status with demo indicators)
                if (result['status_code'] == 200 and 
                    result['has_demo_indicators'] and 
                    not result['has_restriction_message']):
                    best_result = result
                    break
                elif not best_result or result['status_code'] == 200:
                    best_result = result
                    
            except Exception as e:
                result = {
                    'method': str(method),
                    'success': False,
                    'error': str(e)
                }
                if not best_result:
                    best_result = result
                    
        return best_result or {'success': False, 'error': 'No methods worked'}
        
    def test_trial_user_access(self, endpoint: str) -> Dict:
        """Test access with trial user simulation"""
        try:
            # Simulate trial user with session/cookies
            response = self.session.get(
                urljoin(self.base_url, endpoint),
                cookies={'trial_user': 'true', 'trial_start': str(int(time.time()))},
                headers={'X-Trial-User': 'true'},
                allow_redirects=True,
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'final_url': response.url,
                'redirected': len(response.history) > 0,
                'content_snippet': response.text[:200] if response.text else '',
                'has_trial_indicators': self.check_for_trial_indicators(response.text),
                'has_restriction_message': self.check_for_restriction_message(response.text),
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def test_expired_trial_access(self, endpoint: str) -> Dict:
        """Test access with expired trial user simulation"""
        try:
            # Simulate expired trial (30 days ago)
            expired_timestamp = int(time.time()) - (30 * 24 * 60 * 60)
            
            response = self.session.get(
                urljoin(self.base_url, endpoint),
                cookies={
                    'trial_user': 'true', 
                    'trial_start': str(expired_timestamp),
                    'trial_expired': 'true'
                },
                headers={'X-Trial-User': 'expired'},
                allow_redirects=True,
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'final_url': response.url,
                'redirected': len(response.history) > 0,
                'content_snippet': response.text[:200] if response.text else '',
                'has_upgrade_prompt': self.check_for_upgrade_prompt(response.text),
                'has_restriction_message': self.check_for_restriction_message(response.text),
                'blocked_access': response.status_code == 403 or '/pricing' in response.url,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def test_premium_user_access(self, endpoint: str) -> Dict:
        """Test access with premium user simulation"""
        try:
            response = self.session.get(
                urljoin(self.base_url, endpoint),
                cookies={'premium_user': 'true', 'subscription': 'active'},
                headers={'X-Premium-User': 'true'},
                allow_redirects=True,
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'final_url': response.url,
                'redirected': len(response.history) > 0,
                'content_snippet': response.text[:200] if response.text else '',
                'has_full_access': response.status_code == 200 and '/pricing' not in response.url,
                'has_premium_features': self.check_for_premium_features(response.text),
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def check_for_demo_indicators(self, content: str) -> bool:
        """Check if content indicates demo mode"""
        if not content:
            return False
            
        demo_indicators = [
            'demo', 'Demo', 'DEMO',
            'prøveversjon', 'Prøveversjon',
            'begrenset', 'Begrenset',
            'demo-mode', 'demo_mode',
            'trial', 'Trial'
        ]
        
        return any(indicator in content for indicator in demo_indicators)
        
    def check_for_trial_indicators(self, content: str) -> bool:
        """Check if content indicates trial mode"""
        if not content:
            return False
            
        trial_indicators = [
            'trial', 'Trial', 'TRIAL',
            'prøveperiode', 'Prøveperiode',
            'gratis periode', 'gratisperiode',
            'trial-mode', 'trial_mode',
            'dager igjen', 'days left'
        ]
        
        return any(indicator in content for indicator in trial_indicators)
        
    def check_for_restriction_message(self, content: str) -> bool:
        """Check if content shows restriction/upgrade message"""
        if not content:
            return False
            
        restriction_indicators = [
            'oppgrader', 'Oppgrader', 'upgrade', 'Upgrade',
            'abonnement', 'Abonnement', 'subscription',
            'premium', 'Premium', 'PREMIUM',
            'kjøp', 'Kjøp', 'buy', 'purchase',
            'ikke tilgjengelig', 'not available',
            'begrenset tilgang', 'limited access',
            'kun for abonnenter', 'subscribers only'
        ]
        
        return any(indicator in content for indicator in restriction_indicators)
        
    def check_for_upgrade_prompt(self, content: str) -> bool:
        """Check if content shows upgrade prompt"""
        if not content:
            return False
            
        upgrade_indicators = [
            'oppgrader nå', 'upgrade now',
            'kjøp abonnement', 'buy subscription',
            'velg plan', 'choose plan',
            'få tilgang', 'get access',
            'start abonnement', 'start subscription'
        ]
        
        return any(indicator.lower() in content.lower() for indicator in upgrade_indicators)
        
    def check_for_premium_features(self, content: str) -> bool:
        """Check if content shows premium features"""
        if not content:
            return False
            
        premium_indicators = [
            'avansert analyse', 'advanced analysis',
            'premium innsikt', 'premium insights',
            'ekspert anbefalinger', 'expert recommendations',
            'detaljert rapport', 'detailed report',
            'full tilgang', 'full access',
            'ubegrenset', 'unlimited'
        ]
        
        return any(indicator.lower() in content.lower() for indicator in premium_indicators)
        
    def analyze_access_control_results(self, results: Dict) -> Dict:
        """Analyze the access control test results"""
        analysis = {
            'issues': [],
            'warnings': [],
            'correct_behaviors': [],
            'overall_status': 'UNKNOWN'
        }
        
        tests = results['tests']
        should_require_auth = results['should_require_auth']
        should_allow_demo = results['should_allow_demo']
        should_allow_trial = results['should_allow_trial']
        
        # Analyze no-auth access
        if 'no_auth' in tests:
            no_auth = tests['no_auth']
            if should_require_auth:
                if no_auth.get('has_login_redirect'):
                    analysis['correct_behaviors'].append("Correctly redirects to login when not authenticated")
                elif no_auth.get('status_code') == 200:
                    analysis['issues'].append("Endpoint accessible without authentication when it should require auth")
            else:
                if no_auth.get('status_code') == 200:
                    analysis['correct_behaviors'].append("Public endpoint correctly accessible without auth")
                    
        # Analyze demo access
        if 'demo_user' in tests and should_allow_demo:
            demo = tests['demo_user']
            if demo.get('status_code') == 200 and demo.get('has_demo_indicators'):
                analysis['correct_behaviors'].append("Demo user has appropriate access with demo indicators")
            elif demo.get('has_restriction_message'):
                analysis['warnings'].append("Demo user sees restriction messages - check if intended")
                
        # Analyze trial access
        if 'trial_user' in tests and should_allow_trial:
            trial = tests['trial_user']
            if trial.get('status_code') == 200:
                analysis['correct_behaviors'].append("Trial user has access")
            else:
                analysis['warnings'].append("Trial user access may be restricted")
                
        # Analyze expired trial access
        if 'expired_trial' in tests:
            expired = tests['expired_trial']
            if expired.get('blocked_access') or expired.get('has_upgrade_prompt'):
                analysis['correct_behaviors'].append("Expired trial correctly shows upgrade prompt or blocks access")
            elif expired.get('status_code') == 200 and not expired.get('has_restriction_message'):
                analysis['issues'].append("Expired trial user has full access without restrictions")
                
        # Analyze premium access
        if 'premium_user' in tests:
            premium = tests['premium_user']
            if premium.get('has_full_access'):
                analysis['correct_behaviors'].append("Premium user has full access")
            else:
                analysis['warnings'].append("Premium user access may be restricted")
                
        # Determine overall status
        if analysis['issues']:
            analysis['overall_status'] = 'ISSUES_FOUND'
        elif analysis['warnings']:
            analysis['overall_status'] = 'WARNINGS'
        else:
            analysis['overall_status'] = 'PASSED'
            
        return analysis
        
    def run_comprehensive_access_control_test(self) -> List[Dict]:
        """Run comprehensive access control tests"""
        
        print("🔐 Starting comprehensive access control testing...")
        print(f"🌐 Base URL: {self.base_url}")
        print()
        
        # Define endpoints that should have access control
        protected_endpoints = [
            {
                'endpoint': '/analysis',
                'description': 'Main analysis page',
                'should_require_auth': True,
                'should_allow_demo': True,
                'should_allow_trial': True
            },
            {
                'endpoint': '/portfolio',
                'description': 'Portfolio overview',
                'should_require_auth': True,
                'should_allow_demo': True,
                'should_allow_trial': True
            },
            {
                'endpoint': '/portfolio/advanced',
                'description': 'Advanced portfolio features',
                'should_require_auth': True,
                'should_allow_demo': False,  # Premium feature
                'should_allow_trial': True
            },
            {
                'endpoint': '/features/analyst-recommendations',
                'description': 'Analyst recommendations',
                'should_require_auth': True,
                'should_allow_demo': True,
                'should_allow_trial': True
            },
            {
                'endpoint': '/features/social-sentiment',
                'description': 'Social sentiment analysis',
                'should_require_auth': True,
                'should_allow_demo': False,  # Premium feature
                'should_allow_trial': True
            },
            {
                'endpoint': '/features/ai-predictions',
                'description': 'AI predictions',
                'should_require_auth': True,
                'should_allow_demo': False,  # Premium feature
                'should_allow_trial': True
            },
            {
                'endpoint': '/market-intel',
                'description': 'Market intelligence',
                'should_require_auth': True,
                'should_allow_demo': True,
                'should_allow_trial': True
            },
            {
                'endpoint': '/profile',
                'description': 'User profile',
                'should_require_auth': True,
                'should_allow_demo': True,
                'should_allow_trial': True
            },
            {
                'endpoint': '/notifications',
                'description': 'User notifications',
                'should_require_auth': True,
                'should_allow_demo': True,
                'should_allow_trial': True
            }
        ]
        
        # Test each endpoint
        total_tests = len(protected_endpoints)
        passed_tests = 0
        failed_tests = 0
        
        for i, endpoint_config in enumerate(protected_endpoints, 1):
            print(f"\n📋 [{i:2d}/{total_tests}] Testing: {endpoint_config['description']}")
            print("=" * 60)
            
            result = self.test_endpoint_access_control(**endpoint_config)
            
            # Print summary
            analysis = result['analysis']
            status = analysis['overall_status']
            
            if status == 'PASSED':
                print(f"    ✅ PASSED - Access control working correctly")
                passed_tests += 1
            elif status == 'WARNINGS':
                print(f"    ⚠️  WARNINGS - Check the following:")
                for warning in analysis['warnings']:
                    print(f"       🔸 {warning}")
                passed_tests += 1  # Count as passed but with warnings
            else:
                print(f"    ❌ ISSUES FOUND:")
                for issue in analysis['issues']:
                    print(f"       🔸 {issue}")
                failed_tests += 1
                
            # Print correct behaviors
            if analysis['correct_behaviors']:
                print(f"    ✅ Correct behaviors:")
                for behavior in analysis['correct_behaviors']:
                    print(f"       ✓ {behavior}")
                    
        print("\n" + "=" * 60)
        print("📊 Access Control Test Summary:")
        print(f"    ✅ Passed: {passed_tests}")
        print(f"    ❌ Failed: {failed_tests}")
        print(f"    📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        return self.results
        
    def generate_access_control_report(self, filename: str = "access_control_report.json"):
        """Generate detailed access control report"""
        report = {
            'test_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url,
            'total_endpoints_tested': len(self.results),
            'summary': {
                'passed': len([r for r in self.results if r['analysis']['overall_status'] == 'PASSED']),
                'warnings': len([r for r in self.results if r['analysis']['overall_status'] == 'WARNINGS']),
                'failed': len([r for r in self.results if r['analysis']['overall_status'] == 'ISSUES_FOUND']),
            },
            'results': self.results,
            'recommendations': self._generate_recommendations()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📄 Access control report saved to: {filename}")
        return report
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze all results for patterns
        issues_found = []
        for result in self.results:
            issues_found.extend(result['analysis']['issues'])
            
        # Generate specific recommendations
        if any('without authentication' in issue for issue in issues_found):
            recommendations.append("Review authentication decorators on protected endpoints")
            
        if any('full access without restrictions' in issue for issue in issues_found):
            recommendations.append("Implement proper trial expiration checking")
            
        if any('Demo user' in issue for issue in issues_found):
            recommendations.append("Review demo user access permissions")
            
        # Add general recommendations
        recommendations.extend([
            "Regularly test access control with automated tests",
            "Implement proper logging for access control violations",
            "Consider rate limiting for demo/trial users",
            "Ensure consistent UX for access restrictions across all features"
        ])
        
        return recommendations


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Access control testing for Aksjeradar')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL to test (default: http://localhost:5000)')
    parser.add_argument('--output', default='access_control_report.json',
                       help='Output file for detailed report')
    
    args = parser.parse_args()
    
    # Create tester and run tests
    tester = AccessControlTester(args.url)
    
    try:
        results = tester.run_comprehensive_access_control_test()
        
        # Generate report
        tester.generate_access_control_report(args.output)
        
        # Exit with appropriate code
        failed_count = len([r for r in results if r['analysis']['overall_status'] == 'ISSUES_FOUND'])
        warning_count = len([r for r in results if r['analysis']['overall_status'] == 'WARNINGS'])
        
        if failed_count > 0:
            print(f"\n⚠️  {failed_count} endpoints have access control issues.")
            sys.exit(1)
        elif warning_count > 0:
            print(f"\n⚠️  {warning_count} endpoints have warnings but are functioning.")
            sys.exit(0)
        else:
            print("\n🎉 All access control tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
