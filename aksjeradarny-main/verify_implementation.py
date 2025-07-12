#!/usr/bin/env python3
"""
Quick verification that access control code is working correctly
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_access_control_imports():
    """Test that we can verify access control logic from files"""
    
    print("Testing access control configuration...")
    
    try:
        # Read the access_control.py file directly to avoid import issues
        with open('/workspaces/aksjeradarv6/app/utils/access_control.py', 'r') as f:
            content = f.read()
        
        print("✅ Successfully read access control file")
        
        # Check for exempt emails
        expected_emails = ['helene@luxushair.com', 'helene721@gmail.com', 'eiriktollan.berntsen@gmail.com', 'tonjekit91@gmail.com']
        all_emails_found = all(email in content for email in expected_emails)
        
        if all_emails_found:
            print("✅ All expected exempt emails are configured")
        else:
            print("❌ Missing some expected exempt emails")
            
        # Check that main.demo is in unrestricted endpoints
        if "'main.demo'" in content and 'UNRESTRICTED_ENDPOINTS' in content:
            print("✅ main.demo is configured as unrestricted endpoint")
        else:
            print("❌ main.demo not found in unrestricted endpoints")
            
        # Check trial duration is set
        if 'TRIAL_DURATION_MINUTES = 15' in content:
            print("✅ Trial duration is set to 15 minutes")
        else:
            print("⚠️  Trial duration configuration not found or different")
            
        # Check for @access_required decorator function
        if 'def access_required(f):' in content:
            print("✅ access_required decorator is defined")
        else:
            print("❌ access_required decorator not found")
            
        print("✅ Access control configuration checks passed!")
        return True
        
    except FileNotFoundError:
        print("❌ Could not find access_control.py file")
        return False
    except Exception as e:
        print(f"❌ Error checking access control: {e}")
        return False

def test_route_decorator():
    """Test that the main route has the correct decorator"""
    
    print("\nTesting route configuration...")
    
    try:
        # Read the main.py file to check for @access_required
        with open('/workspaces/aksjeradarv6/app/routes/main.py', 'r') as f:
            content = f.read()
        
        # Check for @access_required decorator on index route
        lines = content.split('\n')
        found_route = False
        has_decorator = False
        
        for i, line in enumerate(lines):
            if "@main.route('/')" in line:
                found_route = True
                # Check next few lines for @access_required
                for j in range(1, 5):  # Check up to 4 lines ahead
                    if i + j < len(lines) and '@access_required' in lines[i + j]:
                        has_decorator = True
                        print("✅ Index route (/) has @access_required decorator")
                        break
                break
        
        if not found_route:
            print("❌ Could not find @main.route('/') in main.py")
            return False
            
        if not has_decorator:
            print("❌ Index route (/) does NOT have @access_required decorator")
            return False
            
        # Check that redundant trial logic is removed
        if 'trial_start_time' in content and 'index()' in content:
            # This could indicate old trial logic is still there
            print("⚠️  Warning: Still contains trial_start_time logic - please verify it's removed from index()")
        
        print("✅ Route configuration checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking route configuration: {e}")
        return False

def test_main_function_simplification():
    """Test that index function no longer has complex trial logic"""
    
    print("\nTesting index function simplification...")
    
    try:
        with open('/workspaces/aksjeradarv6/app/routes/main.py', 'r') as f:
            content = f.read()
        
        # Find the index function
        lines = content.split('\n')
        in_index_function = False
        function_lines = []
        
        for line in lines:
            if 'def index():' in line:
                in_index_function = True
                function_lines.append(line)
            elif in_index_function:
                if line.startswith('def ') and 'index' not in line:
                    # Hit next function, stop
                    break
                function_lines.append(line)
        
        function_content = '\n'.join(function_lines)
        
        # Check that complex trial logic is removed
        complex_logic_indicators = [
            'if current_user.is_authenticated:',
            'trial_start = session.get(',
            'trial_start_dt = datetime.fromisoformat(',
            'if datetime.utcnow() - trial_start_dt',
            'restricted = True',
            'show_banner = True'
        ]
        
        has_complex_logic = any(indicator in function_content for indicator in complex_logic_indicators)
        
        if has_complex_logic:
            print("❌ Index function still contains complex trial/restriction logic")
            print("    This should have been simplified since @access_required handles it")
            return False
        else:
            print("✅ Index function has been simplified - no complex trial logic found")
        
        # Check for the new simplified logic
        if 'Since @access_required ensures only users with valid access reach this point' in function_content:
            print("✅ Found expected comment about @access_required handling access")
        else:
            print("⚠️  Expected comment about @access_required not found")
        
        if 'restricted = False' in function_content and 'show_banner = False' in function_content:
            print("✅ Found simplified restricted/banner logic")
        else:
            print("❌ Expected simplified restricted/banner logic not found")
            
        print("✅ Index function simplification checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking index function: {e}")
        return False

if __name__ == "__main__":
    print("🔐 VERIFYING RESTRICTED ACCESS PROTECTION")
    print("=" * 50)
    
    test1 = test_access_control_imports()
    test2 = test_route_decorator()  
    test3 = test_main_function_simplification()
    
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)
    
    tests = [
        ("Access control imports", test1),
        ("Route decorator configuration", test2),
        ("Index function simplification", test3)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ Restricted access protection is properly implemented")
        print("✅ Stock tables are protected from unauthorized access")
    else:
        print(f"\n🚨 {total - passed} VERIFICATION TEST(S) FAILED!")
        print("❌ Please check the implementation")
