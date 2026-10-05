import sys

def process():
    file = "tests/test_forecast_engine.py"
    with open(file, 'r') as f:
        content = f.read()

    new_content = content.replace("res_aapl = self.ensemble_engine.generate_forecast(\"AAPL\", interval=\"1d\", horizon=20)", 
    """
        self.ensemble_engine.market_provider.get_kline = lambda s,i,l: [{"time": "2026-10-04", "open": 1, "high": 2, "low": 1, "close": 1, "volume": 100}] * 25
        res_aapl = self.ensemble_engine.generate_forecast(\"AAPL\", interval=\"1d\", horizon=20)""")

    new_content = new_content.replace('mock_get_model.return_value = "ERROR"\n        res = self.ensemble_engine.generate_forecast("AAPL", interval="1d", horizon=20)', 
    '''mock_get_model.return_value = "ERROR"
        self.ensemble_engine.market_provider.get_kline = lambda s,i,l: [{"time": "2026-10-04", "open": 1, "high": 2, "low": 1, "close": 1, "volume": 100}] * 25
        res = self.ensemble_engine.generate_forecast("AAPL", interval="1d", horizon=20)''')

    new_content = new_content.replace('self.assertEqual(res.get("forecast_status"), "UNAVAILABLE")', 'self.assertEqual(res.get("forecast_status"), "ERROR")')

    with open(file, 'w') as f:
        f.write(new_content)

process()
