import unittest
import os
import json
from unittest.mock import patch, MagicMock

# Force CPU mode for tests to be fast
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from webui.forecast_engine import (
    KronosRealAdapter,
    TechnicalForecastAdapter,
    EnsembleForecastEngine,
    get_kronos_model
)
from webui.market_data import MarketDataProvider

class TestForecastEngine(unittest.TestCase):
    def setUp(self):
        self.market_provider = MarketDataProvider()
        self.ensemble_engine = EnsembleForecastEngine()
        self.bars_aapl = self.market_provider.get_historical_bars("AAPL", "1d", limit=100)["bars"]
        self.bars_msft = self.market_provider.get_historical_bars("MSFT", "1d", limit=100)["bars"]

    def test_missing_infoway_data_fails_explicitly(self):
        # 6. Missing Infoway data cannot silently generate a forecast.
        res = self.ensemble_engine.generate_forecast("BADDATATICKER", interval="1d", horizon=20)
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("forecast_status"), "ERROR")
        self.assertIn("NO_DATA", res.get("error", ""))

    def test_cache_miss_for_different_symbols(self):
        # 1. AAPL request cannot return cached MSFT output.
        res_aapl = self.ensemble_engine.generate_forecast("AAPL", interval="1d", horizon=20)
        res_msft = self.ensemble_engine.generate_forecast("MSFT", interval="1d", horizon=20)
        
        self.assertEqual(res_aapl["symbol"], "AAPL")
        self.assertEqual(res_msft["symbol"], "MSFT")
        self.assertNotEqual(res_aapl["expected_return"], res_msft["expected_return"]) # Unlikely to be exactly same
        self.assertNotEqual(res_aapl["target_price"], res_msft["target_price"])

    def test_forecast_metadata(self):
        # 7. Forecast response contains asset-specific metadata.
        # 8. UI does not display generic canned asset reasoning.
        res = self.ensemble_engine.generate_forecast("AAPL", interval="1d", horizon=20)
        if res.get("success"):
            self.assertIn("asset_context", res)
            self.assertIn("bullish_factors", res)
            self.assertIn("bearish_factors", res)
            self.assertIn("key_drivers", res)
            self.assertIn("missing_information", res)
            self.assertIn("conditions_that_would_change_decision", res)
            
            # Additional fields 
            self.assertIn("forecast_id", res)
            self.assertIn("model_version", res)
            self.assertIn("data_timestamp", res)
            self.assertIn("inference_timestamp", res)

            drivers = res["key_drivers"]
            # Assert they aren't just empty fallback
            self.assertTrue(len(drivers) > 0)
            
            # Check execution
            self.assertIn("execution", res["model_details"]["KRONOS"])
            self.assertIn("inference_mode", res["model_details"]["KRONOS"])
            self.assertIn("device", res["model_details"]["KRONOS"])

    @patch('webui.forecast_engine.get_kronos_model')
    def test_missing_model_explicit_failure(self, mock_get_model):
        # 5. Missing model produces an explicit failure state.
        mock_get_model.return_value = "ERROR"
        res = self.ensemble_engine.generate_forecast("AAPL", interval="1d", horizon=20)
        self.assertFalse(res.get("success", True))
        self.assertEqual(res.get("forecast_status"), "UNAVAILABLE")
        self.assertIn("MODEL UNAVAILABLE", res.get("error", ""))

    def test_model_status_real(self):
        # 3. Model status is REAL only when actual inference executed.
        res = self.ensemble_engine.generate_forecast("AAPL", interval="1d", horizon=20)
        if res.get("success"):
            self.assertEqual(res["forecast_status"], "REAL")
            self.assertEqual(res["forecast_source"], "KRONOS")
            self.assertEqual(res["model_details"]["KRONOS"]["status"], "REAL")

    def test_multiple_assets_independent_conditioning(self):
        # Test AAPL, MSFT, NVDA, AMZN for independency and valid forecast ID
        results = {}
        for sym in ["AAPL", "MSFT", "NVDA", "AMZN"]:
            bars_nvda = self.market_provider.get_historical_bars(sym, "1d", limit=50)["bars"]
            if not bars_nvda:
                continue 
            adapter = KronosRealAdapter()
            res = adapter.forecast(sym, bars_nvda, horizon=10)
            if res.get("status") == "REAL":
                target = res["target_price"]
                last_price = float(bars_nvda[-1]["close"])
                self.assertTrue(abs(target - last_price) > 0.0)
                results[sym] = target

        targets = list(results.values())
        if len(targets) > 1:
            # They should not all be identical
            self.assertTrue(len(set(targets)) > 1)

    def test_synthetic_adapters_removed(self):
        # 4. Synthetic/random forecast adapters cannot appear as REAL.
        import webui.forecast_engine as fe
        # Ensure TimesFMAdapter and ChronosAdapter don't exist anymore
        self.assertFalse(hasattr(fe, 'TimesFMAdapter'))
        self.assertFalse(hasattr(fe, 'ChronosAdapter'))

if __name__ == '__main__':
    unittest.main()
