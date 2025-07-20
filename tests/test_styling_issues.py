#!/usr/bin/env python3
"""
Specific tests for styling issues in Aksjeradar
Focuses on contrast, visibility, and dark mode issues
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Tuple
import colorsys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class StyleChecker:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.issues = []
        
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)
        
        # Calculate relative luminance
        def relative_luminance(rgb):
            r, g, b = [x/255.0 for x in rgb]
            r = r/12.92 if r <= 0.03928 else ((r + 0.055)/1.055) ** 2.4
            g = g/12.92 if g <= 0.03928 else ((g + 0.055)/1.055) ** 2.4
            b = b/12.92 if b <= 0.03928 else ((b + 0.055)/1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        lum1 = relative_luminance(rgb1)
        lum2 = relative_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def check_page_styling(self, url: str) -> List[Dict]:
        """Check a single page for styling issues"""
        page_issues = []
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return page_issues
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check inline styles
            for element in soup.find_all(style=True):
                style = element.get('style', '')
                issues = self.analyze_style(style, element, url)
                page_issues.extend(issues)
            
            # Check style tags
            for style_tag in soup.find_all('style'):
                if style_tag.string:
                    issues = self.analyze_css(style_tag.string, url)
                    page_issues.extend(issues)
            
            # Check Bootstrap dark mode issues
            issues = self.check_bootstrap_dark_mode(soup, url)
            page_issues.extend(issues)
            
            # Check form visibility
            issues = self.check_form_visibility(soup, url)
            page_issues.extend(issues)
            
        except Exception as e:
            page_issues.append({
                'url': url,
                'type': 'error',
                'message': f'Error checking page: {str(e)}'
            })
        
        return page_issues
    
    def analyze_style(self, style: str, element, url: str) -> List[Dict]:
        """Analyze inline style for issues"""
        issues = []
        
        # Extract color and background-color
        color_match = re.search(r'color:\s*([^;]+)', style)
        bg_match = re.search(r'background(?:-color)?:\s*([^;]+)', style)
        
        if color_match and bg_match:
            color = color_match.group(1).strip()
            bg = bg_match.group(1).strip()
            
            # Check if both are hex colors
            if color.startswith('#') and bg.startswith('#'):
                try:
                    contrast = self.calculate_contrast_ratio(color, bg)
                    if contrast < 4.5:  # WCAG AA standard
                        issues.append({
                            'url': url,
                            'type': 'low_contrast',
                            'element': element.name,
                            'color': color,
                            'background': bg,
                            'contrast_ratio': contrast,
                            'required': 4.5,
                            'severity': 'high' if contrast < 3 else 'medium'
                        })
                except:
                    pass
        
        # Check for problematic patterns
        problematic_patterns = [
            (r'color:\s*#[0-3][0-9a-f]{2}', 'dark_text'),
            (r'opacity:\s*0(?:\.0)?[;\s}]', 'invisible_element'),
            (r'visibility:\s*hidden', 'hidden_element'),
            (r'display:\s*none', 'display_none'),
        ]
        
        for pattern, issue_type in problematic_patterns:
            if re.search(pattern, style, re.IGNORECASE):
                issues.append({
                    'url': url,
                    'type': issue_type,
                    'element': element.name,
                    'style': style,
                    'severity': 'high' if issue_type in ['invisible_element', 'hidden_element'] else 'medium'
                })
        
        return issues
    
    def analyze_css(self, css: str, url: str) -> List[Dict]:
        """Analyze CSS content for issues"""
        issues = []
        
        # Find all CSS rules
        rules = re.findall(r'([^{]+)\{([^}]+)\}', css)
        
        for selector, properties in rules:
            # Check for dark on dark
            if 'dark' in selector.lower() or 'bg-dark' in selector:
                color_match = re.search(r'color:\s*([^;]+)', properties)
                if color_match:
                    color = color_match.group(1).strip()
                    if color.startswith('#'):
                        try:
                            rgb = self.hex_to_rgb(color)
                            # Check if color is dark (low luminance)
                            if sum(rgb) < 384:  # Roughly half of max (765)
                                issues.append({
                                    'url': url,
                                    'type': 'dark_on_dark_css',
                                    'selector': selector.strip(),
                                    'color': color,
                                    'severity': 'high'
                                })
                        except:
                            pass
        
        return issues
    
    def check_bootstrap_dark_mode(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Check for Bootstrap dark mode issues"""
        issues = []
        
        # Find elements with dark backgrounds
        dark_elements = soup.find_all(class_=re.compile(r'bg-dark|navbar-dark'))
        
        for element in dark_elements:
            classes = ' '.join(element.get('class', []))
            
            # Check if proper text color is set
            has_light_text = any(cls in classes for cls in ['text-light', 'text-white', 'navbar-dark'])
            
            if not has_light_text:
                # Check children for text
                text_content = element.get_text(strip=True)
                if text_content:
                    issues.append({
                        'url': url,
                        'type': 'missing_light_text_on_dark_bg',
                        'element': element.name,
                        'classes': classes,
                        'text_preview': text_content[:50],
                        'severity': 'high',
                        'fix': 'Add text-light or text-white class'
                    })
        
        return issues
    
    def check_form_visibility(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Check form elements for visibility issues"""
        issues = []
        
        # Check all form inputs
        form_elements = soup.find_all(['input', 'textarea', 'select', 'button'])
        
        for element in form_elements:
            # Skip hidden inputs
            if element.get('type') == 'hidden':
                continue
            
            # Check for dark styling issues
            classes = ' '.join(element.get('class', []))
            style = element.get('style', '')
            
            # Check if element might be invisible
            if 'dark' in classes and 'form-control' in classes:
                parent = element.parent
                parent_classes = ' '.join(parent.get('class', [])) if parent else ''
                
                if 'bg-dark' in parent_classes and 'text-light' not in classes:
                    issues.append({
                        'url': url,
                        'type': 'dark_form_element',
                        'element': f'{element.name}[name="{element.get("name", "unnamed")}"]',
                        'severity': 'high',
                        'fix': 'Add appropriate Bootstrap classes for dark mode'
                    })
        
        return issues
    
    def check_all_pages(self) -> Dict:
        """Check all important pages for styling issues"""
        pages_to_check = [
            '/',
            '/demo',
            '/login',
            '/register',
            '/pricing',
            '/stocks',
            '/stocks/list',
            '/analysis',
            '/portfolio',
            '/about',
            '/contact'
        ]
        
        print("🎨 Checking for styling issues...")
        print("=" * 60)
        
        all_issues = []
        
        for page in pages_to_check:
            url = self.base_url + page
            print(f"\n📍 Checking {page}...")
            
            issues = self.check_page_styling(url)
            all_issues.extend(issues)
            
            if issues:
                print(f"   ⚠️  Found {len(issues)} issues")
                # Group by type
                issue_types = {}
                for issue in issues:
                    issue_type = issue['type']
                    issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
                
                for issue_type, count in issue_types.items():
                    print(f"      • {issue_type}: {count}")
            else:
                print("   ✅ No styling issues found")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 STYLING ISSUES SUMMARY")
        print("=" * 60)
        
        if all_issues:
            # Group by severity
            high_severity = [i for i in all_issues if i.get('severity') == 'high']
            medium_severity = [i for i in all_issues if i.get('severity') == 'medium']
            
            print(f"\n🚨 High severity: {len(high_severity)} issues")
            print(f"⚠️  Medium severity: {len(medium_severity)} issues")
            
            # Show examples of high severity issues
            if high_severity:
                print("\n🔍 Examples of high severity issues:")
                for issue in high_severity[:5]:  # Show first 5
                    print(f"\n   URL: {issue['url']}")
                    print(f"   Type: {issue['type']}")
                    if 'fix' in issue:
                        print(f"   Fix: {issue['fix']}")
                    if 'contrast_ratio' in issue:
                        print(f"   Contrast: {issue['contrast_ratio']:.2f} (required: {issue['required']})")
        else:
            print("\n✅ No styling issues found!")
        
        return {
            'total_issues': len(all_issues),
            'high_severity': len([i for i in all_issues if i.get('severity') == 'high']),
            'medium_severity': len([i for i in all_issues if i.get('severity') == 'medium']),
            'issues': all_issues
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check Aksjeradar for styling issues')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL to test')
    args = parser.parse_args()
    
    checker = StyleChecker(args.url)
    results = checker.check_all_pages()
    
    # Save detailed report
    import json
    from datetime import datetime
    
    report_file = f"styling_issues_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Return exit code based on high severity issues
    return 0 if results['high_severity'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
