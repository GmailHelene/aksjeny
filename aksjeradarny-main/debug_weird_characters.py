#!/usr/bin/env python3
"""
Debug script to check for weird characters in register/login pages
"""
import requests
import sys
import re

def check_page_content(url, page_name):
    """Check page content for weird characters"""
    try:
        print(f"\n=== Checking {page_name} page ===")
        response = requests.get(url, timeout=10)
        content = response.text
        
        # Look for potential weird characters
        first_200_chars = content[:200]
        print(f"First 200 characters:")
        print(repr(first_200_chars))
        
        # Check for common encoding issues
        weird_patterns = [
            r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\xFF]',  # Control characters and high-bit
            r'â€™|â€œ|â€|Ã¡|Ã©|Ã­|Ã³|Ãº',  # Common UTF-8 encoding issues
            r'�',  # Replacement character
        ]
        
        for pattern in weird_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"Found weird characters: {matches[:10]}")  # Show first 10
        
        # Look at the beginning of the body content
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
        if body_match:
            body_start = body_match.group(1)[:500]  # First 500 chars of body
            print(f"\nFirst part of body content:")
            print(repr(body_start))
        
        # Check if there are any characters before DOCTYPE
        before_doctype = content.split('<!DOCTYPE')[0]
        if before_doctype.strip():
            print(f"\nContent before DOCTYPE:")
            print(repr(before_doctype))
            
        print(f"Response status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
    except Exception as e:
        print(f"Error checking {page_name}: {e}")

if __name__ == "__main__":
    # Test both pages
    base_url = "http://localhost:5000"
    
    # You can also test the live version
    if len(sys.argv) > 1 and sys.argv[1] == "live":
        base_url = "https://aksjeradar-production.up.railway.app"
    
    check_page_content(f"{base_url}/register", "Register")
    check_page_content(f"{base_url}/login", "Login")
