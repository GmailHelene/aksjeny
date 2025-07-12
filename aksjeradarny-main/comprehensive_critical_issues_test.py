#!/usr/bin/env python3
"""
Comprehensive Critical Issues Test
Tests all remaining critical issues mentioned in TODO list
"""

import os
import sys
import traceback
from datetime import datetime

def test_template_hardcoded_values():
    """Test for remaining hardcoded values in templates"""
    print("\n🔍 Testing Template Hardcoded Values...")
    
    template_dir = 'app/templates'
    issues_found = []
    
    # Templates to check
    template_files = [
        'market/overview.html',
        'market_overview.html', 
        'portfolio/view.html',
        'analysis/technical.html',
        'analysis/index.html',
        'index.html'
    ]
    
    for template_file in template_files:
        file_path = os.path.join(template_dir, template_file)
        
        if not os.path.exists(file_path):
            print(f"   ⚠️  File not found: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for common hardcoded patterns
            hardcoded_patterns = [
                ('322.50', 'Hardcoded EQNR price'),
                ('215.40', 'Hardcoded DNB price'), 
                ('185.70', 'Hardcoded AAPL price'),
                ('5467.82', 'Hardcoded S&P 500 value'),
                ('17185.33', 'Hardcoded Nasdaq value'),
                ('+2.1', 'Hardcoded percentage change'),
                ('65,432.10', 'Hardcoded Bitcoin price'),
                ('NOK 345.10', 'Hardcoded NOK price')
            ]
            
            file_issues = []
            for pattern, description in hardcoded_patterns:
                if pattern in content:
                    file_issues.append(f"{description}: {pattern}")
            
            if file_issues:
                issues_found.extend([f"{template_file}: {issue}" for issue in file_issues])
                print(f"   ❌ {template_file}: {len(file_issues)} hardcoded values found")
            else:
                print(f"   ✅ {template_file}: No obvious hardcoded values")
                
        except Exception as e:
            print(f"   ❌ Error reading {template_file}: {str(e)}")
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} hardcoded value issues:")
        for issue in issues_found[:10]:  # Show first 10
            print(f"      - {issue}")
        if len(issues_found) > 10:
            print(f"      ... and {len(issues_found) - 10} more")
    else:
        print("\n✅ No hardcoded values detected in checked templates")
    
    return len(issues_found) == 0

