#!/usr/bin/env python3
"""
Aksjeradar Complete Test Suite Runner
Runs all test scripts in sequence and generates a comprehensive report
"""
import os
import sys
import subprocess
import time
import json
from datetime import datetime
import argparse

class Color:
    """Terminal color codes for pretty output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a formatted header"""
    print(f"\n{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{message.center(80)}{Color.ENDC}")
    print(f"{Color.HEADER}{Color.BOLD}{'=' * 80}{Color.ENDC}\n")

def run_test(script_path, base_url, timeout=300):
    """Run a test script and return the result"""
    print(f"{Color.BLUE}Running: {os.path.basename(script_path)}{Color.ENDC}")
    start_time = time.time()
    
    try:
        process = subprocess.run(
            [sys.executable, script_path, '--base-url', base_url],
            check=False,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        
        duration = time.time() - start_time
        success = process.returncode == 0
        
        if success:
            status = f"{Color.GREEN}PASSED{Color.ENDC}"
        else:
            status = f"{Color.RED}FAILED{Color.ENDC}"
        
        print(f"{status} in {duration:.2f} seconds (exit code: {process.returncode})")
        
        return {
            "script": os.path.basename(script_path),
            "success": success,
            "duration": duration,
            "exit_code": process.returncode,
            "output": process.stdout,
            "error": process.stderr
        }
    except subprocess.TimeoutExpired:
        print(f"{Color.RED}TIMEOUT after {timeout} seconds{Color.ENDC}")
        return {
            "script": os.path.basename(script_path),
            "success": False,
            "duration": timeout,
            "exit_code": -1,
            "output": "",
            "error": f"Timeout after {timeout} seconds"
        }
    except Exception as e:
        print(f"{Color.RED}ERROR: {str(e)}{Color.ENDC}")
        return {
            "script": os.path.basename(script_path),
            "success": False,
            "duration": time.time() - start_time,
            "exit_code": -2,
            "output": "",
            "error": str(e)
        }

def run_all_tests(base_url, timeout=300):
    """Run all test scripts and generate a report"""
    print_header("Aksjeradar Complete Test Suite")
    print(f"Testing against: {base_url}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # Define test scripts to run
    test_scripts = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth_system_test.py"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscription_flow_test.py"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "comprehensive_endpoint_test.py")
    ]
    
    # Run each test script
    results = []
    for script in test_scripts:
        if os.path.exists(script):
            result = run_test(script, base_url, timeout)
            results.append(result)
        else:
            print(f"{Color.YELLOW}WARNING: Script not found: {script}{Color.ENDC}")
    
    # Calculate overall statistics
    total_duration = time.time() - start_time
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    # Print summary
    print_header("Test Suite Summary")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {Color.GREEN}{passed}{Color.ENDC}")
    print(f"Failed: {Color.RED}{failed}{Color.ENDC}")
    print(f"Total duration: {total_duration:.2f} seconds")
    print()
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "total_duration": total_duration,
        "results": results
    }
    
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Detailed report saved to: {report_file}")
    
    return passed == len(results)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Aksjeradar Complete Test Suite Runner')
    parser.add_argument('--base-url', default='http://localhost:5000', help='Base URL to test against')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds for each test script')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    success = run_all_tests(args.base_url, args.timeout)
    sys.exit(0 if success else 1)
