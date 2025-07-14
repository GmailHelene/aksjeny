import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import time
import logging
import warnings
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

# Import rate limiter
try:
    from .rate_limiter import rate_limiter
    from .simple_cache import simple_cache
except ImportError:
    # Fallback if rate limiter is not available
    class DummyRateLimiter:
        def wait_if_needed(self, api_name='default'):
            time.sleep(0.5)  # Simple fallback delay
    class DummyCache:
        def get(self, key, cache_type='default'):
            return None
        def set(self, key, value, cache_type='default'):
            pass
    rate_limiter = DummyRateLimiter()
    simple_cache = DummyCache()
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

# Suppress yfinance warnings and errors
warnings.filterwarnings('ignore')
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# Import cache service
try:
    from .cache_service import get_cache_service
except ImportError:
    get_cache_service = None

# Define some constants for demo data
OSLO_BORS_TICKERS = [
    "EQNR.OL", "DNB.OL", "TEL.OL", "YAR.OL", "NHY.OL", "AKSO.OL", 
    "MOWI.OL", "ORK.OL", "SALM.OL", "AKERBP.OL", "SUBC.OL", "KAHOT.OL",
    "BAKKA.OL", "SCATC.OL", "MPCC.OL", "GOGL.OL", "FRONTLINE.OL", "FLEX.OL",
    "AKER.OL", "SUBSEA7.OL", "OKEA.OL", "VARENERGI.OL", "BORR.OL", "ARCHER.OL",
    "NEL.OL", "REC.OL", "SCANA.OL", "THIN.OL", "OTELLO.OL", "AEGA.OL", "BEWI.OL", "BONHR.OL",
    "BOUVET.OL", "BWLPG.OL", "CIRCA.OL", "DLTX.OL", "ELOP.OL", "ENTRA.OL", "FKRAFT.OL", "GJENSIDIGE.OL",
    "GRIEG.OL", "HAFNIA.OL", "HUNTER.OL", "IDEX.OL", "INSR.OL", "KID.OL", "LSG.OL", "MEDI.OL",
    "NAPA.OL", "NSKOG.OL", "OCEAN.OL", "PCIB.OL", "QFREE.OL", "REACH.OL", "SAGA.OL", "SCHA.OL",
    "CRAYON.OL", "AUTOSTORE.OL", "XXLASA.OL", "KOMPLETT.OL", "EUROPRIS.OL", "KITRON.OL"
]

GLOBAL_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", 
    "JPM", "BAC", "JNJ", "V", "WMT", "PG", "UNH", "HD", "MA",
    "DIS", "ADBE", "NFLX", "CRM", "PYPL", "INTC", "CMCSA", "PEP",
    "T", "ABT", "TMO", "COST", "AVGO", "ACN", "TXN", "LLY", "MDT", "NKE",
    "ORCL", "XOM", "CVX", "KO", "MRK", "ABBV", "PFE", "VZ", "CSCO",
    "IBM", "AMD", "QCOM", "AMGN", "GILD", "SBUX", "MCD", "HON", "UPS",
    "CAT", "GS", "MS", "AXP", "MMM", "BA", "GE", "F", "GM", "UBER",
    "LYFT", "SNAP", "TWTR", "SPOT", "ZM", "DOCU", "ROKU", "SQ", "SHOP", "CRWD",
    "SNOW", "PLTR", "COIN", "RBLX", "HOOD", "RIVN", "LCID", "SOFI", "AFRM", "UPST",
    "DKNG", "PENN", "MGM", "WYNN", "LVS", "NCLH", "RCL", "CCL", "DAL", "UAL",
    "AAL", "LUV", "JBLU", "ALK", "SAVE", "SPCE", "ARKK", "QQQ", "SPY", "IWM",
    "GLD", "SLV", "TLT", "HYG", "LQD", "EEM", "VTI", "VXUS", "BND", "VTEB"
]

# Fallback data for when API calls fail
FALLBACK_OSLO_DATA = {
    'EQNR.OL': {
        'ticker': 'EQNR.OL',
        'name': 'Equinor ASA',
        'last_price': 342.55,
        'change': 2.30,
        'change_percent': 0.68,
        'volume': 3200000,
        'signal': 'BUY',
        'market_cap': 1100000000000,
        'sector': 'Energi',
        'rsi': 45.2
    },
    'DNB.OL': {
        'ticker': 'DNB.OL',
        'name': 'DNB Bank ASA',
        'last_price': 212.80,
        'change': -1.20,
        'change_percent': -0.56,
        'volume': 1500000,
        'signal': 'HOLD',
        'market_cap': 350000000000,
        'sector': 'Finansielle tjenester',
        'rsi': 52.1
    },
    'TEL.OL': {
        'ticker': 'TEL.OL',
        'name': 'Telenor ASA',
        'last_price': 125.90,
        'change': -2.10,
        'change_percent': -1.64,
        'volume': 1200000,
        'signal': 'SELL',
        'market_cap': 180000000000,
        'sector': 'Kommunikasjonstjenester',
        'rsi': 72.3
    },
    'YAR.OL': {
        'ticker': 'YAR.OL',
        'name': 'Yara International ASA',
        'last_price': 456.20,
        'change': 3.80,
        'change_percent': 0.84,
        'volume': 800000,
        'signal': 'BUY',
        'market_cap': 120000000000,
        'sector': 'Materialer',
        'rsi': 38.7
    },
    'NHY.OL': {
        'ticker': 'NHY.OL',
        'name': 'Norsk Hydro ASA',
        'last_price': 67.85,
        'change': 0.95,
        'change_percent': 1.42,
        'volume': 2100000,
        'signal': 'BUY',
        'market_cap': 140000000000,
        'sector': 'Materialer',
        'rsi': 41.5
    },
    'MOWI.OL': {
        'ticker': 'MOWI.OL',
        'name': 'Mowi ASA',
        'last_price': 198.50,
        'change': 2.30,
        'change_percent': 1.17,
        'volume': 950000,
        'signal': 'BUY',
        'market_cap': 105000000000,
        'sector': 'Forbruksvarer',
        'rsi': 44.8
    },
    'AKERBP.OL': {
        'ticker': 'AKERBP.OL',
        'name': 'Aker BP ASA',
        'last_price': 289.40,
        'change': -1.80,
        'change_percent': -0.62,
        'volume': 1300000,
        'signal': 'HOLD',
        'market_cap': 190000000000,
        'sector': 'Energi',
        'rsi': 58.2
    },
    'SUBC.OL': {
        'ticker': 'SUBC.OL',
        'name': 'Subsea 7 SA',
        'last_price': 156.20,
        'change': 3.40,
        'change_percent': 2.23,
        'volume': 780000,
        'signal': 'BUY',
        'market_cap': 47000000000,
        'sector': 'Energi',
        'rsi': 35.9
    },
    'SCATC.OL': {
        'ticker': 'SCATC.OL',
        'name': 'Scatec ASA',
        'last_price': 89.60,
        'change': -2.10,
        'change_percent': -2.29,
        'volume': 650000,
        'signal': 'SELL',
        'market_cap': 14000000000,
        'sector': 'Forsyning',
        'rsi': 75.1
    },
    'AKER.OL': {
        'ticker': 'AKER.OL',
        'name': 'Aker ASA',
        'last_price': 567.00,
        'change': 8.50,
        'change_percent': 1.52,
        'volume': 420000,
        'signal': 'BUY',
        'market_cap': 45000000000,
        'sector': 'Industri',
        'rsi': 42.3
    },
    'AUTOSTORE.OL': {
        'ticker': 'AUTOSTORE.OL',
        'name': 'AutoStore Holdings Ltd',
        'last_price': 12.45,
        'change': 0.25,
        'change_percent': 2.05,
        'volume': 2800000,
        'signal': 'BUY',
        'market_cap': 27000000000,
        'sector': 'Teknologi',
        'rsi': 39.6
    },
    'XXLASA.OL': {
        'ticker': 'XXLASA.OL',
        'name': 'XXL ASA',
        'last_price': 18.90,
        'change': -0.45,
        'change_percent': -2.32,
        'volume': 890000,
        'signal': 'HOLD',
        'market_cap': 3400000000,
        'sector': 'Forbrukerdiskresjonær',
        'rsi': 61.4
    },
    'KOMPLETT.OL': {
        'ticker': 'KOMPLETT.OL',
        'name': 'Komplett ASA',
        'last_price': 21.50,
        'change': 0.80,
        'change_percent': 3.86,
        'volume': 650000,
        'signal': 'BUY',
        'market_cap': 2800000000,
        'sector': 'Forbrukerdiskresjonær',
        'rsi': 35.2
    },
    'EUROPRIS.OL': {
        'ticker': 'EUROPRIS.OL',
        'name': 'Europris ASA',
        'last_price': 58.40,
        'change': -1.20,
        'change_percent': -2.01,
        'volume': 420000,
        'signal': 'HOLD',
        'market_cap': 9500000000,
        'sector': 'Forbrukerdiskresjonær',
        'rsi': 68.3
    },
    'KITRON.OL': {
        'ticker': 'KITRON.OL',
        'name': 'Kitron ASA',
        'last_price': 24.70,
        'change': 0.30,
        'change_percent': 1.23,
        'volume': 580000,
        'signal': 'BUY',
        'market_cap': 5100000000,
        'sector': 'Teknologi',
        'rsi': 45.8
    },
    'NEL.OL': {
        'ticker': 'NEL.OL',
        'name': 'Nel ASA',
        'last_price': 8.45,
        'change': -0.25,
        'change_percent': -2.87,
        'volume': 4200000,
        'signal': 'HOLD',
        'market_cap': 14500000000,
        'sector': 'Industri',
        'rsi': 72.1
    },
    'REC.OL': {
        'ticker': 'REC.OL',
        'name': 'REC Silicon ASA',
        'last_price': 4.82,
        'change': 0.12,
        'change_percent': 2.55,
        'volume': 1800000,
        'signal': 'BUY',
        'market_cap': 2100000000,
        'sector': 'Teknologi',
        'rsi': 38.7
    },
    'KAHOT.OL': {
        'ticker': 'KAHOT.OL',
        'name': 'Kahoot! ASA',
        'last_price': 18.65,
        'change': -0.55,
        'change_percent': -2.86,
        'volume': 950000,
        'signal': 'HOLD',
        'market_cap': 3200000000,
        'sector': 'Teknologi',
        'rsi': 65.4
    },
    'BAKKA.OL': {
        'ticker': 'BAKKA.OL',
        'name': 'Bakkafrost P/F',
        'last_price': 485.50,
        'change': 8.50,
        'change_percent': 1.78,
        'volume': 280000,
        'signal': 'BUY',
        'market_cap': 27500000000,
        'sector': 'Forbruksvarer',
        'rsi': 41.9
    },
    'SCATC.OL': {
        'ticker': 'SCATC.OL',
        'name': 'SalMar ASA',
        'last_price': 675.50,
        'change': 12.50,
        'change_percent': 1.89,
        'volume': 520000,
        'signal': 'BUY',
        'market_cap': 87500000000,
        'sector': 'Forbruksvarer',
        'rsi': 43.2
    },
    'VARENERGI.OL': {
        'ticker': 'VARENERGI.OL',
        'name': 'Var Energi ASA',
        'last_price': 38.45,
        'change': 0.95,
        'change_percent': 2.53,
        'volume': 2100000,
        'signal': 'BUY',
        'market_cap': 62000000000,
        'sector': 'Energi',
        'rsi': 39.8
    },
    'FRONTLINE.OL': {
        'ticker': 'FRONTLINE.OL',
        'name': 'Frontline Ltd',
        'last_price': 178.20,
        'change': -3.80,
        'change_percent': -2.09,
        'volume': 890000,
        'signal': 'HOLD',
        'market_cap': 35000000000,
        'sector': 'Energi',
        'rsi': 68.7
    },
    'WALLEY.OL': {
        'ticker': 'WALLEY.OL',
        'name': 'Walley AB',
        'last_price': 45.30,
        'change': 1.20,
        'change_percent': 2.72,
        'volume': 420000,
        'signal': 'BUY',
        'market_cap': 8500000000,
        'sector': 'Finansielle tjenester',
        'rsi': 42.1
    }
}

