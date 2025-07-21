import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta
from app.services.data_service import DataService, retry_with_backoff

class TestDataService(unittest.TestCase):
    def setUp(self):
        self.data_service = DataService()
        self.test_ticker = "TEST.OL"

    @patch('yfinance.Ticker')
    def test_get_stock_data_success(self, mock_ticker):
        # Setup mock
        mock_history = pd.DataFrame({
            'Open': [100],
            'High': [110],
            'Low': [90],
            'Close': [105],
            'Volume': [1000]
        })
        mock_ticker.return_value.history.return_value = mock_history

        # Test
        result = self.data_service.get_stock_data(self.test_ticker)
        self.assertFalse(result.empty)
        self.assertEqual(result['Close'][0], 105)

    @patch('yfinance.Ticker')
    def test_get_stock_data_retry(self, mock_ticker):
        # Setup mock to fail twice then succeed
        mock_history = pd.DataFrame({'Close': [105]})
        mock_ticker.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            MagicMock(history=lambda **kwargs: mock_history)
        ]

        # Test
        result = self.data_service.get_stock_data(self.test_ticker)
        self.assertFalse(result.empty)
        self.assertEqual(result['Close'][0], 105)

    def test_get_demo_stock_data(self):
        result = self.data_service.get_demo_stock_data(self.test_ticker)
        self.assertFalse(result.empty)
        self.assertTrue(all(col in result.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']))
        self.assertEqual(len(result), 30)  # Should have 30 days of data

if __name__ == '__main__':
    unittest.main()
