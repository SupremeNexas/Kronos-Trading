import unittest
import os
import json
import tempfile
from webui.broker_service import MockBrokerAdapter, RiskEngine
from webui.market_data import MarketDataProvider
from webui.ai_berkshire_engine import AIBerkshireEngine
from webui.app import app

class TestRiskEngine(unittest.TestCase):
    def setUp(self):
        self.risk_engine = RiskEngine()

    def test_valid_market_order(self):
        res = self.risk_engine.validate_order(
            symbol="AAPL",
            side="BUY",
            quantity=10,
            price=180.0,
            account_balance=100000.0
        )
        self.assertTrue(res["valid"])

    def test_invalid_quantity(self):
        res = self.risk_engine.validate_order(
            symbol="AAPL",
            side="BUY",
            quantity=-5,
            price=180.0,
            account_balance=100000.0
        )
        self.assertFalse(res["valid"])
        self.assertIn("Invalid quantity", res["reason"])

    def test_invalid_price(self):
        res = self.risk_engine.validate_order(
            symbol="AAPL",
            side="BUY",
            quantity=10,
            price=0.0,
            account_balance=100000.0
        )
        self.assertFalse(res["valid"])
        self.assertIn("Invalid price", res["reason"])

    def test_max_order_value_exceeded(self):
        # Default MAX_ORDER_VALUE is 50,000
        res = self.risk_engine.validate_order(
            symbol="AAPL",
            side="BUY",
            quantity=1000,
            price=180.0, # $180,000 > $50,000
            account_balance=500000.0
        )
        self.assertFalse(res["valid"])
        self.assertIn("MAX_ORDER_VALUE", res["reason"])

    def test_insufficient_buying_power(self):
        res = self.risk_engine.validate_order(
            symbol="AAPL",
            side="BUY",
            quantity=200,
            price=180.0, # $36,000 > $10,000
            account_balance=10000.0
        )
        self.assertFalse(res["valid"])
        self.assertIn("Insufficient buying power", res["reason"])

    def test_kill_switch_active(self):
        self.risk_engine.kill_switch_active = True
        res = self.risk_engine.validate_order(
            symbol="AAPL",
            side="BUY",
            quantity=10,
            price=180.0,
            account_balance=100000.0
        )
        self.assertFalse(res["valid"])
        self.assertIn("KILL SWITCH ACTIVE", res["reason"])

class TestMockBrokerAdapter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.portfolio_file = os.path.join(self.temp_dir.name, "paper_portfolio.json")
        self.broker = MockBrokerAdapter(portfolio_path=self.portfolio_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_initial_account_balance(self):
        acc = self.broker.get_account()
        self.assertEqual(acc["cash"], 100000.0)
        self.assertEqual(acc["portfolio_value"], 100000.0)

    def test_place_buy_order_and_positions(self):
        res = self.broker.place_order(
            symbol="AAPL",
            side="BUY",
            quantity=10,
            order_type="Market",
            price=180.0,
            idempotency_key="ik_test_1"
        )
        self.assertTrue(res["success"])
        acc = self.broker.get_account(mark_prices={"AAPL": 180.0})
        self.assertEqual(acc["cash"], 98200.0)

        positions = self.broker.get_positions(mark_prices={"AAPL": 180.0})
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["symbol"], "AAPL")
        self.assertEqual(positions[0]["quantity"], 10)

    def test_duplicate_order_idempotency(self):
        res1 = self.broker.place_order("AAPL", "BUY", 10, "Market", 180.0, idempotency_key="ik_dup_1")
        self.assertTrue(res1["success"])

        res2 = self.broker.place_order("AAPL", "BUY", 10, "Market", 180.0, idempotency_key="ik_dup_1")
        self.assertFalse(res2["success"])
        self.assertIn("DUPLICATE_ORDER", res2["error"])

    def test_sell_order_and_pnl_calculation(self):
        self.broker.place_order("AAPL", "BUY", 10, "Market", 180.0, idempotency_key="ik_b1")
        res_sell = self.broker.place_order("AAPL", "SELL", 5, "Market", 200.0, idempotency_key="ik_s1")
        self.assertTrue(res_sell["success"])

        acc = self.broker.get_account(mark_prices={"AAPL": 200.0})
        self.assertEqual(acc["realized_pnl"], 100.0) # (200 - 180) * 5 = +100

class TestMarketDataProvider(unittest.TestCase):
    def setUp(self):
        self.provider = MarketDataProvider()

    def test_get_quote(self):
        quote = self.provider.get_quote("AAPL")
        self.assertIn("symbol", quote)
        self.assertIn("price", quote)
        self.assertIn("data_status", quote)

    def test_search_symbols(self):
        results = self.provider.search_symbols("AAPL")
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["symbol"], "AAPL")

class TestAIBerkshireEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = AIBerkshireEngine(data_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_run_research(self):
        report = self.engine.run_research("AAPL")
        self.assertEqual(report["symbol"], "AAPL")
        self.assertIn("overall_score", report)
        self.assertEqual(len(report["checklist"]), 10)
        self.assertIn("bull_case", report)
        self.assertIn("bear_case", report)

class TestFlaskEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_invest_page_route(self):
        response = self.app.get('/invest')
        self.assertEqual(response.status_code, 200)

    def test_invest_symbol_route(self):
        response = self.app.get('/invest/AAPL')
        self.assertEqual(response.status_code, 200)

    def test_api_market_quote(self):
        response = self.app.get('/api/market/quote?symbol=AAPL')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["symbol"], "AAPL")

    def test_api_trading_place_order(self):
        response = self.app.post('/api/trading/place-order', json={
            "symbol": "AAPL",
            "side": "BUY",
            "quantity": 1,
            "order_type": "Market",
            "price": 180.0,
            "idempotency_key": f"ik_api_test_{os.urandom(4).hex()}"
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

    def test_api_research_run(self):
        response = self.app.post('/api/research/run', json={"symbol": "AAPL"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

if __name__ == '__main__':
    unittest.main()
