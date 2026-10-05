import re

with open("webui/broker_service_alpaca.py", "r") as f:
    text = f.read()

text = text.replace(
    'api_key = os.environ.get("ALPACA_API_KEY", "")',
    'api_key = os.environ.get("ALPACA_API_KEY", "") or os.environ.get("APCA_API_KEY_ID", "")'
)
text = text.replace(
    'secret_key = os.environ.get("ALPACA_SECRET_KEY", "")',
    'secret_key = os.environ.get("ALPACA_SECRET_KEY", "") or os.environ.get("APCA_API_SECRET_KEY", "")'
)

with open("webui/broker_service_alpaca.py", "w") as f:
    f.write(text)