FALLBACK_GLOBAL_DATA = {
    'AAPL': {
        'ticker': 'AAPL',
        'name': 'Apple Inc.',
        'last_price': 185.70,
        'change': 1.23,
        'change_percent': 0.67,
        'volume': 50000000,
        'signal': 'BUY',
        'market_cap': 2900000000000,
        'sector': 'Teknologi',
        'rsi': 38.5
    },
    'MSFT': {
        'ticker': 'MSFT',
        'name': 'Microsoft Corporation',
        'last_price': 390.20,
        'change': 2.10,
        'change_percent': 0.54,
        'volume': 25000000,
        'signal': 'BUY',
        'market_cap': 2800000000000,
        'sector': 'Teknologi',
        'rsi': 42.1
    },
    'AMZN': {
        'ticker': 'AMZN',
        'name': 'Amazon.com Inc.',
        'last_price': 178.90,
        'change': -0.80,
        'change_percent': -0.45,
        'volume': 30000000,
        'signal': 'HOLD',
        'market_cap': 1800000000000,
        'sector': 'Forbrukerdiskresjonær',
        'rsi': 55.8
    },
    'GOOGL': {
        'ticker': 'GOOGL',
        'name': 'Alphabet Inc.',
        'last_price': 2850.10,
        'change': 5.60,
        'change_percent': 0.20,
        'volume': 15000000,
        'signal': 'HOLD',
        'market_cap': 1700000000000,
        'sector': 'Kommunikasjonstjenester',
        'rsi': 48.9
    },
    'TSLA': {
        'ticker': 'TSLA',
        'name': 'Tesla Inc.',
        'last_price': 230.10,
        'change': -3.50,
        'change_percent': -1.50,
        'volume': 40000000,
        'signal': 'SELL',
        'market_cap': 750000000000,
        'sector': 'Forbrukerdiskresjonær',
        'rsi': 68.7
    },
    'META': {
        'ticker': 'META',
        'name': 'Meta Platforms Inc.',
        'last_price': 298.50,
        'change': 4.20,
        'change_percent': 1.43,
        'volume': 22000000,
        'signal': 'BUY',
        'market_cap': 760000000000,
        'sector': 'Kommunikasjonstjenester',
        'rsi': 43.2
    },
    'NVDA': {
        'ticker': 'NVDA',
        'name': 'NVIDIA Corporation',
        'last_price': 875.30,
        'change': 12.80,
        'change_percent': 1.48,
        'volume': 35000000,
        'signal': 'BUY',
        'market_cap': 2200000000000,
        'sector': 'Teknologi',
        'rsi': 36.4
    },
    'JPM': {
        'ticker': 'JPM',
        'name': 'JPMorgan Chase & Co.',
        'last_price': 145.60,
        'change': -0.90,
        'change_percent': -0.61,
        'volume': 12000000,
        'signal': 'HOLD',
        'market_cap': 425000000000,
        'sector': 'Finansielle tjenester',
        'rsi': 59.3
    },
    'V': {
        'ticker': 'V',
        'name': 'Visa Inc.',
        'last_price': 234.80,
        'change': 1.50,
        'change_percent': 0.64,
        'volume': 8000000,
        'signal': 'BUY',
        'market_cap': 485000000000,
        'sector': 'Finansielle tjenester',
        'rsi': 44.7
    },
    'WMT': {
        'ticker': 'WMT',
        'name': 'Walmart Inc.',
        'last_price': 158.90,
        'change': 0.80,
        'change_percent': 0.51,
        'volume': 9500000,
        'signal': 'HOLD',
        'market_cap': 430000000000,
        'sector': 'Consumer Staples',
        'rsi': 51.2
    },
    'UNH': {
        'ticker': 'UNH',
        'name': 'UnitedHealth Group Inc.',
        'last_price': 512.40,
        'change': 3.60,
        'change_percent': 0.71,
        'volume': 3200000,
        'signal': 'BUY',
        'market_cap': 485000000000,
        'sector': 'Healthcare',
        'rsi': 40.8
    },
    'HD': {
        'ticker': 'HD',
        'name': 'The Home Depot Inc.',
        'last_price': 325.70,
        'change': -2.30,
        'change_percent': -0.70,
        'volume': 4100000,
        'signal': 'HOLD',
        'market_cap': 335000000000,
        'sector': 'Consumer Discretionary',
        'rsi': 62.1
    },
    'ORCL': {
        'ticker': 'ORCL',
        'name': 'Oracle Corporation',
        'last_price': 115.80,
        'change': 1.20,
        'change_percent': 1.05,
        'volume': 2800000,
        'signal': 'BUY',
        'market_cap': 315000000000,
        'sector': 'Technology',
        'rsi': 48.3
    },
    'XOM': {
        'ticker': 'XOM',
        'name': 'Exxon Mobil Corporation',
        'last_price': 108.50,
        'change': -0.80,
        'change_percent': -0.73,
        'volume': 1900000,
        'signal': 'HOLD',
        'market_cap': 445000000000,
        'sector': 'Energy',
        'rsi': 55.7
    },
    'CVX': {
        'ticker': 'CVX',
        'name': 'Chevron Corporation',
        'last_price': 162.30,
        'change': 2.10,
        'change_percent': 1.31,
        'volume': 1600000,
        'signal': 'BUY',
        'market_cap': 305000000000,
        'sector': 'Energy',
        'rsi': 42.9
    },
    'KO': {
        'ticker': 'KO',
        'name': 'The Coca-Cola Company',
        'last_price': 61.20,
        'change': 0.30,
        'change_percent': 0.49,
        'volume': 1200000,
        'signal': 'HOLD',
        'market_cap': 265000000000,
        'sector': 'Consumer Staples',
        'rsi': 58.4
    },
    'MRK': {
        'ticker': 'MRK',
        'name': 'Merck & Co. Inc.',
        'last_price': 125.40,
        'change': -1.50,
        'change_percent': -1.18,
        'volume': 1800000,
        'signal': 'HOLD',
        'market_cap': 318000000000,
        'sector': 'Healthcare',
        'rsi': 51.2
    },
    'JNJ': {
        'ticker': 'JNJ',
        'name': 'Johnson & Johnson',
        'last_price': 161.80,
        'change': 0.90,
        'change_percent': 0.56,
        'volume': 1300000,
        'signal': 'BUY',
        'market_cap': 435000000000,
        'sector': 'Healthcare',
        'rsi': 44.6
    },
    'PG': {
        'ticker': 'PG',
        'name': 'Procter & Gamble Co.',
        'last_price': 154.20,
        'change': -0.60,
        'change_percent': -0.39,
        'volume': 950000,
        'signal': 'HOLD',
        'market_cap': 365000000000,
        'sector': 'Consumer Staples',
        'rsi': 57.3
    },
    'MA': {
        'ticker': 'MA',
        'name': 'Mastercard Inc.',
        'last_price': 412.70,
        'change': 3.20,
        'change_percent': 0.78,
        'volume': 820000,
        'signal': 'BUY',
        'market_cap': 395000000000,
        'sector': 'Financial Services',
        'rsi': 42.8
    },
    'DIS': {
        'ticker': 'DIS',
        'name': 'The Walt Disney Company',
        'last_price': 96.50,
        'change': -1.80,
        'change_percent': -1.83,
        'volume': 1850000,
        'signal': 'HOLD',
        'market_cap': 176000000000,
        'sector': 'Communication Services',
        'rsi': 63.2
    }
}

