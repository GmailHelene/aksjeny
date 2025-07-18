#!/usr/bin/env python3
"""
Test runner for Aksjeradar application
"""
import pytest
import sys
import os

def run_tests():
    """Run all tests with coverage"""
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    print("🧪 Starting Aksjeradar test suite...")
    print(f"📁 Working directory: {current_dir}")
    print(f"🐍 Python version: {sys.version}")
    
    # Test arguments
    args = [
        'tests/',
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker checking
        '-x',  # Stop on first failure for faster debugging
    ]
    
    # Add coverage if available
    try:
        import pytest_cov
        args.extend([
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-fail-under=70'  # Lower threshold for initial testing
        ])
        print("📊 Running tests with coverage...")
    except ImportError:
        print("⚠️  Running tests without coverage (install pytest-cov for coverage)")
    
    # Check if test directory exists
    test_dir = os.path.join(current_dir, 'tests')
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        print("📁 Creating tests directory...")
        os.makedirs(test_dir)
        
        # Create a simple test file if none exist
        init_file = os.path.join(test_dir, '__init__.py')
        with open(init_file, 'w') as f:
            f.write('# Test package\n')
    
    # Run tests
    print("\n🚀 Running tests...\n")
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
        print("💡 Check the output above for details")
    
    return exit_code

if __name__ == '__main__':
    try:
        exit_code = run_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)
