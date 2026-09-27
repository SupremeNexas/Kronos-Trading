import unittest
import os
import json
from webui.forecast_engine import (
    TimesFMAdapter,
    ChronosAdapter,
    TechnicalForecastAdapter,
    FinRLStrategyAdapter,
    BacktestEngine,
    EnsembleForecastEngine,
    detect_hardware_capabilities
)
from webui.market_data import MarketDataProvider

class TestForecastEngine(unittest.TestCase):
    def setUp(self):
        self.market_provider = MarketDataProvider()
        self.ensemble_engine = EnsembleForecastEngine()
        self.bars = self.market_provider.get_historical_bars("AAPL", "1d", limit=100)["bars"]

    def test_hardware_detection(self):
        hw = detect_hardware_capabilities()
        self.assertIn("gpu_available", hw)
        self.assertIn("forecast_mode", hw)

    def test_timesfm_adapter(self):
        adapter = TimesFMAdapter()
        res = adapter.forecast("AAPL", self.bars, horizon=20)
        self.assertEqual(res["model"], "TimesFM (Google)")
        self.assertEqual(len(res["quantiles"]["p50"]), 20)
        self.assertIn("direction", res)
        self.assertIn(res["direction"], ["BULLISH", "BEARISH", "NEUTRAL"])

    def test_chronos_adapter(self):
        adapter = ChronosAdapter()
        res = adapter.forecast("AAPL", self.bars, horizon=20)
        self.assertEqual(res["model"], "Chronos-2 (Amazon)")
        self.assertEqual(len(res["quantiles"]["p50"]), 20)
        self.assertIn("p10", res["quantiles"])
        self.assertIn("p90", res["quantiles"])

    def test_technical_forecast_adapter(self):
        adapter = TechnicalForecastAdapter()
        res = adapter.analyze(self.bars)
        self.assertEqual(res["model"], "TechnicalForecast")
        self.assertIn("rsi", res)
        self.assertIn("support", res)
        self.assertIn("resistance", res)

    def test_finrl_strategy_adapter(self):
        adapter = FinRLStrategyAdapter()
        res = adapter.evaluate("AAPL", self.bars, expected_return=3.5)
        self.assertEqual(res["model"], "FinRL Strategy Engine (AI4Finance)")
        self.assertIn(res["action"], ["BUY", "ACCUMULATE", "HOLD", "SELL"])
        self.assertIn("suggested_position_pct", res)

    def test_backtest_engine(self):
        engine = BacktestEngine()
        res = engine.run_backtest("AAPL", self.bars, horizon=10)
        self.assertEqual(res["symbol"], "AAPL")
        self.assertIn("mae_pct", res)
        self.assertIn("directional_accuracy_pct", res)
        self.assertTrue(res["directional_accuracy_pct"] >= 50.0)

    def test_ensemble_forecast_engine(self):
        res = self.ensemble_engine.generate_forecast("AAPL", interval="1d", horizon=20)
        self.assertEqual(res["symbol"], "AAPL")
        self.assertIn("direction", res)
        self.assertIn("confidence_pct", res)
        self.assertIn("model_agreement", res)
        self.assertIn("ensemble_trajectory", res)
        self.assertEqual(len(res["ensemble_trajectory"]["p50"]), 20)
        self.assertIn("overall_ai_score", res)
        self.assertIn("scenarios", res)
        self.assertIn("bull", res["scenarios"])
        self.assertIn("base", res["scenarios"])
        self.assertIn("bear", res["scenarios"])

if __name__ == '__main__':
    unittest.main()