FALLBACK_STOCK_INFO = {
    'EQNR.OL': {
        'ticker': 'EQNR.OL',
        'shortName': 'Equinor ASA',
        'longName': 'Equinor ASA',
        'sector': 'Energi',
        'industry': 'Olje og gass',
        'regularMarketPrice': 342.55,
        'marketCap': 1100000000000,
        'dividendYield': 0.0146,
        'country': 'Norge',
        'currency': 'NOK',
        'volume': 3200000,
        'averageVolume': 3000000,
        'fiftyTwoWeekLow': 280.50,
        'fiftyTwoWeekHigh': 380.20,
        'trailingPE': 12.5,
        'forwardPE': 11.2,
        'priceToBook': 1.8,
        'beta': 1.2,
        'longBusinessSummary': 'Equinor ASA er et norsk multinasjonalt energiselskap med hovedkontor i Stavanger. Selskapet er primært involvert i utforskning og produksjon av olje og gass, samt fornybar energi.',
        'website': 'https://www.equinor.com',
        'employees': 21000,
        'city': 'Stavanger',
        'state': '',
        'zip': '4035',
        'phone': '+47 51 99 00 00',
        'previousClose': 340.25,
        'open': 341.80,
        'dayLow': 340.10,
        'dayHigh': 344.50,
        'recommendationKey': 'buy',
        'recommendationMean': 2.1,
        'targetHighPrice': 400.0,
        'targetLowPrice': 320.0,
        'targetMeanPrice': 360.0,
        'earningsGrowth': 0.15,
        'revenueGrowth': 0.08,
        'grossMargins': 0.45,
        'operatingMargins': 0.25,
        'profitMargins': 0.18,
        'returnOnAssets': 0.12,
        'returnOnEquity': 0.22,
        'totalCash': 45000000000,
        'totalDebt': 25000000000,
        'debtToEquity': 0.35,
        'currentRatio': 1.8,
        'quickRatio': 1.5,
        'bookValue': 190.0,
        'priceToSalesTrailing12Months': 1.2,
        'enterpriseValue': 1150000000000,
        'enterpriseToRevenue': 1.3,
        'enterpriseToEbitda': 4.5,
        'pegRatio': 0.8,
        'lastDividendValue': 5.0,
        'lastDividendDate': 1640995200,
        'exDividendDate': 1640995200,
        'payoutRatio': 0.35,
        'fiveYearAvgDividendYield': 0.055,
        'trailingAnnualDividendRate': 5.0,
        'trailingAnnualDividendYield': 0.0146,
        'dividendRate': 5.0,
        'lastSplitFactor': '',
        'lastSplitDate': 0,
        'sharesOutstanding': 3200000000,
        'floatShares': 2800000000,
        'heldPercentInsiders': 0.67,
        'heldPercentInstitutions': 0.15,
        'shortRatio': 2.5,
        'shortPercentOfFloat': 0.02,
        'impliedSharesOutstanding': 3200000000,
        'auditRisk': 3,
        'boardRisk': 2,
        'compensationRisk': 4,
        'shareHolderRightsRisk': 3,
        'overallRisk': 3,
        'governanceEpochDate': 1640995200,
        'compensationAsOfEpochDate': 1640995200,
        'maxAge': 1,
        'priceHint': 2,
        'exchange': 'OSL',
        'quoteType': 'EQUITY',
        'symbol': 'EQNR.OL',
        'underlyingSymbol': 'EQNR.OL',
        'firstTradeDateEpochUtc': 946684800,
        'timeZoneFullName': 'Europe/Oslo',
        'timeZoneShortName': 'CET',
        'uuid': '',
        'messageBoardId': '',
        'gmtOffSetMilliseconds': 3600000,
        'currentPrice': 342.55,
        'targetPrice': 360.0,
        'totalRevenue': 890000000000,
        'revenuePerShare': 278.0,
        'returnOnAssets': 0.12,
        'returnOnEquity': 0.22,
        'freeCashflow': 85000000000,
        'operatingCashflow': 120000000000,
        'earningsGrowth': 0.15,
        'revenueGrowth': 0.08,
        'grossMargins': 0.45,
        'ebitdaMargins': 0.35,
        'operatingMargins': 0.25,
        'financialCurrency': 'NOK',
        'trailingPegRatio': 0.8
    },
    'DNB.OL': {
        'ticker': 'DNB.OL',
        'shortName': 'DNB Bank ASA',
        'longName': 'DNB Bank ASA',
        'sector': 'Finansielle tjenester',
        'industry': 'Bank',
        'regularMarketPrice': 212.80,
        'marketCap': 350000000000,
        'dividendYield': 0.086,
        'country': 'Norge',
        'currency': 'NOK',
        'volume': 1500000,
        'averageVolume': 1400000,
        'fiftyTwoWeekLow': 180.50,
        'fiftyTwoWeekHigh': 240.80,
        'trailingPE': 11.6,
        'forwardPE': 10.8,
        'priceToBook': 1.1,
        'beta': 1.1,
        'longBusinessSummary': 'DNB ASA er Norges største finanskonsern og en av de største bankene i Norden. Banken tilbyr tjenester innen personmarked, bedriftsmarked og kapitalmarkeder.',
        'website': 'https://www.dnb.no',
        'employees': 10500,
        'city': 'Oslo',
        'state': '',
        'zip': '0021',
        'phone': '+47 915 03000',
        'previousClose': 214.00,
        'open': 212.50,
        'dayLow': 211.80,
        'dayHigh': 213.90,
        'recommendationKey': 'hold',
        'recommendationMean': 2.8,
        'targetHighPrice': 250.0,
        'targetLowPrice': 190.0,
        'targetMeanPrice': 220.0,
        'earningsGrowth': 0.12,
        'revenueGrowth': 0.06,
        'grossMargins': 0.65,
        'operatingMargins': 0.45,
        'profitMargins': 0.35,
        'returnOnAssets': 0.018,
        'returnOnEquity': 0.16,
        'totalCash': 85000000000,
        'totalDebt': 45000000000,
        'debtToEquity': 0.15,
        'currentRatio': 1.2,
        'quickRatio': 1.1,
        'bookValue': 190.0,
        'priceToSalesTrailing12Months': 3.2,
        'enterpriseValue': 360000000000,
        'enterpriseToRevenue': 3.5,
        'enterpriseToEbitda': 8.2,
        'pegRatio': 1.2,
        'lastDividendValue': 18.32,
        'exchange': 'OSL',
        'quoteType': 'EQUITY',
        'symbol': 'DNB.OL',
        'currentPrice': 212.80,
        'targetPrice': 220.0,
        'financialCurrency': 'NOK',
        'trailingEps': 18.32
    },
    'HD': {
        'ticker': 'HD',
        'shortName': 'The Home Depot Inc.',
        'longName': 'The Home Depot Inc.',
        'sector': 'Forbrukerdiskresjonær',
        'industry': 'Byggevarer',
        'regularMarketPrice': 345.67,
        'marketCap': 350000000000,
        'dividendYield': 0.025,
        'country': 'USA',
        'currency': 'USD',
        'volume': 3200000,
        'averageVolume': 3000000,
        'fiftyTwoWeekLow': 280.20,
        'fiftyTwoWeekHigh': 420.50,
        'trailingPE': 22.5,
        'forwardPE': 20.2,
        'priceToBook': 8.2,
        'beta': 1.1,
        'longBusinessSummary': 'The Home Depot Inc. driver og opererer varehus som selger byggevarer, hage- og utviklingsmateriell til gjør-det-selv-kunder, profesjonelle installatører og byggebransjen.',
        'website': 'https://www.homedepot.com',
        'employees': 500000,
        'city': 'Atlanta',
        'state': 'Georgia',
        'zip': '30339',
        'phone': '+1 770-433-8211',
        'previousClose': 342.80,
        'open': 344.20,
        'dayLow': 343.10,
        'dayHigh': 347.90,
        'recommendationKey': 'buy',
        'recommendationMean': 2.3,
        'targetHighPrice': 400.0,
        'targetLowPrice': 320.0,
        'targetMeanPrice': 360.0,
        'earningsGrowth': 0.08,
        'revenueGrowth': 0.06,
        'exchange': 'NYSE',
        'quoteType': 'EQUITY',
        'symbol': 'HD',
        'currentPrice': 345.67,
        'targetPrice': 360.0,
        'financialCurrency': 'USD',
        'trailingEps': 15.38
    },
    'TEL.OL': {
        'ticker': 'TEL.OL',
        'shortName': 'Telenor ASA',
        'longName': 'Telenor ASA',
        'sector': 'Kommunikasjonstjenester',
        'industry': 'Telekommunikasjon',
        'regularMarketPrice': 125.90,
        'marketCap': 180000000000,
        'dividendYield': 0.065,
        'country': 'Norge',
        'currency': 'NOK',
        'volume': 1200000,
        'averageVolume': 1100000,
        'fiftyTwoWeekLow': 110.50,
        'fiftyTwoWeekHigh': 145.80,
        'trailingPE': 14.2,
        'forwardPE': 13.1,
        'priceToBook': 2.1,
        'beta': 0.8,
        'longBusinessSummary': 'Telenor ASA er et norsk multinasjonalt telekommunikasjonsselskap. Selskapet tilbyr mobil-, fasttelefon-, og internettjenester i Norge og internasjonalt.',
        'website': 'https://www.telenor.com',
        'employees': 20000,
        'city': 'Fornebu',
        'state': '',
        'zip': '1331',
        'phone': '+47 810 77 000',
        'previousClose': 128.00,
        'open': 126.50,
        'dayLow': 125.20,
        'dayHigh': 127.10,
        'recommendationKey': 'hold',
        'recommendationMean': 2.7,
        'targetHighPrice': 150.0,
        'targetLowPrice': 120.0,
        'targetMeanPrice': 135.0,
        'exchange': 'OSL',
        'quoteType': 'EQUITY',
        'symbol': 'TEL.OL',
        'currentPrice': 125.90,
        'targetPrice': 135.0,
        'financialCurrency': 'NOK',
        'trailingEps': 8.87
    },
    'AKERBP.OL': {
        'ticker': 'AKERBP.OL',
        'shortName': 'Aker BP ASA',
        'longName': 'Aker BP ASA',
        'sector': 'Energi',
        'industry': 'Olje og gass',
        'regularMarketPrice': 289.40,
        'marketCap': 190000000000,
        'dividendYield': 0.035,
        'country': 'Norge',
        'currency': 'NOK',
        'volume': 1300000,
        'averageVolume': 1250000,
        'fiftyTwoWeekLow': 245.00,
        'fiftyTwoWeekHigh': 340.20,
        'trailingPE': 9.8,
        'forwardPE': 8.9,
        'priceToBook': 1.5,
        'beta': 1.4,
        'longBusinessSummary': 'Aker BP ASA er et norsk oljeselskap som driver utforskning og produksjon på norsk kontinentalsokkel. Selskapet fokuserer på økt oljeutvinning og lønnsom vekst.',
        'website': 'https://www.akerbp.com',
        'employees': 2200,
        'city': 'Lysaker',
        'state': '',
        'zip': '1366',
        'phone': '+47 51 35 30 00',
        'previousClose': 291.20,
        'open': 288.90,
        'dayLow': 287.50,
        'dayHigh': 291.80,
        'recommendationKey': 'hold',
        'recommendationMean': 2.5,
        'exchange': 'OSL',
        'quoteType': 'EQUITY',
        'symbol': 'AKERBP.OL',
        'currentPrice': 289.40,
        'financialCurrency': 'NOK',
        'trailingEps': 29.53
    }
}

