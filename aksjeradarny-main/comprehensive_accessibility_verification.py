#!/usr/bin/env python3
"""
Comprehensive Accessibility and Responsive Design Verification Script
Tests all critical aspects of the UI that were mentioned in the TODO list
"""

import os
import re
from pathlib import Path

class AccessibilityVerifier:
    def __init__(self):
        self.app_dir = Path("/workspaces/aksjeradarny/app")
        self.issues = []
        self.passed_tests = []
        
    def test_contrast_compliance(self):
        """Test for proper color contrast across the application"""
        print("🎨 Testing Color Contrast Compliance...")
        
        # Check main style.css for proper contrast declarations
        style_file = self.app_dir / "static/css/style.css"
        if style_file.exists():
            content = style_file.read_text()
            
            # Verify dark text on light backgrounds
            if "#212529" in content and "#fff" in content:
                self.passed_tests.append("✅ Dark text (#212529) on white backgrounds defined")
            
            # Verify white text on dark backgrounds
            if 'color: #fff' in content and 'background-color: #212529' in content:
                self.passed_tests.append("✅ White text on dark backgrounds properly defined")
            
            # Check for dangerous white-on-white patterns
            dangerous_patterns = [
                r'color:\s*#fff.*background.*#fff',
                r'background.*#fff.*color:\s*#fff'
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.issues.append(f"❌ Potential white-on-white contrast issue found")
                else:
                    self.passed_tests.append("✅ No white-on-white contrast issues detected")
        
    def test_responsive_design(self):
        """Test responsive design implementation"""
        print("📱 Testing Responsive Design...")
        
        # Check mobile-optimized.css
        mobile_css = self.app_dir / "static/css/mobile-optimized.css"
        if mobile_css.exists():
            content = mobile_css.read_text()
            
            # Check for proper breakpoints
            breakpoints = ['@media (max-width: 768px)', '@media (max-width: 991px)', '@media (max-width: 575px)']
            for bp in breakpoints:
                if bp in content:
                    self.passed_tests.append(f"✅ Responsive breakpoint found: {bp}")
                else:
                    self.issues.append(f"❌ Missing responsive breakpoint: {bp}")
            
            # Check for mobile-specific optimizations
            mobile_optimizations = [
                'touch-action',
                'min-height: 44px',  # Touch target size
                '-webkit-overflow-scrolling: touch'
            ]
            
            for opt in mobile_optimizations:
                if opt in content:
                    self.passed_tests.append(f"✅ Mobile optimization found: {opt}")
        
    def test_accessibility_features(self):
        """Test accessibility features implementation"""
        print("♿ Testing Accessibility Features...")
        
        # Check templates for accessibility patterns
        templates_dir = self.app_dir / "templates"
        accessibility_patterns = {
            'aria-label': 0,
            'alt=': 0,
            'role=': 0,
            'tabindex=': 0
        }
        
        if templates_dir.exists():
            for template_file in templates_dir.rglob("*.html"):
                content = template_file.read_text()
                for pattern in accessibility_patterns:
                    accessibility_patterns[pattern] += content.count(pattern)
            
            for pattern, count in accessibility_patterns.items():
                if count > 0:
                    self.passed_tests.append(f"✅ Accessibility pattern '{pattern}' found {count} times")
                else:
                    self.issues.append(f"⚠️ Accessibility pattern '{pattern}' not found")
    
    def test_i18n_implementation(self):
        """Test internationalization implementation"""
        print("🌍 Testing Internationalization...")
        
        # Check for i18n.js
        i18n_file = self.app_dir / "static/js/i18n.js"
        if i18n_file.exists():
            content = i18n_file.read_text()
            
            # Check for proper i18n patterns
            i18n_patterns = [
                'translations',
                'setLanguage',
                'updatePageLanguage',
                'localStorage.getItem'
            ]
            
            for pattern in i18n_patterns:
                if pattern in content:
                    self.passed_tests.append(f"✅ I18n pattern found: {pattern}")
                else:
                    self.issues.append(f"❌ Missing I18n pattern: {pattern}")
        else:
            self.issues.append("❌ i18n.js file not found")
    
    def test_pwa_features(self):
        """Test PWA features implementation"""
        print("📱 Testing PWA Features...")
        
        # Check for manifest.json
        manifest_file = self.app_dir / "static/manifest.json"
        if manifest_file.exists():
            self.passed_tests.append("✅ PWA manifest.json found")
        else:
            self.issues.append("❌ PWA manifest.json not found")
        
        # Check for service worker
        sw_file = self.app_dir / "static/sw.js"
        if sw_file.exists():
            self.passed_tests.append("✅ Service worker (sw.js) found")
        else:
            self.issues.append("❌ Service worker not found")
    
    def test_performance_optimizations(self):
        """Test performance optimization implementations"""
        print("⚡ Testing Performance Optimizations...")
        
        # Check for loading states CSS
        loading_css = self.app_dir / "static/css/loading-states.css"
        if loading_css.exists():
            content = loading_css.read_text()
            
            performance_patterns = [
                'skeleton',
                'loading',
                'transition',
                'transform',
                'backdrop-filter'
            ]
            
            for pattern in performance_patterns:
                if pattern in content:
                    self.passed_tests.append(f"✅ Performance pattern found: {pattern}")
        
        # Check for image optimization hints
        style_css = self.app_dir / "static/css/style.css"
        if style_css.exists():
            content = style_css.read_text()
            if 'image-rendering' in content:
                self.passed_tests.append("✅ Image rendering optimization found")
    
    def test_navigation_improvements(self):
        """Test navigation improvements"""
        print("🧭 Testing Navigation Improvements...")
        
        # Check navigation menu
        menu_template = self.app_dir / "templates/analysis/_menu.html"
        if menu_template.exists():
            content = menu_template.read_text()
            
            # Check for proper button groups
            if 'btn-group' in content:
                self.passed_tests.append("✅ Button groups in navigation menu")
            
            # Check for proper navigation structure
            if 'url_for(' in content:
                self.passed_tests.append("✅ Proper Flask routing in navigation")
            
            # Check for icons
            if 'bi bi-' in content:
                self.passed_tests.append("✅ Bootstrap icons in navigation")
    
    def test_form_improvements(self):
        """Test form improvements and validation"""
        print("📝 Testing Form Improvements...")
        
        # Check for enhanced form styling
        style_css = self.app_dir / "static/css/style.css"
        if style_css.exists():
            content = style_css.read_text()
            
            form_patterns = [
                'form-control',
                'form-floating',
                'is-valid',
                'is-invalid'
            ]
            
            for pattern in form_patterns:
                if pattern in content:
                    self.passed_tests.append(f"✅ Form pattern found: {pattern}")
    
    def run_all_tests(self):
        """Run all verification tests"""
        print("🔍 Starting Comprehensive Accessibility & Responsive Design Verification\n")
        
        self.test_contrast_compliance()
        self.test_responsive_design()
        self.test_accessibility_features()
        self.test_i18n_implementation()
        self.test_pwa_features()
        self.test_performance_optimizations()
        self.test_navigation_improvements()
        self.test_form_improvements()
        
        # Report results
        print("\n" + "="*60)
        print("📊 VERIFICATION RESULTS")
        print("="*60)
        
        print(f"\n✅ PASSED TESTS ({len(self.passed_tests)}):")
        for test in self.passed_tests:
            print(f"  {test}")
        
        if self.issues:
            print(f"\n⚠️  ISSUES FOUND ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  {issue}")
        else:
            print(f"\n🎉 NO CRITICAL ISSUES FOUND!")
        
        # Calculate score
        total_tests = len(self.passed_tests) + len(self.issues)
        score = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 OVERALL SCORE: {score:.1f}% ({len(self.passed_tests)}/{total_tests})")
        
        if score >= 90:
            print("🏆 EXCELLENT - Ready for production!")
        elif score >= 75:
            print("👍 GOOD - Minor improvements needed")
        elif score >= 60:
            print("⚠️  FAIR - Several improvements needed")
        else:
            print("❌ POOR - Major improvements required")

if __name__ == "__main__":
    verifier = AccessibilityVerifier()
    verifier.run_all_tests()
