import sys

with open("webui/broker_service_alpaca.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "def get_trading_mode" in line:
        # insert get_tradable_assets before this
        new_lines.insert(len(new_lines) - 1, 
"""
    def get_tradable_assets(self, asset_class="us_equity"):
        if not self.available:
            return []
        try:
            from alpaca.trading.requests import GetAssetsRequest
            from alpaca.trading.enums import AssetClass
            ac = AssetClass.US_EQUITY if asset_class == "us_equity" else AssetClass.CRYPTO
            req = GetAssetsRequest(asset_class=ac, status="active")
            assets = self.client.get_all_assets(req)
            return [a.symbol for a in assets if a.tradable and a.fractionable]
        except Exception as e:
            logging.error(f"Alpaca get_tradable_assets error: {e}")
            return []
""")

with open("webui/broker_service_alpaca.py", "w") as f:
    f.writelines(new_lines)