class DataService:
    @staticmethod
    def get_stock_info(ticker):
        """Get stock info with caching and improved fallback"""
        # Check cache first with longer cache time
        if get_cache_service:
            cache_key = f"stock_info_{ticker}"
            cached_data = get_cache_service().get(cache_key)
            if cached_data:
                return cached_data
        
        # Always try fallback first to reduce API calls
        fallback_data = DataService.get_fallback_stock_info(ticker)
        
        # Only try Yahoo Finance for high-priority requests
        if ticker in ['TSLA', 'AAPL', 'GOOGL', 'MSFT', 'EQNR.OL', 'DNB.OL', 'TEL.OL']:
            try:
                # Very strict rate limiting
                can_request, wait_time = rate_limiter.can_make_request('yfinance')
                if not can_request:
                    logging.info(f"Rate limited for {ticker}, using fallback data")
                    if get_cache_service:
                        get_cache_service().set(cache_key, fallback_data)
                    return fallback_data
                
                rate_limiter.wait_if_needed('yfinance')
                
                # Suppress yfinance output
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    stock = yf.Ticker(ticker)
                    info = stock.info
                
                # Validate the data quality
                if info and len(info) > 1 and info.get('regularMarketPrice'):
                    # Merge with fallback data to fill gaps
                    merged_data = fallback_data.copy()
                    merged_data.update({k: v for k, v in info.items() if v is not None and v != 0})
                    
                    # Cache the successful result for longer
                    if get_cache_service:
                        get_cache_service().set(cache_key, merged_data)
                    return merged_data
                    
            except Exception as e:
                logging.warning(f"YFinance failed for {ticker}: {str(e)}")
                # Don't call record_failure if method doesn't exist
                if hasattr(rate_limiter, 'record_failure'):
                    rate_limiter.record_failure('yfinance')
        
        # Try alternative data source for Norwegian stocks
        if ticker.endswith('.OL'):
            try:
                norwegian_data = DataService.get_oslo_bors_overview()
                if norwegian_data and ticker in norwegian_data:
                    stock_data = norwegian_data[ticker]
                    # Merge with fallback data
                    enhanced_data = fallback_data.copy()
                    enhanced_data.update({
                        'regularMarketPrice': stock_data.get('last_price', fallback_data['regularMarketPrice']),
                        'regularMarketChange': stock_data.get('change', fallback_data['regularMarketChange']),
                        'regularMarketChangePercent': stock_data.get('change_percent', fallback_data['regularMarketChangePercent']),
                        'volume': stock_data.get('volume', fallback_data['volume']),
                    })
                    # Cache and return
                    if get_cache_service:
                        get_cache_service().set(cache_key, enhanced_data)
                    return enhanced_data
            except Exception as e:
                logging.warning(f"Oslo Børs data failed for {ticker}: {str(e)}")
        
        # Return enhanced fallback data
        # Cache fallback data for shorter time to retry sooner
        if get_cache_service:
            get_cache_service().set(cache_key, fallback_data)
        return fallback_data
    
    @staticmethod
    def get_stock_data(ticker, period='1mo', interval='1d'):
        """Get stock data with caching"""
        # Check cache first
        if get_cache_service:
            cache_key = f"stock_data_{ticker}_{period}_{interval}"
            cached_data = get_cache_service().get(cache_key, max_age_minutes=5)
            if cached_data:
                # Convert back to DataFrame
                return pd.DataFrame(cached_data)
        
        try:
            # Rate limiting
            rate_limiter.wait_if_needed('yfinance')
            
            # Suppress yfinance output
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                stock = yf.Ticker(ticker)
                data = stock.history(period=period, interval=interval)
            
            if not data.empty:
                # Cache the successful result (convert DataFrame to dict)
                if get_cache_service:
                    cache_data = data.reset_index().to_dict('records')
                    get_cache_service().set(cache_key, cache_data)
                return data
                
        except Exception as e:
            logging.error(f"Error fetching stock data for {ticker}: {str(e)}")
        
        # Return empty DataFrame on error
        return pd.DataFrame()

    @staticmethod
    def get_fallback_chart_data(ticker):
        """Generate fallback chart data for when API fails"""
        import pandas as pd
        from datetime import datetime, timedelta
        import random
        
        # Get base price from fallback data
        base_price = 100.0  # Default
        if ticker in FALLBACK_OSLO_DATA:
            base_price = FALLBACK_OSLO_DATA[ticker]['last_price']
        elif ticker in FALLBACK_GLOBAL_DATA:
            base_price = FALLBACK_GLOBAL_DATA[ticker]['last_price']
        
        # Generate 30 days of data
        dates = []
        prices = []
        volumes = []
        
        current_date = datetime.now() - timedelta(days=30)
        current_price = base_price * 0.95  # Start slightly lower
        
        for i in range(30):
            dates.append(current_date)
            
            # Generate realistic price movement
            change_percent = random.uniform(-0.03, 0.03)  # ±3% daily change
            current_price = current_price * (1 + change_percent)
            
            # Generate OHLC data
            open_price = current_price * random.uniform(0.995, 1.005)
            high_price = max(open_price, current_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, current_price) * random.uniform(0.98, 1.0)
            close_price = current_price
            
            prices.append({
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price
            })
            
            # Generate volume
            base_volume = 1000000 if '.OL' in ticker else 10000000
            volume = int(base_volume * random.uniform(0.5, 2.0))
            volumes.append(volume)
            
            current_date += timedelta(days=1)
        
        # Create DataFrame
        df = pd.DataFrame(prices, index=dates)
        df['Volume'] = volumes
        df.index.name = 'Date'
        
        return df
    
    @staticmethod
    def get_fallback_stock_info(ticker):
        """Get fallback stock info for a ticker"""
        if ticker in FALLBACK_STOCK_INFO:
            return FALLBACK_STOCK_INFO[ticker]
        
        # Enhanced fallback with realistic demo data based on ticker
        base_price = 100.0
        if ticker.endswith('.OL'):
            # Norwegian stocks
            base_price = random.uniform(50, 800)
            currency = 'NOK'
            market_cap = random.randint(1000000000, 500000000000)  # 1B - 500B NOK
        elif ticker in ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA']:
            # Major US tech stocks
            base_price = random.uniform(100, 400)
            currency = 'USD'
            market_cap = random.randint(500000000000, 3000000000000)  # 500B - 3T USD
        elif ticker.endswith('-USD') and 'BTC' in ticker or 'ETH' in ticker:
            # Crypto
            if 'BTC' in ticker:
                base_price = random.uniform(40000, 70000)
            elif 'ETH' in ticker:
                base_price = random.uniform(2000, 4000)
            else:
                base_price = random.uniform(0.1, 100)
            currency = 'USD'
            market_cap = random.randint(10000000000, 1000000000000)
        else:
            base_price = random.uniform(20, 200)
            currency = 'USD'
            market_cap = random.randint(1000000000, 100000000000)
        
        # Generate realistic financial metrics
        pe_ratio = random.uniform(8, 35)
        pb_ratio = random.uniform(0.5, 8)
        dividend_yield = random.uniform(0, 0.08) if not ticker.endswith('-USD') else 0
        volume = random.randint(100000, 50000000)
        change = random.uniform(-0.05, 0.05) * base_price
        change_percent = (change / base_price) * 100
        
        return {
            'ticker': ticker,
            'shortName': ticker.replace('.OL', '').replace('-USD', ''),
            'longName': f"{ticker.replace('.OL', '').replace('-USD', '')} Corporation",
            'sector': random.choice(['Technology', 'Energy', 'Finance', 'Healthcare', 'Consumer Goods']),
            'industry': random.choice(['Software', 'Oil & Gas', 'Banking', 'Pharmaceuticals', 'Retail']),
            'regularMarketPrice': round(base_price, 2),
            'regularMarketChange': round(change, 2),
            'regularMarketChangePercent': round(change_percent, 2),
            'marketCap': market_cap,
            'dividendYield': round(dividend_yield, 4),
            'country': 'Norway' if ticker.endswith('.OL') else 'United States',
            'currency': currency,
            'volume': volume,
            'averageVolume': volume,
            'fiftyTwoWeekLow': round(base_price * 0.7, 2),
            'fiftyTwoWeekHigh': round(base_price * 1.4, 2),
            'trailingPE': round(pe_ratio, 2),
            'forwardPE': round(pe_ratio * 0.9, 2),
            'priceToBook': round(pb_ratio, 2),
            'beta': round(random.uniform(0.5, 2.0), 2),
            'longBusinessSummary': f'{ticker} is a leading company in its sector with strong market position and growth prospects.',
            'website': f'https://www.{ticker.lower().replace(".ol", "").replace("-usd", "")}.com',
            'employees': random.randint(1000, 100000),
            'city': 'Oslo' if ticker.endswith('.OL') else 'New York',
            'state': 'Oslo' if ticker.endswith('.OL') else 'NY',
            'zip': '0150' if ticker.endswith('.OL') else '10001',
            'phone': '+47 12 34 56 78' if ticker.endswith('.OL') else '+1 555-123-4567',
            'previousClose': round(base_price - change, 2),
            'open': round(base_price + random.uniform(-0.02, 0.02) * base_price, 2),
            'dayLow': round(base_price * 0.98, 2),
            'dayHigh': round(base_price * 1.02, 2),
            'recommendationKey': random.choice(['buy', 'hold', 'sell']),
            'recommendationMean': round(random.uniform(2.0, 4.0), 1),
            'targetHighPrice': round(base_price * 1.2, 2),
            'targetLowPrice': round(base_price * 0.8, 2),
            'targetMeanPrice': round(base_price * 1.1, 2),
            'earningsGrowth': round(random.uniform(-0.1, 0.3), 3),
            'revenueGrowth': round(random.uniform(-0.05, 0.25), 3),
            'grossMargins': round(random.uniform(0.2, 0.8), 3),
            'operatingMargins': round(random.uniform(0.05, 0.4), 3),
            'profitMargins': round(random.uniform(0.02, 0.3), 3),
            'returnOnAssets': round(random.uniform(0.02, 0.2), 3),
            'returnOnEquity': round(random.uniform(0.05, 0.4), 3),
            'totalCash': random.randint(1000000000, 200000000000),
            'totalDebt': random.randint(500000000, 100000000000),
            'debtToEquity': round(random.uniform(0.1, 2.0), 2),
            'currentRatio': round(random.uniform(1.0, 3.0), 2),
            'quickRatio': round(random.uniform(0.5, 2.0), 2),
            'bookValue': round(base_price / pb_ratio, 2),
            'priceToSalesTrailing12Months': round(random.uniform(1.0, 15.0), 2),
            'enterpriseValue': 0,
            'enterpriseToRevenue': 0.0,
            'enterpriseToEbitda': 0.0,
            'pegRatio': 0.0,
            'lastDividendValue': 0.0,
            'lastDividendDate': 0,
            'exDividendDate': 0,
            'payoutRatio': 0.0,
            'fiveYearAvgDividendYield': 0.0,
            'trailingAnnualDividendRate': 0.0,
            'trailingAnnualDividendYield': 0.0,
            'dividendRate': 0.0,
            'lastSplitFactor': '',
            'lastSplitDate': 0,
            'sharesOutstanding': 0,
            'floatShares': 0,
            'heldPercentInsiders': 0.0,
            'heldPercentInstitutions': 0.0,
            'shortRatio': 0.0,
            'shortPercentOfFloat': 0.0,
            'impliedSharesOutstanding': 0,
            'auditRisk': 0,
            'boardRisk': 0,
            'compensationRisk': 0,
            'shareHolderRightsRisk': 0,
            'overallRisk': 0,
            'governanceEpochDate': 0,
            'compensationAsOfEpochDate': 0,
            'maxAge': 1,
            'priceHint': 0,
            'exchange': 'OTC',
            'quoteType': 'EQUITY',
            'symbol': ticker,
            'underlyingSymbol': ticker,
            'firstTradeDateEpochUtc': 0,
            'timeZoneFullName': 'UTC',
            'timeZoneShortName': 'UTC',
            'uuid': '',
            'messageBoardId': '',
            'gmtOffSetMilliseconds': 0,
            'currentPrice': 0.0,
            'targetPrice': 0.0,
            'totalRevenue': 0,
            'revenuePerShare': 0.0,
            'returnOnAssets': 0.0,
            'returnOnEquity': 0.0,
            'freeCashflow': 0,
            'operatingCashflow': 0,
            'earningsGrowth': 0.0,
            'revenueGrowth': 0.0,
            'grossMargins': 0.0,
            'ebitdaMargins': 0.0,
            'operatingMargins': 0.0,
            'financialCurrency': 'USD',
            'trailingPegRatio': 0.0,
            'enterpriseToRevenue': 0.0,
            'enterpriseToEbitda': 0.0,
            '52WeekChange': 0.0,
            'SandP52WeekChange': 0.0,
            'lastDividendValue': 0.0,
            'lastDividendDate': 0,
            'timeZoneFullName': 'UTC',
            'timeZoneShortName': 'UTC',
            'uuid': '',
            'messageBoardId': '',
            'gmtOffSetMilliseconds': 0,
            'currentPrice': 0.0,
            'targetPrice': 0.0,
            'totalRevenue': 0,
            'revenuePerShare': 0.0,
            'returnOnAssets': 0.0,
            'returnOnEquity': 0.0,
            'freeCashflow': 0,
            'operatingCashflow': 0,
            'earningsGrowth': 0.0,
            'revenueGrowth': 0.0,
            'grossMargins': 0.0,
            'ebitdaMargins': 0.0,
            'operatingMargins': 0.0,
            'financialCurrency': 'USD',
            'trailingPegRatio': 0.0,
            'trailingEps': 0.0,
        }
    
    @staticmethod
    def get_news(ticker):
        """Get news for a stock using yfinance with fallback"""
        try:
            # Use rate limiter instead of simple sleep
            rate_limiter.wait_if_needed('yahoo_finance')
            
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            # Format news data
            formatted_news = []
            for article in news[:5]:  # Limit to 5 articles
                formatted_news.append({
                    'title': article.get('title', 'Ingen tittel'),
                    'link': article.get('link', '#'),
                    'publisher': article.get('publisher', 'Ukjent kilde'),
                    'providerPublishTime': article.get('providerPublishTime', 0),
                    'type': article.get('type', 'STORY'),
                    'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '') if article.get('thumbnail') else '',
                    'relatedTickers': article.get('relatedTickers', [])
                })
            
            return formatted_news
        except Exception as e:
            print(f"Error fetching news for {ticker}: {str(e)}")
            return []
    
    @staticmethod
    def get_related_symbols(ticker):
        """Get related symbols for a stock with fallback"""
        try:
            # Add delay to avoid rate limiting
            time.sleep(0.1)
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try to get recommendations or similar companies
            recommendations = info.get('recommendations', []) or info.get('recommendedSymbols', [])
            
            if recommendations:
                return recommendations[:5]  # Limit to 5 recommendations
            
            # Fallback: return similar stocks from the same sector/industry
            if '.OL' in ticker:
                # Return some Oslo Børs stocks from the same sector
                return ['EQNR.OL', 'DNB.OL', 'TEL.OL'][:3]
            else:
                # Return some US stocks from the same sector
                return ['AAPL', 'MSFT', 'GOOGL'][:3]
        except Exception as e:
            print(f"Error fetching related symbols for {ticker}: {str(e)}")
            if '.OL' in ticker:
                return ['EQNR.OL', 'DNB.OL', 'TEL.OL'][:3]
            else:
                return ['AAPL', 'MSFT', 'GOOGL'][:3]
    
    @staticmethod
    def get_company_description(ticker):
        """Get company description with fallback"""
        try:
            # Fallback descriptions for major Norwegian companies
            descriptions = {
                'EQNR.OL': 'Equinor ASA er et norsk multinasjonalt energiselskap med hovedkontor i Stavanger. Selskapet er primært involvert i utforskning og produksjon av olje og gass, samt fornybar energi, og er en ledende aktør på norsk kontinentalsokkel.',
                'DNB.OL': 'DNB ASA er Norges største finanskonsern og en av de største bankene i Norden. Banken tilbyr tjenester innen personmarked, bedriftsmarked og kapitalmarkeder, med sterke posisjoner i Norge, Sverige og Danmark.',
                'TEL.OL': 'Telenor ASA er et norsk multinasjonalt telekommunikasjonsselskap med hovedkontor på Fornebu. Selskapet er en av verdens største mobiloperatører med virksomhet i Norden og Asia.',
                'YAR.OL': 'Yara International ASA er et norsk kjemisk selskap som produserer, distribuerer og selger nitrogenbaserte mineralgjødsel og industrielle kjemikalier. Selskapet er verdens ledende produsent av mineralgjødsel.',
                'NHY.OL': 'Norsk Hydro ASA er et norsk multinasjonalt aluminiums- og fornybar energiselskap med hovedkontor i Oslo. Selskapet opererer gjennom hele verdikjeden fra bauksitt til resirkulert aluminium.',
                'MOWI.OL': 'Mowi ASA er verdens største oppdrettslaksselskap og en av de største sjømatprodusentene i verden, med virksomhet i Norge, Skottland, Canada, Færøyene, Chile og Irland.',
                'ORK.OL': 'Orkla ASA er et norsk konglomerat som opererer innen merkevaremat, hjem- og personlig pleie, og andre forbrukerprodukter, hovedsakelig i de nordiske landene og utvalgte internasjonale markeder.',
                'AKSO.OL': 'Aker Solutions ASA leverer produkter, systemer og tjenester til olje- og gassindustrien over hele verden, med fokus på ingeniørløsninger, teknologi og prosjektleveranser.',
                'XXLASA.OL': 'XXL ASA er Nordens største sportskjede med over 40 varehus i Norge, Sverige, Finland og Danmark. Selskapet tilbyr et bredt utvalg av sportsklær, sportsutstyr og friluftsutstyr fra ledende merkevarer.',
                'KOMPLETT.OL': 'Komplett ASA er en ledende nordisk e-handelsaktør innen teknologi og hjemmeelektronikk, med sterke posisjoner i Norge, Sverige og Danmark.',
                'AUTOSTORE.OL': 'AutoStore Holdings Ltd er et norsk teknologiselskap som utvikler og leverer robotiserte lagersystemer for e-handel og detaljhandel over hele verden.',
                'EUROPRIS.OL': 'Europris ASA er Norges største lavpriskjede med over 480 butikker, som tilbyr et bredt sortiment av kvalitetsprodukter til lave priser.',
                'KITRON.OL': 'Kitron ASA er en ledende skandinavisk leverandør av elektronikkproduksjon og relaterte tjenester for sektorer som offshore/marine, energi/telekom, industri, medisinsk utstyr og forsvar/luftfart.',
                'AKERBP.OL': 'Aker BP ASA er et norsk olje- og gasselskap som fokuserer på utforskning, utvikling og produksjon på norsk kontinentalsokkel, med hovedfokus på Johan Sverdrup-feltet.',
                'NEL.OL': 'Nel ASA er et norsk hydrogenselskap som leverer løsninger for produksjon, lagring og distribusjon av hydrogen fra fornybare energikilder, og er en global leder innen hydrogenteknologi.',
                'SALM.OL': 'SalMar ASA er et av verdens største oppdrettslaksselskaper med virksomhet i Norge, Island og Skottland, fokusert på bærekraftig produksjon av atlantisk laks.',
                'AAPL': 'Apple Inc. er et amerikansk multinasjonalt teknologiselskap som designer, utvikler og selger forbrukerelektronikk, dataprogramvare og nettjenester, inkludert iPhone, iPad, Mac og Apple Watch.',
                'MSFT': 'Microsoft Corporation er et amerikansk multinasjonalt teknologiselskap som produserer dataprogramvare, forbrukerelektronikk, personlige datamaskiner og relaterte tjenester, inkludert Windows, Office og Azure.',
                'AMZN': 'Amazon.com Inc. er et amerikansk multinasjonalt teknologiselskap som fokuserer på e-handel, cloud computing, digitale strømmetjenester og kunstig intelligens.',
                'GOOGL': 'Alphabet Inc. er holdingselskapet for Google og andre datterselskaper, som opererer innen søkemotorer, online annonsering, cloud computing og andre teknologitjenester.',
                'META': 'Meta Platforms Inc. (tidligere Facebook) er et amerikansk teknologikonglomerat som eier og opererer Facebook, Instagram, WhatsApp og andre sosiale medieplattformer.',
                'TSLA': 'Tesla Inc. er et amerikansk elektrisk kjøretøy- og ren energiselskap som designer og produserer elektriske biler, energilagringssystemer og solarpaneler.',
                'NVDA': 'NVIDIA Corporation er et amerikansk teknologiselskap som designer og produserer grafikkprosessorer (GPU) for gaming, profesjonelle markeder og datasentre, samt AI- og maskinlæringsteknologi.',
                'JPM': 'JPMorgan Chase & Co. er en amerikansk multinasjonell investeringsbank og finanstjenesteselskap med hovedkontor i New York City.',
                'V': 'Visa Inc. er et amerikansk multinasjonalt finanstjenesteselskap som leverer elektroniske pengeoverføringer over hele verden, mest kjent for sine Visa-merkede kreditt- og debetkort.',
                'HD': 'The Home Depot Inc. er den største amerikanske hjemmeleverandør-kjeden og er den største detaljhandelen i USA innen hjemmeforbedring.',
                'WMT': 'Walmart Inc. er et amerikansk multinasjonalt detaljhandelsselskap som driver kjeder av hypermarkeder, lavprisvarehus og dagligvarebutikker.',
                'UNH': 'UnitedHealth Group Inc. er et amerikansk multinasjonalt administrert helsetjeneste- og forsikringsselskap basert i Minnesota.'
            }
            
            return descriptions.get(ticker, f'Beskrivelse av {ticker.replace(".OL", "").replace("-USD", "")} er ikke tilgjengelig i øyeblikket.')
        except Exception as e:
            print(f"Error fetching description for {ticker}: {str(e)}")
            return 'Ingen beskrivelse tilgjengelig.'
    
    @staticmethod
    def calculate_technical_signal(ticker):
        """Calculate technical signal with fallback"""
        try:
            # Use fallback data for signals
            if ticker in FALLBACK_OSLO_DATA:
                return FALLBACK_OSLO_DATA[ticker]['signal']
            elif ticker in FALLBACK_GLOBAL_DATA:
                return FALLBACK_GLOBAL_DATA[ticker]['signal']
            else:
                return random.choice(['BUY', 'SELL', 'HOLD'])
        except Exception as e:
            print(f"Error calculating signal for {ticker}: {str(e)}")
            return 'HOLD'
    
    @staticmethod
    def get_indices():
        """Get market indices with fallback data"""
        try:
            # Return fallback indices data
            return [
                {'name': 'OSEBX', 'value': 1245.67, 'change': 12.34, 'change_percent': 1.00},
                {'name': 'S&P 500', 'value': 4567.89, 'change': -23.45, 'change_percent': -0.51},
                {'name': 'NASDAQ', 'value': 14123.45, 'change': 89.12, 'change_percent': 0.63},
                {'name': 'DAX', 'value': 15678.90, 'change': -45.67, 'change_percent': -0.29}
            ]
        except Exception as e:
            print(f"Error getting indices: {str(e)}")
            return []

    @staticmethod
    def get_most_active_stocks():
        """Get most active stocks with fallback data"""
        try:
            return [
                {'ticker': 'EQNR.OL', 'name': 'Equinor', 'volume': 1234567, 'price': 275.50, 'change': 2.50},
                {'ticker': 'DNB.OL', 'name': 'DNB Bank', 'volume': 987654, 'price': 180.25, 'change': -1.75},
                {'ticker': 'TEL.OL', 'name': 'Telenor', 'volume': 765432, 'price': 120.80, 'change': 0.80},
                {'ticker': 'MOWI.OL', 'name': 'Mowi', 'volume': 654321, 'price': 195.60, 'change': 3.20}
            ]
        except Exception as e:
            print(f"Error getting most active stocks: {str(e)}")
            return []

    @staticmethod
    def get_stock_gainers():
        """Get stock gainers with fallback data"""
        try:
            return [
                {'ticker': 'NEL.OL', 'name': 'Nel', 'price': 12.45, 'change': 1.23, 'change_percent': 10.97},
                {'ticker': 'REC.OL', 'name': 'REC Silicon', 'price': 8.67, 'change': 0.78, 'change_percent': 9.89},
                {'ticker': 'SCANA.OL', 'name': 'Scana', 'price': 45.32, 'change': 3.45, 'change_percent': 8.24},
                {'ticker': 'THIN.OL', 'name': 'Thin Film', 'price': 23.56, 'change': 1.67, 'change_percent': 7.63}
            ]
        except Exception as e:
            print(f"Error getting stock gainers: {str(e)}")
            return []

    @staticmethod
    def get_stock_losers():
        """Get stock losers with fallback data"""
        try:
            return [
                {'ticker': 'FRONTLINE.OL', 'name': 'Frontline', 'price': 78.90, 'change': -7.89, 'change_percent': -9.09},
                {'ticker': 'GOGL.OL', 'name': 'Golden Ocean', 'price': 56.34, 'change': -4.56, 'change_percent': -7.49},
                {'ticker': 'MPCC.OL', 'name': 'MPC Container', 'price': 34.21, 'change': -2.34, 'change_percent': -6.41},
                {'ticker': 'BAKKA.OL', 'name': 'Bakkavor', 'price': 12.89, 'change': -0.87, 'change_percent': -6.32}
            ]
        except Exception as e:
            print(f"Error getting stock losers: {str(e)}")
            return []

    @staticmethod
    def get_sectors_performance():
        """Get sectors performance with fallback data"""
        try:
            return [
                {'name': 'Energi', 'change_percent': 2.34, 'count': 15},
                {'name': 'Finans', 'change_percent': -1.23, 'count': 8},
                {'name': 'Teknologi', 'change_percent': 3.45, 'count': 12},
                {'name': 'Helse', 'change_percent': 1.67, 'count': 6},
                {'name': 'Industri', 'change_percent': -0.89, 'count': 10},
                {'name': 'Forbruksvarer', 'change_percent': 0.56, 'count': 9}
            ]
        except Exception as e:
            print(f"Error getting sectors performance: {str(e)}")
            return []

    @staticmethod
    def get_oslo_bors_overview():
        """Get overview of Oslo Børs stocks with fallback data"""
        try:
            # Return fallback data directly to avoid API rate limiting
            return FALLBACK_OSLO_DATA.copy()
        except Exception as e:
            print(f"Error getting Oslo Børs overview: {str(e)}")
            return FALLBACK_OSLO_DATA.copy()

    @staticmethod
    def get_global_stocks_overview():
        """Get overview of global stocks with fallback data"""
        try:
            # Return fallback data directly to avoid API rate limiting
            return FALLBACK_GLOBAL_DATA.copy()
        except Exception as e:
            print(f"Error getting global stocks overview: {str(e)}")
            return FALLBACK_GLOBAL_DATA.copy()
    
    @staticmethod
    def get_single_stock_data(ticker):
        """Get data for a single stock with fallback"""
        try:
            # Check fallback data first
            if ticker in FALLBACK_OSLO_DATA:
                return FALLBACK_OSLO_DATA[ticker].copy()
            elif ticker in FALLBACK_GLOBAL_DATA:
                return FALLBACK_GLOBAL_DATA[ticker].copy()
            
            # If not in fallback, return basic data
            return {
                'ticker': ticker,
                'name': ticker,
                'last_price': 100.0,
                'change': 0.0,
                'change_percent': 0.0,
                'signal': 'HOLD',
                'volume': 1000000,
                'market_cap': 10000000000
            }
        except Exception as e:
            print(f"Error getting data for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def get_crypto_overview():
        """Get overview of cryptocurrencies with fallback data"""
        try:
            # Return fallback crypto data
            crypto_data = {
                'BTC-USD': {
                    'ticker': 'BTC-USD',
                    'name': 'Bitcoin',
                    'last_price': 65432.10,
                    'change': 1200.50,
                    'change_percent': 1.87,
                    'volume': 25000000000,
                    'signal': 'BUY'
                },
                'ETH-USD': {
                    'ticker': 'ETH-USD',
                    'name': 'Ethereum',
                    'last_price': 3456.78,
                    'change': 56.78,
                    'change_percent': 1.67,
                    'volume': 15000000000,
                    'signal': 'BUY'
                },
                'XRP-USD': {
                    'ticker': 'XRP-USD',
                    'name': 'Ripple',
                    'last_price': 0.632,
                    'change': 0.002,
                    'change_percent': 0.32,
                    'volume': 2000000000,
                    'signal': 'HOLD'
                },
                'LTC-USD': {
                    'ticker': 'LTC-USD',
                    'name': 'Litecoin',
                                       'last_price': 344.54,
                    'change': 1.30,
                    'change_percent': 0.38,
                    'volume': 500000000,
                    'signal': 'BUY'
                },
                'ADA-USD': {
                    'ticker': 'ADA-USD',
                    'name': 'Cardano',
                    'last_price': 0.485,
                    'change': 0.015,
                    'change_percent': 3.19,
                    'volume': 750000000,
                    'signal': 'BUY'
                },
                'SOL-USD': {
                    'ticker': 'SOL-USD',
                    'name': 'Solana',
                    'last_price': 148.75,
                    'change': -2.30,
                    'change_percent': -1.52,
                    'volume': 850000000,
                    'signal': 'HOLD'
                },
                'DOT-USD': {
                    'ticker': 'DOT-USD',
                    'name': 'Polkadot',
                    'last_price': 6.82,
                    'change': 0.18,
                    'change_percent': 2.71,
                    'volume': 380000000,
                    'signal': 'BUY'
                },
                'AVAX-USD': {
                    'ticker': 'AVAX-USD',
                    'name': 'Avalanche',
                    'last_price': 35.60,
                    'change': 1.40,
                    'change_percent': 4.09,
                    'volume': 420000000,
                    'signal': 'BUY'
                },
                'LINK-USD': {
                    'ticker': 'LINK-USD',
                    'name': 'Chainlink',
                    'last_price': 14.85,
                    'change': -0.25,
                    'change_percent': -1.66,
                    'volume': 320000000,
                    'signal': 'HOLD'
                }
            }
            return crypto_data
        except Exception as e:
            print(f"Error getting crypto overview: {str(e)}")
            return {}
        
    @staticmethod
    def get_currency_overview(base='NOK'):
        """Get overview of currencies with fallback data"""
        try:
            # Return fallback currency data
            if base == 'NOK':
                currency_data = {
                    'USDNOK=X': {
                        'ticker': 'USDNOK=X',
                        'name': 'USD/NOK',
                        'last_price': 10.45,
                        'change': -0.15,
                        'change_percent': -1.42,
                        'volume': 2500000000,
                        'signal': 'HOLD'
                    },
                    'EURNOK=X': {
                        'ticker': 'EURNOK=X',
                        'name': 'EUR/NOK',
                        'last_price': 11.32,
                        'change': 0.08,
                        'change_percent': 0.71,
                        'volume': 1800000000,
                        'signal': 'BUY'
                    }
                }
            else:
                currency_data = {
                    'EURUSD=X': {
                        'ticker': 'EURUSD=X',
                        'name': 'EUR/USD',
                        'last_price': 1.0845,
                        'change': 0.0012,
                        'change_percent': 0.11,
                        'volume': 4200000000,
                        'signal': 'HOLD'
                    }
                }
            
            return currency_data
        except Exception as e:
            print(f"Error getting currency overview: {str(e)}")
            return {}
    
    @staticmethod
    def get_market_overview():
        """Get complete market overview with fallback data"""
        return {
            'oslo_stocks': DataService.get_oslo_bors_overview(),
            'global_stocks': DataService.get_global_stocks_overview(),
            'crypto': DataService.get_crypto_overview(),
            'currency': DataService.get_currency_overview()
        }
    
    @staticmethod
    def search_ticker(query):
        """Search for ticker symbols (alias for search_stocks for backward compatibility)"""
        results = DataService.search_stocks(query)
        # Return just ticker symbols for backward compatibility
        return [result['ticker'] for result in results]
    
    @staticmethod
    def search_stocks(query):
        """Search for stocks by name or ticker with fallback data"""
        results = []
        query = query.upper()
        
        # Search in fallback Oslo Børs data
        for ticker, data in FALLBACK_OSLO_DATA.items():
            if query in ticker or query in data['name'].upper():
                results.append({
                    'ticker': ticker,
                    'name': data['name'],
                    'exchange': 'Oslo Børs',
                    'sector': data['sector']
                })
        
        # Search in fallback global data
        for ticker, data in FALLBACK_GLOBAL_DATA.items():
            if query in ticker or query in data['name'].upper():
                results.append({
                    'ticker': ticker,
                    'name': data['name'],
                    'exchange': 'NASDAQ',
                    'sector': data['sector']
                })
        
        return results[:10]  # Limit to 10 results

    @staticmethod
    def get_fallback_eps(ticker):
        """Get fallback EPS value for ticker"""
        eps_data = {
            'EQNR.OL': 27.45,
            'DNB.OL': 18.32,
            'TEL.OL': 12.67,
            'YAR.OL': 15.89,
            'NHY.OL': 8.23,
            'MOWI.OL': 11.45,
            'AKERBP.OL': 22.18,
            'AAPL': 6.13,
            'MSFT': 9.65,
            'AMZN': 3.24,
            'GOOGL': 5.80,
            'TSLA': 4.90
        }
        return eps_data.get(ticker, 8.50)  # Default EPS

    @staticmethod
    def get_fallback_sector(ticker):
        """Get fallback sector for ticker"""
        if '.OL' in ticker:
            sector_data = {
                'EQNR.OL': 'Energy',
                'DNB.OL': 'Financial Services',
                'TEL.OL': 'Communication Services',
                'YAR.OL': 'Basic Materials',
                'NHY.OL': 'Basic Materials',
                'MOWI.OL': 'Consumer Defensive',
                'AKERBP.OL': 'Energy'
            }
            return sector_data.get(ticker, 'Industrials')
        else:
            sector_data = {
                'AAPL': 'Technology',
                'MSFT': 'Technology',
                'AMZN': 'Consumer Cyclical',
                'GOOGL': 'Communication Services',
                'TSLA': 'Consumer Cyclical'
            }
            return sector_data.get(ticker, 'Technology')

    @staticmethod
    def get_fallback_industry(ticker):
        """Get fallback industry for ticker"""
        if '.OL' in ticker:
            industry_data = {
                'EQNR.OL': 'Oil & Gas Integrated',
                'DNB.OL': 'Banks - Regional',
                'TEL.OL': 'Telecom Services',
                'YAR.OL': 'Agricultural Inputs',
                'NHY.OL': 'Aluminum',
                'MOWI.OL': 'Farm Products',
                'AKERBP.OL': 'Oil & Gas E&P'
            }
            return industry_data.get(ticker, 'Industrial Conglomerates')
        else:
            industry_data = {
                'AAPL': 'Consumer Electronics',
                'MSFT': 'Software - Infrastructure',
                'AMZN': 'Internet Retail',
                'GOOGL': 'Internet Content & Information',
                'TSLA': 'Auto Manufacturers'
            }
            return industry_data.get(ticker, 'Software - Application')

    @staticmethod
    def get_fallback_country(ticker):
        """Get fallback country for ticker"""
        if '.OL' in ticker:
            return 'Norway'
        else:
            return 'United States'
    
    @staticmethod
    def get_market_status():
        """Get market open/close status for Oslo Børs and other markets"""
        from datetime import datetime, timezone, timedelta
        import pytz
        
        try:
            # Get current time in different timezones
            oslo_tz = pytz.timezone('Europe/Oslo')
            ny_tz = pytz.timezone('America/New_York')
            current_utc = datetime.now(timezone.utc)
            
            oslo_time = current_utc.astimezone(oslo_tz)
            ny_time = current_utc.astimezone(ny_tz)
            
            # Oslo Børs trading hours: 9:00 - 16:30 CET, Monday-Friday
            oslo_open = False
            if oslo_time.weekday() < 5:  # Monday = 0, Friday = 4
                oslo_start = oslo_time.replace(hour=9, minute=0, second=0, microsecond=0)
                oslo_end = oslo_time.replace(hour=16, minute=30, second=0, microsecond=0)
                oslo_open = oslo_start <= oslo_time <= oslo_end
            
            # NYSE trading hours: 9:30 - 16:00 EST, Monday-Friday
            ny_open = False
            if ny_time.weekday() < 5:  # Monday = 0, Friday = 4
                ny_start = ny_time.replace(hour=9, minute=30, second=0, microsecond=0)
                ny_end = ny_time.replace(hour=16, minute=0, second=0, microsecond=0)
                ny_open = ny_start <= ny_time <= ny_end
            
            return {
                'oslo_bors': {
                    'is_open': oslo_open,
                    'status': 'Åpen' if oslo_open else 'Stengt',
                    'local_time': oslo_time.strftime('%H:%M CET'),
                    'next_open': DataService._get_next_market_open(oslo_time, 9, 0) if not oslo_open else None,
                    'next_close': DataService._get_next_market_close(oslo_time, 16, 30) if oslo_open else None
                },
                'nasdaq': {
                    'is_open': ny_open,
                    'status': 'Open' if ny_open else 'Closed',
                    'local_time': ny_time.strftime('%H:%M EST'),
                    'next_open': DataService._get_next_market_open(ny_time, 9, 30) if not ny_open else None,
                    'next_close': DataService._get_next_market_close(ny_time, 16, 0) if ny_open else None
                },
                'crypto': {
                    'is_open': True,
                    'status': '24/7',
                    'local_time': current_utc.strftime('%H:%M UTC'),
                    'next_open': None,
                    'next_close': None
                }
            }
        except Exception as e:
            print(f"Error getting market status: {str(e)}")
            # Fallback status
            return {
                'oslo_bors': {'is_open': False, 'status': 'Stengt', 'local_time': '15:30'},
                'nasdaq': {'is_open': False, 'status': 'Stengt', 'local_time': '22:00'},
                'crypto': {'is_open': True, 'status': '24/7', 'local_time': 'Alltid åpen'}
            }
    
    @staticmethod
    def _get_next_market_open(current_time, hour, minute):
        """Get next market open time"""
        try:
            next_open = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If it's past market hours today, go to next weekday
            if current_time.time() > next_open.time() or current_time.weekday() >= 5:
                days_ahead = 1
                if current_time.weekday() == 4:  # Friday
                    days_ahead = 3  # Skip to Monday
                elif current_time.weekday() == 5:  # Saturday
                    days_ahead = 2  # Skip to Monday
                elif current_time.weekday() == 6:  # Sunday
                    days_ahead = 1  # Skip to Monday
                
                next_open += timedelta(days=days_ahead)
            
            return next_open.strftime('%d.%m %H:%M')
        except:
            return 'Ukjent'
    
    @staticmethod
    def _get_next_market_close(current_time, hour, minute):
        """Get next market close time"""
        try:
            next_close = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return next_close.strftime('%H:%M')
        except:
            return 'Ukjent'
    
    @staticmethod
    def create_basic_fallback(ticker):
        """Create basic fallback data for any ticker with realistic pricing"""
        import random
        
        # Generate more realistic pricing based on ticker type
        if ticker.endswith('.OL'):
            # Oslo Børs stocks - typically range from 10-500 NOK
            base_price = random.uniform(50, 300)
            currency = 'NOK'
            country = 'Norge'
            exchange = 'OSL'
            name_suffix = ' ASA'
        else:
            # International stocks - typically range from 20-500 USD
            base_price = random.uniform(75, 400)
            currency = 'USD'
            country = 'United States'
            exchange = 'NASDAQ'
            name_suffix = ' Inc.'
        
        # Generate realistic market metrics
        market_cap = int(random.uniform(5000000000, 200000000000))  # 5B to 200B
        volume = int(random.uniform(500000, 5000000))
        change = random.uniform(-0.05, 0.05)  # ±5% change
        change_percent = change * 100
        
        return {
            'ticker': ticker,
            'shortName': ticker.replace('.OL', '') if ticker.endswith('.OL') else ticker,
            'longName': ticker.replace('.OL', '') + name_suffix if ticker.endswith('.OL') else ticker + name_suffix,
            'sector': DataService.get_fallback_sector(ticker),
            'industry': DataService.get_fallback_industry(ticker),
            'regularMarketPrice': round(base_price, 2),
            'currentPrice': round(base_price, 2),
            'regularMarketChange': round(base_price * change, 2),
            'regularMarketChangePercent': round(change_percent, 2),
            'regularMarketVolume': volume,
            'marketCap': market_cap,
            'currency': currency,
            'country': country,
            'exchange': exchange,
            'trailingPE': round(random.uniform(10, 30), 2),
            'forwardPE': round(random.uniform(12, 25), 2),
            'dividendYield': round(random.uniform(0, 0.05), 4) if random.random() > 0.3 else 0,
            'beta': round(random.uniform(0.7, 1.5), 2),
            'bookValue': round(base_price * random.uniform(0.5, 1.2), 2),
            'priceToBook': round(random.uniform(1.0, 3.0), 2),
            'earningsGrowth': round(random.uniform(-0.1, 0.3), 3),
            'revenueGrowth': round(random.uniform(-0.05, 0.25), 3),
            'trailingEps': round(base_price / random.uniform(15, 25), 2),
            'financialCurrency': currency,
            'timeZoneFullName': 'Europe/Oslo' if currency == 'NOK' else 'America/New_York',
            'timeZoneShortName': 'CET' if currency == 'NOK' else 'EST',
            'website': f'https://example-{ticker.lower().replace(".", "-")}.com',
            'longBusinessSummary': f'This is a fallback description for {ticker}. Real data is temporarily unavailable due to rate limiting.',
            'fullTimeEmployees': random.randint(1000, 50000),
            'city': 'Oslo' if currency == 'NOK' else 'New York',
            'state': '' if currency == 'NOK' else 'NY',
            'phone': '+47 12 34 56 78' if currency == 'NOK' else '+1 555-123-4567'
        }
    
    @staticmethod
    def get_stock_news(ticker, limit=5):
        """Get news for a specific stock ticker"""
        try:
            # Check cache first
            if get_cache_service:
                cache_key = f"stock_news_{ticker}"
                cached_news = get_cache_service().get(cache_key)
                if cached_news:
                    return cached_news
            
            # Generate relevant news based on ticker
            company_name = ticker.replace('.OL', '').replace('-', ' ')
            if ticker.endswith('.OL'):
                # Norwegian companies
                news_items = [
                    {
                        'title': f'{company_name} rapporterer kvartalstall',
                        'summary': f'Selskapet presenterer sine siste finansielle resultater med fokus på fremtidig vekst.',
                        'url': f'https://e24.no/{ticker.lower()}',
                        'published': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                        'source': 'E24',
                        'sentiment': 'positive'
                    },
                    {
                        'title': f'Analytikere oppdaterer kursmål for {company_name}',
                        'summary': f'Flere meglerhus justerer sine anbefalinger etter siste markedsutvikling.',
                        'url': f'https://dn.no/{ticker.lower()}',
                        'published': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                        'source': 'Dagens Næringsliv',
                        'sentiment': 'neutral'
                    },
                    {
                        'title': f'{company_name} på Oslo Børs i dag',
                        'summary': f'Aksjen handles aktivt på Oslo Børs med økt interesse fra investorer.',
                        'url': f'https://finansavisen.no/{ticker.lower()}',
                        'published': (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                        'source': 'Finansavisen',
                        'sentiment': 'positive'
                    }
                ]
            else:
                # International companies
                news_items = [
                    {
                        'title': f'{company_name} Reports Strong Quarterly Results',
                        'summary': f'The company exceeded analyst expectations with robust revenue growth and improved margins.',
                        'url': f'https://finance.yahoo.com/news/{ticker.lower()}',
                        'published': (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                        'source': 'Yahoo Finance',
                        'sentiment': 'positive'
                    },
                    {
                        'title': f'Analysts Upgrade {company_name} Price Target',
                        'summary': f'Wall Street analysts raise price targets following strong fundamentals and market position.',
                        'url': f'https://marketwatch.com/{ticker.lower()}',
                        'published': (datetime.utcnow() - timedelta(hours=8)).isoformat(),
                        'source': 'MarketWatch',
                        'sentiment': 'positive'
                    },
                    {
                        'title': f'{company_name} Trading Update',
                        'summary': f'Stock shows continued momentum with increased institutional interest and volume.',
                        'url': f'https://bloomberg.com/{ticker.lower()}',
                        'published': (datetime.utcnow() - timedelta(hours=14)).isoformat(),
                        'source': 'Bloomberg',
                        'sentiment': 'neutral'
                    }
                ]
            
            # Limit results
            news_items = news_items[:limit]
            
            # Cache the results
            if get_cache_service:
                get_cache_service().set(cache_key, news_items)
            
            return news_items
            
        except Exception as e:
            logging.error(f"Error getting news for {ticker}: {str(e)}")
            return [{
                'title': f'Markedsoppdatering for {ticker}',
                'summary': f'Følg med på utviklingen for {ticker} og andre relaterte aksjer.',
                'url': '#',
                'published': datetime.utcnow().isoformat(),
                'source': 'Aksjeradar',
                'sentiment': 'neutral'
            }]