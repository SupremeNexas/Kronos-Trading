"""
Tests for Kronos Quantitative Validation Engine and Trading Journal.
Covers all 8 classes in quant_validation.py and TradingJournal.
"""

import os
import unittest
import tempfile
import json
import datetime
import numpy as np

from webui.agents_engine.quant_validation import (
    BacktestIntegrityAuditor,
    WalkForwardValidator,
    MultipleTestingCorrector,
    RegimeAnalyzer,
    PositionSizer,
    TradingGatekeeper,
    ProductionHealthMonitor,
    RealisticCostCalculator,
)
from webui.agents_engine.trading_journal import TradingJournal


# ---------------------------------------------------------------------------
# Helpers — synthetic data generators
# ---------------------------------------------------------------------------

def _make_bars(n: int, start_price: float = 100.0, trend: float = 0.001,
               volatility: float = 0.02) -> list:
    """Generate n synthetic OHLCV bar dicts."""
    np.random.seed(42)
    bars = []
    price = start_price
    for i in range(n):
        ret = trend + volatility * np.random.randn()
        price *= (1 + ret)
        high = price * (1 + abs(volatility * np.random.rand()))
        low = price * (1 - abs(volatility * np.random.rand()))
        bars.append({
            "open": round(price * (1 + 0.001 * np.random.randn()), 4),
            "high": round(high, 4),
            "low": round(low, 4),
            "close": round(price, 4),
            "volume": int(1e6 + 1e5 * np.random.randn()),
        })
    return bars


def _closes_array(n: int, start: float = 100.0, trend: float = 0.001,
                  volatility: float = 0.02) -> np.ndarray:
    """Generate n synthetic close prices as a numpy array."""
    np.random.seed(42)
    returns = trend + volatility * np.random.randn(n - 1)
    prices = np.empty(n)
    prices[0] = start
    for i in range(1, n):
        prices[i] = prices[i - 1] * (1 + returns[i - 1])
    return prices


# =========================================================================
# 1. BacktestIntegrityAuditor
# =========================================================================

class TestBacktestIntegrityAuditor(unittest.TestCase):

    def setUp(self):
        self.auditor = BacktestIntegrityAuditor()
        self.bars = _make_bars(100)

    def test_pass_case_next_bar_execution_no_leakage_fees(self):
        """Next-bar execution, no leakage, fees applied => should pass."""
        signals = [
            {"bar_index": 10, "execution_bar_index": 11, "symbol": "TEST", "quantity": 1},
            {"bar_index": 50, "execution_bar_index": 51, "symbol": "TEST", "quantity": 1},
        ]
        result = self.auditor.audit(
            bars=self.bars,
            signals=signals,
            fees_applied=True,
            slippage_applied=True,
            train_end_idx=60,
            test_start_idx=70,
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["checks"]["look_ahead_bias"], "ABSENT")
        self.assertEqual(result["checks"]["next_bar_execution"], "PRESENT")
        self.assertEqual(result["checks"]["parameter_data_leakage"], "ABSENT")
        self.assertEqual(result["checks"]["fees_accounted"], "PRESENT")
        self.assertIn("timestamp", result)

    def test_fail_same_bar_execution_look_ahead_bias(self):
        """Same-bar execution should detect look-ahead bias and fail."""
        signals = [
            {"bar_index": 10, "execution_bar_index": 10, "symbol": "TEST", "quantity": 1},
        ]
        result = self.auditor.audit(
            bars=self.bars,
            signals=signals,
            fees_applied=True,
            slippage_applied=True,
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["look_ahead_bias"], "PRESENT")
        self.assertEqual(result["checks"]["next_bar_execution"], "ABSENT")
        self.assertTrue(len(result["issues"]) > 0)

    def test_leakage_detection_train_overlaps_test(self):
        """train_end_idx >= test_start_idx should flag data leakage."""
        signals = [
            {"bar_index": 10, "execution_bar_index": 11, "symbol": "TEST", "quantity": 1},
        ]
        result = self.auditor.audit(
            bars=self.bars,
            signals=signals,
            fees_applied=True,
            slippage_applied=True,
            train_end_idx=70,
            test_start_idx=70,
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["checks"]["parameter_data_leakage"], "PRESENT")


# =========================================================================
# 2. WalkForwardValidator
# =========================================================================

