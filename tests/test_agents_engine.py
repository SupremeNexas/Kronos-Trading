import os
import unittest
import tempfile
import json
import pandas as pd
from unittest.mock import MagicMock

# Import Agent components
from webui.agents_engine.checkpoint.manager import CheckpointManager
from webui.agents_engine.memory.manager import MemoryManager
from webui.agents_engine.gate.risk_gate import KronosRiskGate
from webui.agents_engine.llm_agent import KronosLLMAgent
from webui.agents_engine.orchestrator import AgentEngineOrchestrator

class TestAgentsEngine(unittest.TestCase):
    def setUp(self):
        # Create temp files for checkpoint db and agent memory json
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_mem = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_db.close()
        self.temp_mem.close()

        # Mock Broker
        self.mock_broker = MagicMock()
        self.mock_broker.get_balance.return_value = 10000.0
        self.mock_broker.get_positions.return_value = {
            "AAPL": {"quantity": 10.0, "average_price": 150.0, "current_price": 180.0}
        }
        self.mock_broker.place_order.return_value = {"success": True, "message": "Order executed"}

    def tearDown(self):
        os.unlink(self.temp_db.name)
        os.unlink(self.temp_mem.name)

    def test_checkpoint_manager(self):
        manager = CheckpointManager(db_path=self.temp_db.name)

        # Save a checkpoint
        analysis_id = "test_run_1"
        symbol = "AAPL"
        stage = "DATA_FETCH"
        status = "SUCCESS"
        result = {"data": "fetched"}

        manager.save_checkpoint(analysis_id, symbol, stage, status, result=result)

        # Retrieve a checkpoint
        retrieved = manager.get_checkpoint(analysis_id, stage)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["status"], "SUCCESS")
        self.assertEqual(retrieved["result"], result)

        # Get all stages
        all_stages = manager.get_all_stages(analysis_id)
        self.assertIn("DATA_FETCH", all_stages)
        self.assertEqual(all_stages["DATA_FETCH"]["status"], "SUCCESS")

        # Clear checkpoints
        manager.clear_checkpoints(analysis_id)
        self.assertIsNone(manager.get_checkpoint(analysis_id, stage))

    def test_memory_manager(self):
        manager = MemoryManager(memory_path=self.temp_mem.name)

        # Test storing decision
        symbol = "AAPL"
        ai_decision = {
            "action": "BUY",
            "confidence": 0.8,
            "stop_loss": 170.0,
            "take_profit": 200.0,
            "reasoning": "High confidence bullish setup"
        }
        manager.store_decision(
            symbol=symbol,
            ai_decision=ai_decision,
            kronos_direction="BULLISH",
            risk_level="MEDIUM",
            entry_price=180.0
        )

        # Test resolving outcomes (it is currently unresolved)
        past_reflections = manager.get_past_reflections(symbol)
        self.assertEqual(len(past_reflections), 0)  # Because it's not resolved yet

        # Resolve outcome: Positive price return
        manager.resolve_outcomes(symbol, current_price=190.0)

        # Check if now resolved and reflection is accessible
        past_reflections = manager.get_past_reflections(symbol)
        self.assertEqual(len(past_reflections), 1)
        self.assertEqual(past_reflections[0]["outcome"], "PROFIT")
        self.assertIn("correct", past_reflections[0]["lessons"].lower())

    def test_risk_gate(self):
        gate = KronosRiskGate(max_asset_exposure=0.3, max_stop_loss_pct=0.10)

        portfolio_holdings = {
            "AAPL": {"quantity": 10.0, "average_price": 150.0, "current_price": 180.0}
        }
        portfolio_cash = 10000.0

        # Valid BUY (no pre-existing exposure on MSFT)
        res = gate.validate_action(
            symbol="MSFT",
            action="BUY",
            price=180.0,
            quantity=10.0,
            stop_loss=170.0,
            take_profit=210.0,
            portfolio_cash=portfolio_cash,
            portfolio_holdings=portfolio_holdings
        )
        self.assertTrue(res["approved"])
        self.assertEqual(res["adjusted_quantity"], 10.0)

        # Asset Concentration checking (AAPL pre-existing exposure adjusts qty from 10.0 to 9.0)
        res_concentration = gate.validate_action(
            symbol="AAPL",
            action="BUY",
            price=180.0,
            quantity=10.0,
            stop_loss=170.0,
            take_profit=210.0,
            portfolio_cash=portfolio_cash,
            portfolio_holdings=portfolio_holdings
        )
        self.assertTrue(res_concentration["approved"])
        self.assertEqual(res_concentration["adjusted_quantity"], 9.0)

        # BUY with invalid stop loss (too wide)
        res_invalid_sl = gate.validate_action(
            symbol="AAPL",
            action="BUY",
            price=180.0,
            quantity=10.0,
            stop_loss=150.0, # distance is 30, which is > 10% (18.0)
            take_profit=210.0,
            portfolio_cash=portfolio_cash,
            portfolio_holdings=portfolio_holdings
        )
        self.assertFalse(res_invalid_sl["approved"])
        self.assertIn("too wide", res_invalid_sl["reason"])

        # SELL with sufficient inventory
        res_sell = gate.validate_action(
            symbol="AAPL",
            action="SELL",
            price=180.0,
            quantity=5.0,
            stop_loss=0.0,
            take_profit=0.0,
            portfolio_cash=portfolio_cash,
            portfolio_holdings=portfolio_holdings
        )
        self.assertTrue(res_sell["approved"])
        self.assertEqual(res_sell["adjusted_quantity"], 5.0)

        # SELL exceeding holdings footprint
        res_sell_excess = gate.validate_action(
            symbol="AAPL",
            action="SELL",
            price=180.0,
            quantity=15.0,
            stop_loss=0.0,
            take_profit=0.0,
            portfolio_cash=portfolio_cash,
            portfolio_holdings=portfolio_holdings
        )
        self.assertFalse(res_sell_excess["approved"])
        self.assertIn("Insufficient holdings", res_sell_excess["reason"])

    def test_llm_agent_fallback(self):
        agent = KronosLLMAgent()
        kronos_pred = {
            "signal": "BUY",
            "return_pct": 2.5,
            "support": 175.0,
            "resistance": 195.0,
            "last_close": 180.0
        }
        reflections = []

        analysis = agent._rule_based_analysis("AAPL", 180.0, kronos_pred, reflections)
        self.assertEqual(analysis["action"], "BUY")
        self.assertGreater(analysis["confidence"], 0.7)
        self.assertLess(analysis["stop_loss"], 180.0)
        self.assertGreater(analysis["take_profit"], 180.0)

    def test_orchestrator_integration(self):
        # We build orchestrator with mock components
        orchestrator = AgentEngineOrchestrator(
            broker=self.mock_broker,
            predictor=None,
            db_path=self.temp_db.name,
            memory_path=self.temp_mem.name
        )

        # Run orchestrator cycle
        res = orchestrator.run_cycle(
            symbol="AAPL",
            timeframe="1d",
            pred_len=14,
            allow_trading=True
        )

        self.assertTrue(res["success"])
        self.assertIn("analysis_id", res)
        self.assertIn("forecast", res)
        self.assertIn("proposal", res)
        self.assertIn("validation", res)
        self.assertIn("execution", res)

if __name__ == "__main__":
    unittest.main()
