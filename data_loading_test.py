#!/usr/bin/env python3
"""
Data loading and template rendering test for Aksjeradar
Specifically tests that data is being fetched and displayed correctly
"""
import requests
import re
import json
from bs4 import BeautifulSoup
import sys

class DataLoadingTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, status, message, details=None):
        """Log test result"""
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {message}")
        if details:
            print(f"   📋 {details}")
        
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details
        })
    
    def test_homepage_data(self):
        """Test that homepage loads with proper data"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code != 200:
                self.log_result("Homepage Data", "FAIL", f"Status code: {response.status_code}")
                return False
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for essential homepage elements
            checks = [
                ('Title tag', soup.find('title')),
                ('Navigation', soup.find('nav') or soup.find(class_='navbar')),
                ('Main content', soup.find('main') or soup.find(class_='container')),
                ('Aksjeradar branding', 'aksjeradar' in response.text.lower()),
            ]
            
            passed = 0
            for check_name, check_result in checks:
                if check_result:
                    passed += 1
                else:
                    self.log_result(f"Homepage - {check_name}", "FAIL", "Element missing")
            
            if passed == len(checks):
                self.log_result("Homepage Data", "PASS", f"All {passed} checks passed")
                return True
            else:
                self.log_result("Homepage Data", "FAIL", f"Only {passed}/{len(checks)} checks passed")
                return False
                
        except Exception as e:
            self.log_result("Homepage Data", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_demo_page_data(self):
        """Test that demo page has proper data and functionality"""
        try:
            response = self.session.get(f"{self.base_url}/demo")
            
            if response.status_code != 200:
                self.log_result("Demo Page Data", "FAIL", f"Status code: {response.status_code}")
                return False
            
            content = response.text.lower()
            
            # Look for demo-specific content
            demo_indicators = [
                ('Stock symbol', 'eqnr' in content or 'equinor' in content),
                ('Price data', 'nok' in content or 'kroner' in content or any(price in content for price in ['287.', '234.', '156.'])),
                ('Demo label', 'demo' in content),
                ('Interactive elements', 'button' in content or 'onclick' in content),
                ('Norwegian content', any(word in content for word in ['aksjer', 'analyse', 'portefølje', 'marked'])),
            ]
            
            passed = sum(1 for _, check in demo_indicators if check)
            
            if passed >= 4:  # At least 4 out of 5 should pass
                self.log_result("Demo Page Data", "PASS", f"{passed}/5 data indicators found")
                return True
            else:
                failed_checks = [name for name, check in demo_indicators if not check]
                self.log_result("Demo Page Data", "FAIL", f"Only {passed}/5 indicators found", 
                               f"Missing: {failed_checks}")
                return False
                
        except Exception as e:
            self.log_result("Demo Page Data", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_template_structure(self):
        """Test that templates have proper structure"""
        pages_to_test = [
            ('/', 'Homepage'),
            ('/demo', 'Demo page'),
            ('/login', 'Login page'),
            ('/register', 'Register page'),
        ]
        
        passed_pages = 0
        
        for url, page_name in pages_to_test:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                
                if response.status_code != 200:
                    self.log_result(f"Template - {page_name}", "FAIL", f"Status: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check essential template elements
                template_checks = [
                    ('HTML structure', soup.find('html') and soup.find('head') and soup.find('body')),
                    ('Bootstrap CSS', 'bootstrap' in response.text.lower()),
                    ('Navigation', soup.find('nav') or soup.find(class_=re.compile('nav', re.I))),
                    ('Main content area', soup.find('main') or soup.find(class_=re.compile('container|content', re.I))),
                    ('No template errors', '{{' not in response.text and '}}' not in response.text),
                ]
                
                page_passed = sum(1 for _, check in template_checks if check)
                
                if page_passed >= 4:  # At least 4 out of 5
                    self.log_result(f"Template - {page_name}", "PASS", f"{page_passed}/5 checks passed")
                    passed_pages += 1
                else:
                    failed = [name for name, check in template_checks if not check]
                    self.log_result(f"Template - {page_name}", "FAIL", 
                                   f"Only {page_passed}/5 checks passed", f"Failed: {failed}")
                
            except Exception as e:
                self.log_result(f"Template - {page_name}", "FAIL", f"Error: {str(e)}")
        
        overall_status = "PASS" if passed_pages >= 3 else "FAIL"
        self.log_result("Template Structure Overall", overall_status, 
                       f"{passed_pages}/{len(pages_to_test)} pages passed")
        
        return passed_pages >= 3
    
    def test_static_resources(self):
        """Test that static resources load correctly"""
        static_resources = [
            ('/static/css/style.css', 'Main CSS'),
            ('/static/css/mobile-optimized.css', 'Mobile CSS'),
            ('/static/js/main.js', 'Main JavaScript'),
            ('/favicon.ico', 'Favicon'),
        ]
        
        passed = 0
        
        for url, resource_name in static_resources:
            try:
                response = self.session.get(f"{self.base_url}{url}")
                
                if response.status_code == 200:
                    # Check content is not empty and has expected format
                    if len(response.content) > 0:
                        if url.endswith('.css') and ('font-family' in response.text or 'color' in response.text):
                            self.log_result(f"Static - {resource_name}", "PASS", "Valid CSS content")
                            passed += 1
                        elif url.endswith('.js') and ('function' in response.text or 'var' in response.text):
                            self.log_result(f"Static - {resource_name}", "PASS", "Valid JS content")
                            passed += 1
                        elif url.endswith('.ico'):
                            self.log_result(f"Static - {resource_name}", "PASS", "Favicon accessible")
                            passed += 1
                        else:
                            self.log_result(f"Static - {resource_name}", "WARN", "File accessible but content unclear")
                    else:
                        self.log_result(f"Static - {resource_name}", "FAIL", "Empty file")
                else:
                    self.log_result(f"Static - {resource_name}", "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Static - {resource_name}", "FAIL", f"Error: {str(e)}")
        
        overall_status = "PASS" if passed >= 2 else "FAIL"  # At least 2 resources should work
        self.log_result("Static Resources Overall", overall_status, f"{passed}/{len(static_resources)} resources OK")
        
        return passed >= 2
    
    def test_navigation_links(self):
        """Test that navigation links work and render properly"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code != 200:
                self.log_result("Navigation Links", "FAIL", "Homepage not accessible")
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find navigation links
            nav_links = soup.find_all('a', href=True)
            internal_links = [link['href'] for link in nav_links 
                            if link['href'].startswith('/') and not link['href'].startswith('//')]
            
            if not internal_links:
                self.log_result("Navigation Links", "FAIL", "No internal navigation links found")
                return False
            
            # Test a few key navigation links
            key_links = [link for link in internal_links if any(path in link for path in ['/demo', '/login', '/register', '/pricing'])]
            
            working_links = 0
            for link in key_links[:5]:  # Test max 5 links to avoid too many requests
                try:
                    link_response = self.session.get(f"{self.base_url}{link}")
                    if link_response.status_code in [200, 302]:  # 200 OK or 302 redirect are both fine
                        working_links += 1
                except:
                    pass
            
            if working_links >= 2:
                self.log_result("Navigation Links", "PASS", f"{working_links} links working")
                return True
            else:
                self.log_result("Navigation Links", "FAIL", f"Only {working_links} links working")
                return False
                
        except Exception as e:
            self.log_result("Navigation Links", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_mobile_responsiveness(self):
        """Test mobile CSS loading"""
        try:
            # Test mobile CSS file specifically
            response = self.session.get(f"{self.base_url}/static/css/mobile-optimized.css")
            
            if response.status_code == 200:
                css_content = response.text.lower()
                
                # Check for mobile-specific CSS rules
                mobile_indicators = [
                    '@media' in css_content,
                    'navbar' in css_content,
                    'padding' in css_content,
                    'margin' in css_content,
                ]
                
                passed_indicators = sum(mobile_indicators)
                
                if passed_indicators >= 3:
                    self.log_result("Mobile CSS", "PASS", f"{passed_indicators}/4 mobile indicators found")
                    return True
                else:
                    self.log_result("Mobile CSS", "FAIL", f"Only {passed_indicators}/4 mobile indicators found")
                    return False
            else:
                self.log_result("Mobile CSS", "FAIL", f"Mobile CSS not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Mobile CSS", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all data loading tests"""
        print("🧪 Testing Data Loading and Template Rendering")
        print("=" * 50)
        
        tests = [
            self.test_homepage_data,
            self.test_demo_page_data,
            self.test_template_structure,
            self.test_static_resources,
            self.test_navigation_links,
            self.test_mobile_responsiveness,
        ]
        
        passed_tests = 0
        
        for test_func in tests:
            print(f"\n📋 Running {test_func.__name__}...")
            if test_func():
                passed_tests += 1
        
        # Generate summary
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n{'='*50}")
        print(f"📊 DATA LOADING TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total test categories: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        # Save report
        report = {
            'summary': {
                'total_categories': total_tests,
                'passed': passed_tests,
                'failed': total_tests - passed_tests,
                'success_rate': success_rate
            },
            'detailed_results': self.test_results
        }
        
        with open('/workspaces/aksjeny/data_loading_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: data_loading_test_report.json")
        
        if success_rate >= 80:
            print("\n🎉 Data loading tests mostly passed! Application is functioning well.")
            return True
        else:
            print("\n⚠️ Several data loading issues detected. Please review the failures above.")
            return False

def main():
    """Main test runner"""
    tester = DataLoadingTester()
    
    # Check server availability
    try:
        response = requests.get(tester.base_url, timeout=5)
        print(f"✅ Server accessible at {tester.base_url}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server not running at {tester.base_url}")
        print("💡 Start server: python3 app.py")
        sys.exit(1)
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
