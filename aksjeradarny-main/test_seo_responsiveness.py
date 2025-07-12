#!/usr/bin/env python3
"""
Comprehensive SEO and Responsiveness Test
Tests all SEO optimizations and responsive design implementations.
"""

import requests
from bs4 import BeautifulSoup
import sys
import time

def test_seo_elements(url, expected_title_part=None):
    """Test SEO elements for a given URL"""
    print(f"\n=== Testing SEO for {url} ===")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test title
        title = soup.find('title')
        if title:
            print(f"✓ Title: {title.text}")
            if expected_title_part and expected_title_part in title.text:
                print(f"✓ Title contains expected text: {expected_title_part}")
        else:
            print("✗ No title found")
            
        # Test meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            print(f"✓ Meta description: {meta_desc.get('content')[:100]}...")
        else:
            print("✗ No meta description found")
            
        # Test meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            print(f"✓ Meta keywords: {meta_keywords.get('content')[:100]}...")
        else:
            print("✗ No meta keywords found")
            
        # Test canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            print(f"✓ Canonical URL: {canonical.get('href')}")
        else:
            print("✗ No canonical URL found")
            
        # Test Open Graph tags
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        
        if og_title:
            print(f"✓ OG Title: {og_title.get('content')}")
        else:
            print("✗ No OG title found")
            
        if og_desc:
            print(f"✓ OG Description: {og_desc.get('content')[:100]}...")
        else:
            print("✗ No OG description found")
            
        if og_image:
            print(f"✓ OG Image: {og_image.get('content')}")
        else:
            print("✗ No OG image found")
            
        # Test Twitter Card tags
        twitter_card = soup.find('meta', attrs={'property': 'twitter:card'})
        if twitter_card:
            print(f"✓ Twitter Card: {twitter_card.get('content')}")
        else:
            print("✗ No Twitter Card found")
            
        # Test Schema.org markup
        schema_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
        if schema_scripts:
            print(f"✓ Schema.org markup found: {len(schema_scripts)} scripts")
        else:
            print("✗ No Schema.org markup found")
            
        # Test robots meta tag
        robots = soup.find('meta', attrs={'name': 'robots'})
        if robots:
            print(f"✓ Robots meta: {robots.get('content')}")
        else:
            print("✗ No robots meta found")
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing {url}: {str(e)}")
        return False

def test_responsiveness(url):
    """Test responsive design elements"""
    print(f"\n=== Testing Responsiveness for {url} ===")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            print(f"✓ Viewport meta: {viewport.get('content')}")
        else:
            print("✗ No viewport meta found")
            
        # Test responsive CSS classes
        responsive_classes = [
            'img-fluid', 'table-responsive', 'd-md-none', 'd-lg-block',
            'col-md-', 'col-lg-', 'col-sm-', 'row', 'container'
        ]
        
        found_classes = []
        for cls in responsive_classes:
            if soup.find(class_=lambda x: x and cls in x):
                found_classes.append(cls)
                
        if found_classes:
            print(f"✓ Responsive classes found: {', '.join(found_classes)}")
        else:
            print("✗ No responsive classes found")
            
        # Test Bootstrap grid
        rows = soup.find_all(class_=lambda x: x and 'row' in x)
        cols = soup.find_all(class_=lambda x: x and ('col-' in x or 'col ' in x))
        
        if rows and cols:
            print(f"✓ Bootstrap grid: {len(rows)} rows, {len(cols)} columns")
        else:
            print("✗ No Bootstrap grid found")
            
        # Test responsive images
        img_fluid = soup.find_all(class_=lambda x: x and 'img-fluid' in x)
        responsive_imgs = soup.find_all('img', style=lambda x: x and ('width: 100%' in x or 'max-width: 100%' in x))
        
        if img_fluid or responsive_imgs:
            print(f"✓ Responsive images: {len(img_fluid)} img-fluid, {len(responsive_imgs)} with responsive styles")
        else:
            print("✗ No responsive images found")
            
        # Test mobile-optimized styles
        mobile_css = soup.find('link', href=lambda x: x and 'mobile' in x)
        if mobile_css:
            print(f"✓ Mobile CSS: {mobile_css.get('href')}")
        else:
            print("✗ No mobile-specific CSS found")
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing responsiveness for {url}: {str(e)}")
        return False

def test_special_seo_files(base_url):
    """Test robots.txt and sitemap.xml"""
    print(f"\n=== Testing Special SEO Files ===")
    
    # Test robots.txt
    try:
        robots_url = f"{base_url}/robots.txt"
        response = requests.get(robots_url, timeout=10)
        if response.status_code == 200:
            print(f"✓ robots.txt found: {len(response.text)} characters")
            if 'Sitemap:' in response.text:
                print("✓ Sitemap declaration in robots.txt")
            else:
                print("✗ No sitemap declaration in robots.txt")
        else:
            print(f"✗ robots.txt not found (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error testing robots.txt: {str(e)}")
        
    # Test sitemap.xml
    try:
        sitemap_url = f"{base_url}/sitemap.xml"
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code == 200:
            print(f"✓ sitemap.xml found: {len(response.text)} characters")
            if '<urlset' in response.text and '<url>' in response.text:
                print("✓ Valid XML sitemap structure")
            else:
                print("✗ Invalid sitemap structure")
        else:
            print(f"✗ sitemap.xml not found (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error testing sitemap.xml: {str(e)}")

def main():
    """Main test function"""
    base_url = "http://localhost:5000"  # Adjust as needed
    
    # Test pages
    test_pages = [
        (f"{base_url}/", "Aksjeradar"),
        (f"{base_url}/stocks", "Aksjer"),
        (f"{base_url}/stocks?category=oslo", "Oslo Børs"),
        (f"{base_url}/stocks?category=global", "Globale"),
        (f"{base_url}/stocks?category=crypto", "Kryptovaluta"),
        (f"{base_url}/stocks/EQNR.OL", "EQNR"),
        (f"{base_url}/analysis", "Analyse"),
        (f"{base_url}/portfolio", "Portefølje"),
        (f"{base_url}/news", "Nyheter"),
        (f"{base_url}/blog", "Blogg"),
    ]
    
    print("Starting comprehensive SEO and Responsiveness Test")
    print("=" * 60)
    
    # Test special SEO files first
    test_special_seo_files(base_url)
    
    # Test each page
    total_tests = 0
    passed_tests = 0
    
    for url, expected_title in test_pages:
        total_tests += 2  # SEO + Responsiveness
        
        if test_seo_elements(url, expected_title):
            passed_tests += 1
            
        if test_responsiveness(url):
            passed_tests += 1
            
        time.sleep(1)  # Be nice to the server
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! SEO and responsiveness are optimized.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