class TestWalkForwardValidator(unittest.TestCase):

    def setUp(self):
        self.validator = WalkForwardValidator()

    def test_200_bars_synthetic_data(self):
        """Walk-forward with 200+ bars should produce fold results."""
        closes = _closes_array(250)
        result = self.validator.validate(closes, n_folds=5)
        self.assertNotIn("error", result)
        self.assertIn("n_folds", result)
        self.assertIn("mean_sharpe", result)
        self.assertIn("passed", result)
        self.assertIsInstance(result["n_folds"], int)
        self.assertGreaterEqual(result["n_folds"], 2)
        self.assertIsInstance(result["folds"], list)
        self.assertTrue(len(result["folds"]) > 0)

    def test_insufficient_data_returns_error(self):
        """Fewer than 60 bars should return an error dict."""
        closes = _closes_array(30)
        result = self.validator.validate(closes)
        self.assertIn("error", result)
        self.assertFalse(result["passed"])

    def test_result_contains_required_keys(self):
        """Verify the result dict contains n_folds, mean_sharpe, passed."""
        closes = _closes_array(200)
        result = self.validator.validate(closes, n_folds=4)
        for key in ("n_folds", "mean_sharpe", "passed"):
            self.assertIn(key, result)


# =========================================================================
# 3. MultipleTestingCorrector
# =========================================================================

class TestMultipleTestingCorrector(unittest.TestCase):

    def setUp(self):
        self.corrector = MultipleTestingCorrector()

    def test_pass_high_sharpe_single_trial(self):
        """A very high Sharpe with only 1 trial should PASS."""
        result = self.corrector.deflated_sharpe(
            observed_sharpe=5.0,
            n_trials=1,
            n_observations=500,
        )
        self.assertEqual(result["verdict"], "PASS")
        self.assertTrue(result["passed"])

    def test_reject_many_trials(self):
        """A moderate Sharpe tested across many trials should be REJECTED."""
        result = self.corrector.deflated_sharpe(
            observed_sharpe=0.8,
            n_trials=1000,
            n_observations=252,
        )
        self.assertEqual(result["verdict"], "REJECT")
        self.assertFalse(result["passed"])

    def test_insufficient_observations(self):
        """n_observations <= 1 should return an error."""
        result = self.corrector.deflated_sharpe(
            observed_sharpe=1.0,
            n_trials=1,
            n_observations=1,
        )
        self.assertIn("error", result)
        self.assertFalse(result["passed"])


# =========================================================================
# 4. RegimeAnalyzer
# =========================================================================

class TestRegimeAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = RegimeAnalyzer()

    def test_trending_data_detects_regimes(self):
        """Build a series with a bull then bear segment; analyzer should detect at least one regime."""
        np.random.seed(7)
        n = 200
        # First half: bull trend; second half: bear trend
        bull = 100.0 * np.cumprod(1 + 0.005 + 0.01 * np.random.randn(n // 2))
        bear = bull[-1] * np.cumprod(1 - 0.005 + 0.01 * np.random.randn(n // 2))
        closes = np.concatenate([[100.0], bull, bear])
        result = self.analyzer.analyze(closes, sma_period=20)
        self.assertIn("regimes", result)
        self.assertIn("robustness", result)
        # At least one of BULL or BEAR should be evaluated
        evaluated = result.get("evaluated_regimes", [])
        self.assertTrue(len(evaluated) > 0,
                        "Expected at least one evaluated regime")

    def test_insufficient_data(self):
        """Short series should return an error."""
        closes = _closes_array(30)
        result = self.analyzer.analyze(closes, sma_period=50)
        self.assertIn("error", result)
        self.assertFalse(result["passed"])


# =========================================================================
# 5. PositionSizer
# =========================================================================

class TestPositionSizer(unittest.TestCase):

    def setUp(self):
        self.sizer = PositionSizer()

    def test_valid_buy_sizing(self):
        """Standard BUY with valid stop should be approved."""
        result = self.sizer.calculate(
            account_capital=100000,
            entry_price=50.0,
            stop_price=48.0,
            side="BUY",
        )
        self.assertTrue(result["approved"])
        self.assertGreater(result["position_size"], 0)
        self.assertEqual(result["side"], "BUY")
        self.assertIn("notional_exposure", result)

    def test_stop_above_entry_rejected_for_buy(self):
        """Stop above entry on a BUY should be rejected."""
        result = self.sizer.calculate(
            account_capital=100000,
            entry_price=50.0,
            stop_price=52.0,
            side="BUY",
        )
        self.assertFalse(result["approved"])
        self.assertEqual(result["position_size"], 0)
        self.assertIn("must be below", result["reason"])

    def test_portfolio_cap_enforced(self):
        """When risk-based size exceeds portfolio cap, cap should be enforced."""
        # Tiny risk_per_unit => large position => triggers cap
        result = self.sizer.calculate(
            account_capital=100000,
            entry_price=100.0,
            stop_price=99.99,  # only 0.01 risk per unit
            side="BUY",
            max_portfolio_pct=20.0,
        )
        self.assertTrue(result["approved"])
        self.assertLessEqual(result["portfolio_pct"], 20.0)


# =========================================================================
# 6. TradingGatekeeper
# =========================================================================

class TestTradingGatekeeper(unittest.TestCase):

    def setUp(self):
        self.gatekeeper = TradingGatekeeper()
        self.bars = _make_bars(200)

    def test_evaluate_gates_returns_verdict_and_all_gates(self):
        """evaluate_gates should return verdict and all 5 gate keys."""
        result = self.gatekeeper.evaluate_gates(
            bars=self.bars,
            signal="BUY",
            entry_price=self.bars[-1]["close"],
            stop_price=self.bars[-1]["close"] * 0.95,
            account_capital=100000,
            side="BUY",
        )
        self.assertIn("verdict", result)
        self.assertIn(result["verdict"], ("TRADE_ALLOWED", "NO_TRADE"))
        self.assertIn("gates", result)
        gates = result["gates"]
        expected_gate_keys = [
            "GATE_1_LEAKAGE",
            "GATE_2_MULTIPLE_TESTING",
            "GATE_3_WALK_FORWARD",
            "GATE_4_RISK",
            "GATE_5_DATA_FRESHNESS",
        ]
        for key in expected_gate_keys:
            self.assertIn(key, gates, f"Missing gate key: {key}")

    def test_each_gate_has_passed_key(self):
        """Each gate result should contain a 'passed' boolean."""
        result = self.gatekeeper.evaluate_gates(
            bars=self.bars,
            signal="BUY",
            entry_price=self.bars[-1]["close"],
            stop_price=self.bars[-1]["close"] * 0.95,
            account_capital=100000,
            side="BUY",
        )
        for gate_name, gate_val in result["gates"].items():
            self.assertIn("passed", gate_val,
                          f"Gate {gate_name} missing 'passed' key")
            self.assertIsInstance(gate_val["passed"], bool)


# =========================================================================
# 7. ProductionHealthMonitor
# =========================================================================

class TestProductionHealthMonitor(unittest.TestCase):

    def setUp(self):
        self.monitor = ProductionHealthMonitor()

    def test_insufficient_trades_returns_continue(self):
        """Fewer than 3 trades should return INSUFFICIENT_DATA / CONTINUE."""
        self.monitor.record_trade("AAPL", 150.0, 152.0, "BUY")
        status = self.monitor.get_health_status("AAPL")
        self.assertEqual(status["status"], "INSUFFICIENT_DATA")
        self.assertEqual(status["recommendation"], "CONTINUE")
        self.assertFalse(status["halt_new_trades"])

    def test_negative_returns_recommend_warning_or_halt(self):
        """Consistently losing trades should yield WARNING or HALT."""
        for i in range(10):
            self.monitor.record_trade("AAPL", 150.0, 140.0, "BUY")
        status = self.monitor.get_health_status("AAPL")
        self.assertEqual(status["status"], "EVALUATED")
        self.assertIn(status["recommendation"], ("WARNING", "HALT"))


# =========================================================================
# 8. RealisticCostCalculator
# =========================================================================

class TestRealisticCostCalculator(unittest.TestCase):

    def setUp(self):
        self.calculator = RealisticCostCalculator()

    def test_costs_reduce_net_returns(self):
        """Net returns after costs should be less than gross returns."""
        np.random.seed(42)
        gross = 0.001 + 0.01 * np.random.randn(100)
        result = self.calculator.apply_costs(gross, n_trades=50, n_periods=100)
        self.assertLess(result["net_return_pct"], result["gross_return_pct"])
        self.assertGreater(result["cost_drag_pct"], 0)

    def test_zero_trades_no_drag(self):
        """With zero trades there is no turnover, so cost drag is zero."""
        np.random.seed(42)
        gross = 0.001 + 0.01 * np.random.randn(100)
        result = self.calculator.apply_costs(gross, n_trades=0, n_periods=100)
        self.assertAlmostEqual(result["cost_drag_pct"], 0.0, places=5)
        self.assertAlmostEqual(result["net_return_pct"],
                               result["gross_return_pct"], places=5)


# =========================================================================
# 9. TradingJournal
# =========================================================================

class TestTradingJournal(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.journal = TradingJournal(journal_path=self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_full_lifecycle(self):
        """record_prediction -> update_confirmation -> update_order -> update_outcome."""
        entry_id = self.journal.record_prediction(
            symbol="AAPL",
            market_data_timestamp=datetime.datetime.now().isoformat(),
            forecast={
                "direction": "BULLISH",
                "expected_return_pct": 2.5,
                "target_price": 185.0,
                "support": 170.0,
                "resistance": 195.0,
            },
            confidence=0.85,
            signal="BUY",
        )
        self.assertTrue(entry_id.startswith("jrn_"))

        # Confirm the trade
        ok = self.journal.update_confirmation(entry_id, confirmed=True)
        self.assertTrue(ok)
        entry = self.journal.get_entry(entry_id)
        self.assertEqual(entry["user_confirmation"], "CONFIRMED")

        # Record order placement
        ok = self.journal.update_order(entry_id, order_id="ORD_001",
                                       order_status="FILLED",
                                       fill_price=180.0)
        self.assertTrue(ok)
        entry = self.journal.get_entry(entry_id)
        self.assertEqual(entry["paper_order_id"], "ORD_001")
        self.assertEqual(entry["fill_price"], 180.0)

        # Record outcome
        ok = self.journal.update_outcome(entry_id, exit_price=190.0,
                                          notes="Take profit hit")
        self.assertTrue(ok)
        entry = self.journal.get_entry(entry_id)
        self.assertEqual(entry["outcome"], "PROFIT")
        self.assertGreater(entry["pnl_pct"], 0)
        self.assertTrue(entry["model_correct"])

    def test_get_accuracy_report(self):
        """Accuracy report should reflect resolved trades."""
        # Record and resolve two trades
        id1 = self.journal.record_prediction(
            symbol="AAPL",
            market_data_timestamp=datetime.datetime.now().isoformat(),
            forecast={"direction": "BULLISH", "target_price": 185.0},
            confidence=0.8,
            signal="BUY",
        )
        self.journal.update_order(id1, "ORD_1", "FILLED", fill_price=180.0)
        self.journal.update_outcome(id1, exit_price=190.0)

        id2 = self.journal.record_prediction(
            symbol="AAPL",
            market_data_timestamp=datetime.datetime.now().isoformat(),
            forecast={"direction": "BULLISH", "target_price": 160.0},
            confidence=0.6,
            signal="BUY",
        )
        self.journal.update_order(id2, "ORD_2", "FILLED", fill_price=155.0)
        self.journal.update_outcome(id2, exit_price=150.0)

        report = self.journal.get_accuracy_report("AAPL")
        self.assertEqual(report["resolved_trades"], 2)
        self.assertEqual(report["profitable_trades"], 1)
        self.assertEqual(report["losing_trades"], 1)
        self.assertIn("hit_rate_pct", report)
        self.assertIn("avg_pnl_pct", report)

    def test_get_rejected_trades_report(self):
        """Rejected trades should appear in the rejected trades report."""
        entry_id = self.journal.record_prediction(
            symbol="TSLA",
            market_data_timestamp=datetime.datetime.now().isoformat(),
            forecast={"direction": "BEARISH"},
            confidence=0.4,
            signal="SELL",
        )
        self.journal.update_confirmation(entry_id, confirmed=False)

        rejected = self.journal.get_rejected_trades_report()
        self.assertTrue(len(rejected) >= 1)
        symbols = [r["symbol"] for r in rejected]
        self.assertIn("TSLA", symbols)
        matching = [r for r in rejected if r["id"] == entry_id]
        self.assertEqual(len(matching), 1)
        self.assertIn("User rejected", matching[0]["reason"])


if __name__ == "__main__":
    unittest.main()
