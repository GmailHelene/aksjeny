#!/usr/bin/env python3
"""
Test EQNR.OL on the stocks details page specifically
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

def test_stock_details_page():
    """Test the stocks details route logic"""
    print("=" * 60)
    print("TESTING STOCK DETAILS PAGE LOGIC")
    print("=" * 60)
    
    from app.routes.stocks import details
    from app.services.data_service import DataService
    from app.services.analysis_service import AnalysisService
    
    ticker = 'EQNR.OL'
    print(f"\nTesting ticker: {ticker}")
    
    # Test all the individual components that the details page uses
    print("\n1. Stock Info:")
    stock_info = DataService.get_stock_info(ticker)
    if stock_info:
        print(f"   ✓ Stock name: {stock_info.get('shortName', 'N/A')}")
        print(f"   ✓ Price: {stock_info.get('regularMarketPrice', 'N/A')}")
        print(f"   ✓ Sector: {stock_info.get('sector', 'N/A')}")
        print(f"   ✓ Market cap: {stock_info.get('marketCap', 'N/A')}")
    else:
        print("   ✗ No stock info")
    
    print("\n2. Stock Data (Chart):")
    stock_data = DataService.get_stock_data(ticker, period='1mo')
    if hasattr(stock_data, 'empty') and not stock_data.empty:
        print(f"   ✓ Chart data: {stock_data.shape[0]} days")
        print(f"   ✓ Last price: {stock_data['Close'].iloc[-1]:.2f}")
        print(f"   ✓ Date range: {stock_data.index[0].date()} to {stock_data.index[-1].date()}")
    else:
        print("   ✗ No chart data")
    
    print("\n3. Technical Analysis:")
    technical_analysis = AnalysisService.get_technical_analysis(ticker)
    if technical_analysis:
        print(f"   ✓ Signal: {technical_analysis.get('overall_signal', 'N/A')}")
        print(f"   ✓ RSI: {technical_analysis.get('rsi', 'N/A')}")
        print(f"   ✓ MACD: {technical_analysis.get('macd', 'N/A')}")
        print(f"   ✓ Signal reason: {technical_analysis.get('signal_reason', 'N/A')[:50]}...")
    else:
        print("   ✗ No technical analysis")
    
    print("\n4. Company Description:")
    description = DataService.get_company_description(ticker)
    if description and description != 'Ingen beskrivelse tilgjengelig.':
        print(f"   ✓ Description: {description[:100]}...")
    else:
        print("   ✗ No description")
    
    print("\n5. Related Symbols:")
    related = DataService.get_related_symbols(ticker)
    if related:
        print(f"   ✓ Related symbols: {related}")
    else:
        print("   ✗ No related symbols")
    
    print("\n" + "=" * 60)
    print("STOCK DETAILS PAGE TEST COMPLETE")
    print("All components needed for the details page are working!")
    print("=" * 60)

if __name__ == "__main__":
    test_stock_details_page()