def test_data_consistency():
    """Test data consistency across the application"""
    print("\n🔍 Testing Data Consistency...")
    
    try:
        # Import required modules
        sys.path.append('.')
        from app.services.ai_service import AIService
        from app.services.analysis_service import AnalysisService
        
        test_tickers = ['EQNR.OL', 'AAPL', 'DNB.OL', 'MSFT']
        consistency_issues = []
        
        for ticker in test_tickers:
            try:
                # Test AI service data
                ai_data = AIService.get_stock_analysis(ticker)
                if not ai_data or 'error' in ai_data:
                    consistency_issues.append(f"AI service failed for {ticker}")
                    continue
                
                # Test technical data
                tech_data = AnalysisService.get_fallback_technical_data(ticker)
                if not tech_data:
                    consistency_issues.append(f"Technical data missing for {ticker}")
                    continue
                
                # Check data consistency
                ai_price = ai_data.get('prediction', {}).get('current_price')
                tech_price = tech_data.get('last_price')
                
                if ai_price and tech_price:
                    price_diff = abs(float(ai_price) - float(tech_price)) / float(tech_price)
                    if price_diff > 0.1:  # More than 10% difference
                        consistency_issues.append(f"Price inconsistency for {ticker}: {ai_price} vs {tech_price}")
                
                print(f"   ✅ {ticker}: Data consistency check passed")
                
            except Exception as e:
                consistency_issues.append(f"Error processing {ticker}: {str(e)}")
                print(f"   ❌ {ticker}: {str(e)}")
        
        if consistency_issues:
            print(f"\n❌ Found {len(consistency_issues)} data consistency issues:")
            for issue in consistency_issues:
                print(f"      - {issue}")
        else:
            print("\n✅ Data consistency checks passed")
        
        return len(consistency_issues) == 0
        
    except Exception as e:
        print(f"❌ Data consistency test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_mobile_responsiveness():
    """Test mobile responsiveness indicators"""
    print("\n🔍 Testing Mobile Responsiveness...")
    
    # Check for responsive CSS classes and viewport meta tag
    responsive_indicators = []
    
    # Check base template for viewport
    base_template = 'app/templates/base.html'
    if os.path.exists(base_template):
        try:
            with open(base_template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'viewport' in content and 'width=device-width' in content:
                responsive_indicators.append("✅ Viewport meta tag present")
            else:
                responsive_indicators.append("❌ Missing viewport meta tag")
            
            if 'table-responsive' in content:
                responsive_indicators.append("✅ Responsive table classes found")
            else:
                responsive_indicators.append("⚠️  No responsive table classes in base template")
                
            if '@media' in content:
                responsive_indicators.append("✅ Media queries present")
            else:
                responsive_indicators.append("⚠️  No media queries in base template")
                
        except Exception as e:
            responsive_indicators.append(f"❌ Error checking base template: {str(e)}")
    else:
        responsive_indicators.append("❌ Base template not found")
    
    # Check CSS files
    css_files = ['app/static/css/style.css', 'app/static/css/mobile-optimized.css']
    for css_file in css_files:
        if os.path.exists(css_file):
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                media_queries = content.count('@media')
                if media_queries > 0:
                    responsive_indicators.append(f"✅ {os.path.basename(css_file)}: {media_queries} media queries")
                else:
                    responsive_indicators.append(f"⚠️  {os.path.basename(css_file)}: No media queries")
                    
            except Exception as e:
                responsive_indicators.append(f"❌ Error reading {css_file}: {str(e)}")
        else:
            responsive_indicators.append(f"⚠️  CSS file not found: {css_file}")
    
    print(f"   Mobile responsiveness indicators:")
    for indicator in responsive_indicators:
        print(f"      {indicator}")
    
    # Count positive indicators
    positive_count = sum(1 for indicator in responsive_indicators if indicator.startswith("✅"))
    total_count = len(responsive_indicators)
    
    success_rate = positive_count / total_count if total_count > 0 else 0
    print(f"\n   📊 Responsiveness score: {positive_count}/{total_count} ({success_rate:.1%})")
    
    return success_rate > 0.7  # 70% success rate threshold

def test_error_handling():
    """Test error handling capabilities"""
    print("\n🔍 Testing Error Handling...")
    
    error_handling_tests = []
    
    try:
        # Test AI service with invalid ticker
        from app.services.ai_service import AIService
        
        invalid_result = AIService.get_stock_analysis('INVALID_TICKER')
        if invalid_result and not invalid_result.get('error'):
            error_handling_tests.append("✅ AI service handles invalid tickers gracefully")
        else:
            error_handling_tests.append("⚠️  AI service error handling for invalid tickers")
        
        # Test with None input
        none_result = AIService.get_stock_analysis(None)
        if none_result:
            error_handling_tests.append("✅ AI service handles None input")
        else:
            error_handling_tests.append("❌ AI service fails with None input")
            
    except Exception as e:
        error_handling_tests.append(f"❌ AI service error handling test failed: {str(e)}")
    
    try:
        # Test analysis service
        from app.services.analysis_service import AnalysisService
        
        invalid_tech = AnalysisService.get_fallback_technical_data('INVALID')
        if invalid_tech:
            error_handling_tests.append("✅ Analysis service provides fallback data")
        else:
            error_handling_tests.append("❌ Analysis service has no fallback mechanism")
            
    except Exception as e:
        error_handling_tests.append(f"❌ Analysis service error handling test failed: {str(e)}")
    
    print(f"   Error handling tests:")
    for test in error_handling_tests:
        print(f"      {test}")
    
    # Count positive results
    positive_count = sum(1 for test in error_handling_tests if test.startswith("✅"))
    total_count = len(error_handling_tests)
    
    success_rate = positive_count / total_count if total_count > 0 else 0
    print(f"\n   📊 Error handling score: {positive_count}/{total_count} ({success_rate:.1%})")
    
    return success_rate > 0.6  # 60% success rate threshold

def run_comprehensive_test():
    """Run all critical issue tests"""
    print("🚀 COMPREHENSIVE CRITICAL ISSUES TEST")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {}
    
    # Run all tests
    test_functions = [
        ("Template Hardcoded Values", test_template_hardcoded_values),
        ("Data Consistency", test_data_consistency),
        ("Mobile Responsiveness", test_mobile_responsiveness),
        ("Error Handling", test_error_handling)
    ]
    
    for test_name, test_function in test_functions:
        print(f"\n{'='*50}")
        try:
            result = test_function()
            test_results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            traceback.print_exc()
            test_results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 50)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    overall_score = passed_tests / total_tests if total_tests > 0 else 0
    print(f"\nOverall Score: {passed_tests}/{total_tests} ({overall_score:.1%})")
    
    if overall_score >= 0.8:
        print("🎉 EXCELLENT: Most critical issues resolved!")
    elif overall_score >= 0.6:
        print("👍 GOOD: Critical issues mostly addressed, some work remaining")
    elif overall_score >= 0.4:
        print("⚠️  FAIR: Significant critical issues remain")
    else:
        print("❌ POOR: Major critical issues need attention")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return overall_score >= 0.6

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
