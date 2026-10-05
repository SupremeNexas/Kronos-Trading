import unittest
from unittest.mock import patch
from webui.strategies.early_signal_scanner import EarlySignalScanner
from webui.db import get_db_connection

class TestEarlySignalScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = EarlySignalScanner()
        self.scanner.api_key = "mock_key"

    def test_successful_scanner_scan(self):
        def mock_fetch(url):
            if "trending" in url:
                return {"coins": [{"item": {"id": "bitcoin"}}]}
            elif "market_chart" in url:
                return {"total_volumes": [[1, 100], [2, 100], [3, 100]]}
            elif "markets" in url:
                return [{"price_change_percentage_7d_in_currency": 6.0, "total_volume": 200}]
            return None
        
        self.scanner._fetch_json = mock_fetch
        results = self.scanner.scan_assets(["bitcoin"])
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["asset"], "bitcoin")
        self.assertEqual(results[0]["volume_ratio"], 2.0)
        self.assertEqual(results[0]["momentum_7d"], 6.0)
        self.assertEqual(results[0]["attention_score"], 1)
        self.assertEqual(results[0]["score"], 3)
        self.assertEqual(results[0]["decision"], "WATCHLIST")

    def test_unknown_attention_and_metrics(self):
        def mock_fetch(url):
            return None
            
        self.scanner._fetch_json = mock_fetch
        results = self.scanner.scan_assets(["unknown_coin"])
        
        self.assertEqual(results[0]["attention_score"], "UNKNOWN")
        self.assertEqual(results[0]["volume_ratio"], "UNKNOWN")
        self.assertEqual(results[0]["momentum_7d"], "UNKNOWN")
        self.assertEqual(results[0]["score"], 0)
        self.assertEqual(results[0]["decision"], "MONITOR")

    def test_no_automatic_trading(self):
        def mock_fetch(url):
            if "trending" in url:
                return {"coins": [{"item": {"id": "solana"}}]}
            elif "market_chart" in url:
                return {"total_volumes": [[1, 100], [2, 100], [3, 100]]}
            elif "markets" in url:
                return [{"price_change_percentage_7d_in_currency": 10.0, "total_volume": 500}]
            return None
            
        self.scanner._fetch_json = mock_fetch
        results = self.scanner.scan_assets(["solana"])
        
        self.assertEqual(results[0]["decision"], "WATCHLIST")
        self.assertNotIn("alpaca_order_id", results[0])

    def test_db_persistence(self):
        if get_db_connection:
            history = self.scanner.get_scan_history()
            self.assertIsInstance(history, list)

if __name__ == '__main__':
    unittest.main()
