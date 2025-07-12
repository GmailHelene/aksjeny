#!/usr/bin/env python3
"""
Comprehensive validation test for all recent fixes:
- 15 minutes trial period text updates
- 199 kr pricing updates  
- Search functionality in navigation
- Button styling (white text on "Kjøp med Stripe")
- Navigation hover styles
- Exempt emails identification
"""

import requests
import re
from datetime import datetime

class ValidationTester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.issues = []
        
    def log(self, message, success=True):
        status = "✅" if success else "❌"
        print(f"{status} {message}")
        if not success:
            self.issues.append(message)
    
    def test_trial_period_updates(self):
        """Test that all 10 minutter references are updated to 15 minutter"""
        print("\n🔍 Testing trial period text updates...")
        
        pages_to_check = [
            '/register',
            '/login',  
            '/demo',
            '/restricted_access'
        ]
        
        for page in pages_to_check:
            try:
                response = requests.get(f"{self.base_url}{page}", timeout=10)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for old "10 minutter" references
                    if "10 minutter" in content:
                        self.log(f"Page {page} still contains '10 minutter' references", False)
                    else:
                        self.log(f"Page {page} correctly updated from '10 minutter'")
                    
                    # Check for new "15 minutter" references
                    if "15 minutter" in content or "15-minutters" in content:
                        self.log(f"Page {page} correctly shows '15 minutter' trial period")
                    
                else:
                    self.log(f"Could not access {page} (status: {response.status_code})", False)
                    
            except Exception as e:
                self.log(f"Error testing {page}: {str(e)}", False)
    
    def test_pricing_updates(self):
        """Test that all 99 kr references are updated to 199 kr"""
        print("\n💰 Testing pricing updates...")
        
        pages_to_check = [
            '/subscription',
            '/pricing', 
            '/register',
            '/'
        ]
        
        for page in pages_to_check:
            try:
                response = requests.get(f"{self.base_url}{page}", timeout=10)
                if response.status_code == 200:
                    content = response.text
                    
                    # Check for old "99 kr" references (but allow "199 kr", "399 kr" etc)
                    old_price_pattern = r'\b99\s*kr\b'
                    if re.search(old_price_pattern, content):
                        self.log(f"Page {page} still contains '99 kr' pricing", False)
                    else:
                        self.log(f"Page {page} correctly updated from '99 kr'")
                    
                    # Check for correct "199 kr" starting price
                    if "199 kr" in content or "199kr" in content:
                        self.log(f"Page {page} correctly shows '199 kr' starting price")
                    
                else:
                    self.log(f"Could not access {page} (status: {response.status_code})", False)
                    
            except Exception as e:
                self.log(f"Error testing {page}: {str(e)}", False)
    
    def test_search_functionality(self):
        """Test search functionality in navigation and footer"""
        print("\n🔍 Testing search functionality...")
        
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for search in stocks dropdown
                if 'søk i aksjer' in content.lower():
                    self.log("Search functionality found in navigation")
                else:
                    self.log("Search functionality missing from navigation", False)
                
                # Check for search in footer
                if 'søk &amp; språk' in content.lower() or 'søk & språk' in content.lower():
                    self.log("Search functionality found in footer")
                else:
                    self.log("Search functionality missing from footer", False)
                
                # Check for search form
                if '<form action=' in content and 'search' in content.lower():
                    self.log("Search form found on page")
                else:
                    self.log("Search form missing from page", False)
                    
            else:
                self.log(f"Could not access homepage (status: {response.status_code})", False)
                
        except Exception as e:
            self.log(f"Error testing search functionality: {str(e)}", False)
    
    def test_button_styling(self):
        """Test that Kjøp med Stripe buttons have correct styling"""
        print("\n🎨 Testing button styling...")
        
        try:
            response = requests.get(f"{self.base_url}/subscription", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Check for "Kjøp med Stripe" buttons
                stripe_buttons = re.findall(r'<button[^>]*>.*?Kjøp med Stripe.*?</button>', content, re.DOTALL | re.IGNORECASE)
                
                if stripe_buttons:
                    self.log(f"Found {len(stripe_buttons)} 'Kjøp med Stripe' buttons")
                    
                    # Check if buttons use btn-primary or btn-success classes (which have white text)
                    for button in stripe_buttons:
                        if 'btn-primary' in button or 'btn-success' in button:
                            self.log("'Kjøp med Stripe' button uses correct styling class")
                        else:
                            self.log("'Kjøp med Stripe' button missing correct styling", False)
                else:
                    self.log("No 'Kjøp med Stripe' buttons found", False)
                    
            else:
                self.log(f"Could not access subscription page (status: {response.status_code})", False)
                
        except Exception as e:
            self.log(f"Error testing button styling: {str(e)}", False)
    
    def test_navigation_structure(self):
        """Test improved navigation structure"""
        print("\n🧭 Testing navigation structure...")
        
        try:
            response = requests.get(self.base_url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for language switcher in footer
                if 'språk' in content and 'footer' in content:
                    self.log("Language switcher appears to be in footer")
                else:
                    self.log("Language switcher may not be in footer", False)
                
                # Check for responsive navigation
                if 'navbar-toggler' in content:
                    self.log("Responsive navigation toggle found")
                else:
                    self.log("Responsive navigation toggle missing", False)
                
                # Check for user dropdown improvements
                if 'userdropdown' in content or 'guestdropdown' in content:
                    self.log("User dropdown functionality found")
                else:
                    self.log("User dropdown functionality missing", False)
                    
            else:
                self.log(f"Could not access homepage (status: {response.status_code})", False)
                
        except Exception as e:
            self.log(f"Error testing navigation: {str(e)}", False)
    
    def show_exempt_emails(self):
        """Display the list of exempt emails"""
        print("\n📧 Exempt Emails (Always have full access):")
        exempt_emails = [
            'helene@luxushair.com',
            'helene721@gmail.com', 
            'eiriktollan.berntsen@gmail.com'
        ]
        
        for email in exempt_emails:
            print(f"   • {email}")
        
        print("\nThese emails are exempt from:")
        print("   • Trial period restrictions")
        print("   • Subscription requirements") 
        print("   • Access control limitations")
        print("   • Payment requirements")
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("=" * 60)
        print("🔧 COMPREHENSIVE VALIDATION TEST")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.test_trial_period_updates()
        self.test_pricing_updates()
        self.test_search_functionality()
        self.test_button_styling()
        self.test_navigation_structure()
        self.show_exempt_emails()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        if not self.issues:
            print("✅ ALL TESTS PASSED! No issues found.")
        else:
            print(f"❌ Found {len(self.issues)} issues:")
            for issue in self.issues:
                print(f"   • {issue}")
        
        print(f"\nTest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return len(self.issues) == 0

if __name__ == "__main__":
    tester = ValidationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
