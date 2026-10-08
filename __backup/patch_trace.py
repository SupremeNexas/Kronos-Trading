import re
with open("webui/verification_routes.py", "r") as f:
    content = f.read()

content = content.replace("SELECT count(*) FROM paper_orders", "SELECT count(*) FROM scanner_trades")
content = content.replace("SELECT symbol, side, qty, alpaca_order_id FROM paper_orders", "SELECT asset, user_action, position_size, alpaca_order_id FROM scanner_trades")
# Notice we need to change variables mapping: asset is [0], side/qty is in user_action [1] (which is "BUY 1.0"), position_size [2], alpaca_order_id [3]
content = content.replace('f"{last_ord[1]} {last_ord[2]} {last_ord[0]} [ID: {last_ord[3]}]"', 'f"{last_ord[1]} {last_ord[0]} [ID: {last_ord[3]}]"')

with open("webui/verification_routes.py", "w") as f:
    f.write(content)
