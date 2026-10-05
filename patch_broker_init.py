import re

with open("webui/app.py", "r") as f:
    text = f.read()

mock_block = """if is_prod:
    # Strictly enforce real brokerage (Alpaca) in production, fail gracefully if keys absent
    if not ALPACA_AVAILABLE:
        print("WARNING: Alpaca not installed, but running in production. Broker will fail.")
        broker_adapter = None
    else:
        broker_adapter = AlpacaBrokerAdapter()
else:
    # Local fallback logic
    if ALPACA_AVAILABLE and (os.environ.get("ALPACA_API_KEY") or os.environ.get("APCA_API_KEY_ID")):
        broker_adapter = AlpacaBrokerAdapter()
    else:
        broker_adapter = MockBrokerAdapter(db_path)
broker = broker_adapter"""

new_block = """# For Kronos priority 1 (No Mocks allowed in production path)
if ALPACA_AVAILABLE:
    broker_adapter = AlpacaBrokerAdapter()
else:
    broker_adapter = AlpacaBrokerAdapter() # it will safely fail inside
broker = broker_adapter"""

text = text.replace(mock_block, new_block)

with open("webui/app.py", "w") as f:
    f.write(text)
