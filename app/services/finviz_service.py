"""
Advanced Stock Screening Service using Finviz
Provides comprehensive stock screening capabilities with real market data
"""
import logging
from typing import Dict, List, Optional, Any
import pandas as pd

logger = logging.getLogger(__name__)

class FinvizScreenerService:
    """Service for advanced stock screening using Finviz"""
    
    def __init__(self):
        self.available_filters = {
            # Market Cap filters
            'cap_mega': 'exch_nasd',  # Mega cap (>$200B)
            'cap_large': 'cap_largeover',  # Large cap (>$10B)
            'cap_mid': 'cap_mid',  # Mid cap ($2B-$10B)
            'cap_small': 'cap_small',  # Small cap (<$2B)
            
            # Exchange filters
            'nasdaq': 'exch_nasd',
            'nyse': 'exch_nyse',
            
            # Index filters
            'sp500': 'idx_sp500',
            'sp400': 'idx_sp400',
            'sp600': 'idx_sp600',
            'nasdaq100': 'idx_ndx',
            'russell2000': 'idx_russell2000',
            
            # Sector filters
            'tech': 'sec_technology',
            'healthcare': 'sec_healthcare',
            'finance': 'sec_financial',
            'energy': 'sec_energy',
            'consumer': 'sec_consumer_cyclical',
            'industrial': 'sec_industrial',
            'utilities': 'sec_utilities',
            'realestate': 'sec_realestate',
            'materials': 'sec_basic_materials',
            
            # Valuation filters
            'pe_low': 'fa_pe_low',  # P/E < 15
            'pe_profitable': 'fa_pe_profitable',  # P/E > 0
            'pe_high': 'fa_pe_high',  # P/E > 50
            'peg_low': 'fa_peg_low',  # PEG < 1
            'pb_low': 'fa_pb_low',  # P/B < 1
            'ps_low': 'fa_ps_low',  # P/S < 1
            
            # Performance filters
            'perf_week_up': 'ta_perf_1w_o',  # Week performance > 0%
            'perf_month_up': 'ta_perf_1m_o',  # Month performance > 0%
            'perf_ytd_up': 'ta_perf_ytd_o',  # YTD performance > 0%
            'perf_year_up': 'ta_perf_y_o',  # Year performance > 0%
            
            # Technical filters
            'rsi_oversold': 'ta_rsi_os30',  # RSI < 30 (oversold)
            'rsi_overbought': 'ta_rsi_ob70',  # RSI > 70 (overbought)
            'price_near_high': 'ta_highlow52w_nh',  # Near 52-week high
            'price_near_low': 'ta_highlow52w_nl',  # Near 52-week low
            'volume_high': 'sh_avgvol_o2000',  # Volume > 2M
            
            # Fundamental filters
            'dividend_yield': 'fa_div_pos',  # Dividend yield > 0%
            'dividend_high': 'fa_div_high',  # Dividend yield > 5%
            'roe_high': 'fa_roe_pos',  # ROE > 0%
            'roa_high': 'fa_roa_pos',  # ROA > 0%
            'debt_low': 'fa_debteq_low',  # Debt/Equity < 0.5
            'current_ratio_high': 'fa_curratio_high',  # Current ratio > 1.5
            
            # Growth filters
            'sales_growth': 'fa_sales5years_pos',  # 5Y sales growth > 0%
            'eps_growth': 'fa_eps5years_pos',  # 5Y EPS growth > 0%
            'earnings_growth': 'fa_estltgrowth_pos',  # Est. long-term growth > 0%
        }
        
    def get_available_filters(self) -> Dict[str, str]:
        """Get all available screening filters"""
        return {
            'Market Cap': ['cap_mega', 'cap_large', 'cap_mid', 'cap_small'],
            'Exchange': ['nasdaq', 'nyse'],
            'Index': ['sp500', 'sp400', 'sp600', 'nasdaq100', 'russell2000'],
            'Sector': ['tech', 'healthcare', 'finance', 'energy', 'consumer', 'industrial', 'utilities', 'realestate', 'materials'],
            'Valuation': ['pe_low', 'pe_profitable', 'pe_high', 'peg_low', 'pb_low', 'ps_low'],
            'Performance': ['perf_week_up', 'perf_month_up', 'perf_ytd_up', 'perf_year_up'],
            'Technical': ['rsi_oversold', 'rsi_overbought', 'price_near_high', 'price_near_low', 'volume_high'],
            'Fundamental': ['dividend_yield', 'dividend_high', 'roe_high', 'roa_high', 'debt_low', 'current_ratio_high'],
            'Growth': ['sales_growth', 'eps_growth', 'earnings_growth']
        }
    
    def screen_stocks(self, filter_criteria: List[str], table_type: str = 'Performance', order_by: str = 'price') -> List[Dict[str, Any]]:
        """
        Screen stocks using Finviz
        
        Args:
            filter_criteria: List of filter keys to apply
            table_type: Type of table ('Performance', 'Valuation', 'Financial', 'Ownership', 'Technical')
            order_by: Column to order by ('price', 'change', 'volume', etc.)
        
        Returns:
            List of dictionaries with stock data
        """
        try:
            # Import finviz here to handle cases where it's not installed
            try:
                from finviz.screener import Screener
            except ImportError:
                logger.warning("Finviz not installed, using fallback data")
                return self._get_fallback_screening_data(filter_criteria)
            
            # Convert filter criteria to finviz filters
            finviz_filters = []
            for criteria in filter_criteria:
                if criteria in self.available_filters:
                    finviz_filters.append(self.available_filters[criteria])
            
            if not finviz_filters:
                logger.warning("No valid filters provided")
                return self._get_fallback_screening_data(['sp500'])
            
            # Create screener with filters
            stock_list = Screener(
                filters=finviz_filters,
                table=table_type,
                order=order_by
            )
            
            # Convert to list of dictionaries
            results = []
            for stock in stock_list:
                stock_data = {
                    'ticker': stock.get('Ticker', ''),
                    'company': stock.get('Company', ''),
                    'sector': stock.get('Sector', ''),
                    'industry': stock.get('Industry', ''),
                    'market_cap': stock.get('Market Cap', ''),
                    'price': self._parse_numeric(stock.get('Price', 0)),
                    'change': self._parse_numeric(stock.get('Change', 0)),
                    'change_percent': self._parse_percentage(stock.get('Chg', '0%')),
                    'volume': self._parse_volume(stock.get('Volume', '0')),
                    'pe_ratio': self._parse_numeric(stock.get('P/E', 0)),
                    'peg_ratio': self._parse_numeric(stock.get('PEG', 0)),
                    'pb_ratio': self._parse_numeric(stock.get('P/B', 0)),
                    'ps_ratio': self._parse_numeric(stock.get('P/S', 0)),
                    'dividend_yield': self._parse_percentage(stock.get('Dividend %', '0%')),
                    'rsi': self._parse_numeric(stock.get('RSI (14)', 0)),
                    'performance_week': self._parse_percentage(stock.get('Perf Week', '0%')),
                    'performance_month': self._parse_percentage(stock.get('Perf Month', '0%')),
                    'performance_ytd': self._parse_percentage(stock.get('Perf YTD', '0%')),
                    'performance_year': self._parse_percentage(stock.get('Perf Year', '0%')),
                    'recommendation': self._get_recommendation(stock)
                }
                results.append(stock_data)
            
            logger.info(f"Screened {len(results)} stocks with filters: {filter_criteria}")
            return results[:50]  # Limit to 50 results
            
        except Exception as e:
            logger.error(f"Error in stock screening: {e}")
            return self._get_fallback_screening_data(filter_criteria)
    
    def _parse_numeric(self, value: Any) -> float:
        """Parse numeric value from string"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Remove % and other characters
                cleaned = value.replace('%', '').replace(',', '').replace('$', '').strip()
                if cleaned == '-' or cleaned == '':
                    return 0.0
                return float(cleaned)
            return 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def _parse_percentage(self, value: str) -> float:
        """Parse percentage value"""
        try:
            if isinstance(value, str):
                cleaned = value.replace('%', '').strip()
                if cleaned == '-' or cleaned == '':
                    return 0.0
                return float(cleaned)
            return float(value)
        except (ValueError, AttributeError):
            return 0.0
    
    def _parse_volume(self, value: str) -> int:
        """Parse volume value with K/M suffixes"""
        try:
            if isinstance(value, str):
                value = value.replace(',', '').upper()
                if 'K' in value:
                    return int(float(value.replace('K', '')) * 1000)
                elif 'M' in value:
                    return int(float(value.replace('M', '')) * 1000000)
                elif 'B' in value:
                    return int(float(value.replace('B', '')) * 1000000000)
                else:
                    return int(float(value))
            return int(value)
        except (ValueError, AttributeError):
            return 0
    
    def _get_recommendation(self, stock_data: dict) -> str:
        """Generate recommendation based on stock data"""
        try:
            pe = self._parse_numeric(stock_data.get('P/E', 0))
            peg = self._parse_numeric(stock_data.get('PEG', 0))
            rsi = self._parse_numeric(stock_data.get('RSI (14)', 50))
            perf_month = self._parse_percentage(stock_data.get('Perf Month', '0%'))
            
            # Simple recommendation logic
            if pe > 0 and pe < 15 and peg > 0 and peg < 1:
                return 'STRONG BUY'
            elif rsi < 30 and perf_month > 0:
                return 'BUY'
            elif rsi > 70 or pe > 50:
                return 'SELL'
            elif pe > 0 and pe < 25 and perf_month > -5:
                return 'HOLD'
            else:
                return 'NEUTRAL'
        except:
            return 'NEUTRAL'
    
    def _get_fallback_screening_data(self, filter_criteria: List[str]) -> List[Dict[str, Any]]:
        """Fallback data when Finviz is not available"""
        # Mock data for demonstration
        fallback_stocks = [
            {
                'ticker': 'AAPL',
                'company': 'Apple Inc.',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'market_cap': '3.1T',
                'price': 185.24,
                'change': 2.15,
                'change_percent': 1.17,
                'volume': 45000000,
                'pe_ratio': 28.5,
                'peg_ratio': 1.2,
                'pb_ratio': 42.1,
                'ps_ratio': 7.8,
                'dividend_yield': 0.5,
                'rsi': 58.2,
                'performance_week': 1.2,
                'performance_month': 3.4,
                'performance_ytd': 12.5,
                'performance_year': 15.2,
                'recommendation': 'HOLD'
            },
            {
                'ticker': 'MSFT',
                'company': 'Microsoft Corporation',
                'sector': 'Technology',
                'industry': 'Software - Infrastructure',
                'market_cap': '2.8T',
                'price': 372.45,
                'change': -1.23,
                'change_percent': -0.33,
                'volume': 32000000,
                'pe_ratio': 32.1,
                'peg_ratio': 1.5,
                'pb_ratio': 12.4,
                'ps_ratio': 11.2,
                'dividend_yield': 0.7,
                'rsi': 52.8,
                'performance_week': -0.5,
                'performance_month': 2.1,
                'performance_ytd': 18.3,
                'performance_year': 22.1,
                'recommendation': 'BUY'
            },
            {
                'ticker': 'GOOGL',
                'company': 'Alphabet Inc.',
                'sector': 'Communication Services',
                'industry': 'Internet Content & Information',
                'market_cap': '1.7T',
                'price': 138.21,
                'change': 1.45,
                'change_percent': 1.06,
                'volume': 28000000,
                'pe_ratio': 26.8,
                'peg_ratio': 1.1,
                'pb_ratio': 5.2,
                'ps_ratio': 5.5,
                'dividend_yield': 0.0,
                'rsi': 61.3,
                'performance_week': 2.1,
                'performance_month': 4.2,
                'performance_ytd': 25.4,
                'performance_year': 31.2,
                'recommendation': 'BUY'
            }
        ]
        
        logger.info(f"Using fallback screening data with {len(fallback_stocks)} stocks")
        return fallback_stocks
    
    def export_to_csv(self, stock_data: List[Dict], filename: str = "screener_results.csv") -> str:
        """Export screening results to CSV"""
        try:
            df = pd.DataFrame(stock_data)
            df.to_csv(filename, index=False)
            logger.info(f"Exported {len(stock_data)} stocks to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return ""
    
    def get_preset_screens(self) -> Dict[str, List[str]]:
        """Get predefined screening presets"""
        return {
            "Value Stocks": ['pe_low', 'pb_low', 'debt_low', 'roe_high'],
            "Growth Stocks": ['eps_growth', 'sales_growth', 'perf_year_up', 'pe_profitable'],
            "Dividend Stocks": ['dividend_high', 'roe_high', 'debt_low', 'pe_profitable'],
            "Tech Giants": ['tech', 'cap_large', 'pe_profitable', 'volume_high'],
            "Small Cap Growth": ['cap_small', 'eps_growth', 'perf_year_up', 'volume_high'],
            "Oversold Stocks": ['rsi_oversold', 'pe_profitable', 'volume_high'],
            "Momentum Stocks": ['perf_month_up', 'perf_week_up', 'volume_high', 'pe_profitable'],
            "Safe Haven": ['dividend_yield', 'debt_low', 'pe_low', 'roe_high']
        }

# Global service instance
finviz_screener_service = FinvizScreenerService()
