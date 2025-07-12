#!/usr/bin/env python3
"""
Final test script for Aksjeradar application
"""
import os
import sys
import requests
import json
from datetime import datetime

def test_application():
    """Test the Aksjeradar application endpoints"""
    print("🧪 Testing Aksjeradar Application")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    tests = [
        {"name": "Homepage", "endpoint": "/", "expected_status": 200},
        {"name": "Demo Page", "endpoint": "/demo", "expected_status": 200},
        {"name": "Login Page", "endpoint": "/login", "expected_status": 200},
        {"name": "Register Page", "endpoint": "/register", "expected_status": 200},
        {"name": "Forgot Password", "endpoint": "/forgot_password", "expected_status": 200},
        {"name": "API Health", "endpoint": "/api/health", "expected_status": 200},
        {"name": "Static CSS", "endpoint": "/static/css/style.css", "expected_status": 200},
        {"name": "Static JS", "endpoint": "/static/js/main.js", "expected_status": 200},
    ]
    
    print(f"📍 Testing against: {base_url}")
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    for test in tests:
        try:
            url = f"{base_url}{test['endpoint']}"
            print(f"🔍 Testing {test['name']}...")
            print(f"   URL: {url}")
            
            response = requests.get(url, timeout=10)
            status = response.status_code
            
            if status == test['expected_status']:
                print(f"   ✅ PASS - Status: {status}")
                results.append({"test": test['name'], "status": "PASS", "code": status})
            else:
                print(f"   ❌ FAIL - Status: {status} (expected: {test['expected_status']})")
                results.append({"test": test['name'], "status": "FAIL", "code": status})
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ FAIL - Connection refused (app not running?)")
            results.append({"test": test['name'], "status": "FAIL", "code": "Connection Error"})
        except requests.exceptions.Timeout:
            print(f"   ❌ FAIL - Request timeout")
            results.append({"test": test['name'], "status": "FAIL", "code": "Timeout"})
        except Exception as e:
            print(f"   ❌ FAIL - Error: {e}")
            results.append({"test": test['name'], "status": "FAIL", "code": f"Error: {e}"})
        
        print()
    
    # Summary
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"❌ Failed: {failed}/{total} ({failed/total*100:.1f}%)")
    print()
    
    if failed > 0:
        print("❌ FAILED TESTS:")
        for r in results:
            if r['status'] == 'FAIL':
                print(f"   • {r['test']} - {r['code']}")
    else:
        print("🎉 ALL TESTS PASSED!")
    
    print()
    print("💡 NEXT STEPS:")
    if failed > 0:
        print("   1. Start the Flask app: python app.py")
        print("   2. Fix any remaining issues")
        print("   3. Re-run this test")
    else:
        print("   1. Application is ready for production!")
        print("   2. Push to GitHub")
        print("   3. Deploy to server")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{passed/total*100:.1f}%",
            "results": results
        }, f, indent=2)
    
    print(f"📄 Results saved to: {results_file}")

if __name__ == "__main__":
    test_application()
