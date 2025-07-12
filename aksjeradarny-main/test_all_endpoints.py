#!/usr/bin/env python
"""Comprehensive endpoint testing script"""

import requests
import json
from flask import Flask
from app import create_app
import sys
from datetime import datetime

class EndpointTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_count = 0
        
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"{text}")
        print(f"{'='*60}")
        
    def print_success(self, text):
        print(f"✓ {text}")
        
    def print_error(self, text):
        print(f"✗ {text}")
        
    def print_warning(self, text):
        print(f"⚠ {text}")
        
    def test_endpoint(self, path, method="GET", data=None, auth=None, expected_status=None):
        """Test a single endpoint"""
        self.total_count += 1
        url = f"{self.base_url}{path}"
        
        try:
            if method == "GET":
                response = self.session.get(url, auth=auth)
            elif method == "POST":
                response = self.session.post(url, json=data, auth=auth)
            else:
                response = self.session.request(method, url, json=data, auth=auth)
            
            # Check for errors
            error_found = False
            
            # Check status code
            if response.status_code >= 400:
                self.print_error(f"{method} {path} - Status: {response.status_code}")
                self.errors.append({
                    'endpoint': path,
                    'method': method,
                    'status': response.status_code,
                    'type': 'HTTP Error'
                })
                error_found = True
            
            # Check for error messages in content
            if response.headers.get('content-type', '').startswith('text/html'):
                content = response.text.lower()
                error_phrases = [
                    "det oppstod en uventet feil",
                    "beklager, en feil oppsto",
                    "vi jobber med å løse problemet",
                    "prøv igjen senere",
                    "internal server error",
                    "something went wrong",
                    "kunne ikke",
                    "feil ved",
                    "error",
                    "exception"
                ]
                
                for phrase in error_phrases:
                    if phrase in content and not error_found:
                        self.print_warning(f"{method} {path} - Contains error message: '{phrase}'")
                        self.warnings.append({
                            'endpoint': path,
                            'method': method,
                            'status': response.status_code,
                            'type': 'Error Message',
                            'message': phrase
                        })
                        error_found = True
                        break
            
            # Check if redirect to login (might indicate access control issue)
            if response.history and '/login' in response.url:
                self.print_warning(f"{method} {path} - Redirected to login")
                
            if not error_found:
                self.print_success(f"{method} {path} - OK ({response.status_code})")
                self.success_count += 1
                
            return response
            
        except Exception as e:
            self.print_error(f"{method} {path} - Exception: {str(e)}")
            self.errors.append({
                'endpoint': path,
                'method': method,
                'type': 'Exception',
                'error': str(e)
            })
            return None
    
    def get_all_routes(self):
        """Get all routes from Flask app"""
        app = create_app()
        routes = []
        
        for rule in app.url_map.iter_rules():
            # Skip static files and some internal routes
            if rule.endpoint == 'static' or rule.rule.startswith('/_'):
                continue
                
            methods = list(rule.methods - {'HEAD', 'OPTIONS'})
            for method in methods:
                routes.append({
                    'path': rule.rule,
                    'method': method,
                    'endpoint': rule.endpoint,
                    'has_params': '<' in rule.rule
                })
        
        return routes
    
    def run_tests(self):
        """Run all endpoint tests"""
        self.print_header("AKSJERADAR ENDPOINT TESTING")
        print(f"Base URL: {self.base_url}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test specific problem endpoints first
        self.print_header("Testing Known Problem Endpoints")
        
        problem_endpoints = [
            '/features/social-sentiment',
            '/features/analyst-recommendations', 
            '/features/ai-predictions',
            '/market-intel',
            '/analysis/technical',
            '/analysis/prediction',
            '/analysis/recommendation',
            '/analysis/ai',
            '/portfolio/advanced',
            '/api/realtime/price/AAPL',
            '/api/realtime/batch-updates',
            '/stocks/details/AAPL',
            '/api/search?q=apple',
            '/api/stock/AAPL',
            '/api/market/overview'
        ]
        
        for endpoint in problem_endpoints:
            self.test_endpoint(endpoint)
        
        # Print summary
        self.print_header("TEST SUMMARY")
        print(f"Total endpoints tested: {self.total_count}")
        print(f"Successful: {self.success_count}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors: {len(self.errors)}")
        
        if self.errors:
            self.print_header("ERRORS FOUND")
            for error in self.errors:
                print(f"• {error['method']} {error['endpoint']} - {error['type']}")
                if 'status' in error:
                    print(f"  Status Code: {error['status']}")
                if 'error' in error:
                    print(f"  Error: {error['error']}")
        
        if self.warnings:
            self.print_header("WARNINGS")
            for warning in self.warnings:
                print(f"• {warning['method']} {warning['endpoint']} - {warning['type']}")
                if 'message' in warning:
                    print(f"  Message found: '{warning['message']}'")
        
        # Generate fix report
        self.generate_fix_report()
        
    def generate_fix_report(self):
        """Generate a report with fixes needed"""
        if not self.errors and not self.warnings:
            return
            
        with open('endpoint_fixes_needed.md', 'w') as f:
            f.write("# Endpoint Fixes Needed\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if self.errors:
                f.write("## Errors to Fix\n\n")
                for error in self.errors:
                    f.write(f"### {error['endpoint']}\n")
                    f.write(f"- Method: {error['method']}\n")
                    f.write(f"- Issue: {error['type']}\n")
                    if 'status' in error:
                        f.write(f"- Status Code: {error['status']}\n")
                    if 'error' in error:
                        f.write(f"- Error: {error['error']}\n")
                    f.write("\n")
            
            if self.warnings:
                f.write("## Warnings to Address\n\n")
                for warning in self.warnings:
                    f.write(f"### {warning['endpoint']}\n")
                    f.write(f"- Method: {warning['method']}\n")
                    f.write(f"- Issue: {warning['type']}\n")
                    if 'message' in warning:
                        f.write(f"- Error phrase found: '{warning['message']}'\n")
                    f.write("\n")
        
        print(f"\nFix report saved to: endpoint_fixes_needed.md")

if __name__ == "__main__":
    # Check if app is running
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code != 200:
            print("App is not running properly on localhost:5000")
            print("Please start the app with: python run.py")
            sys.exit(1)
    except:
        print("App is not running on localhost:5000")
        print("Please start the app with: python run.py")
        sys.exit(1)
    
    # Run tests
    tester = EndpointTester()
    tester.run_tests()
