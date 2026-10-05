import re

with open("webui/app.py", "r") as f:
    text = f.read()

old_code = """if ALPACA_AVAILABLE and os.environ.get("ALPACA_API_KEY"):
    broker_adapter = AlpacaBrokerAdapter()
else:
    broker_adapter = MockBrokerAdapter(db_path)"""

new_code = """is_prod = os.environ.get("RENDER") is not None

if is_prod:
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
        broker_adapter = MockBrokerAdapter(db_path)"""

text = text.replace(old_code, new_code)

with open("webui/app.py", "w") as f:
    f.write(text)
