import os
from alpaca.trading.client import TradingClient

api_key = os.environ.get("ALPACA_API_KEY", "") or os.environ.get("APCA_API_KEY_ID", "")
secret_key = os.environ.get("ALPACA_SECRET_KEY", "") or os.environ.get("APCA_API_SECRET_KEY", "")
client = TradingClient(api_key, secret_key, paper=True)

print(dir(client))
