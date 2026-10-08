import re

with open("webui/app.py", "r") as f:
    text = f.read()

sql_pattern = r"INSERT INTO trade_history \((.*?)\) VALUES \(\?\*\)"
# I'll just find the exact block and replace it.
block = """
        c.execute(\"\"\"
            INSERT INTO trade_history (
                id, user_id, symbol, side, quantity, fill_price, order_type,
                status, submitted_at, alpaca_order_id, client_order_id, tactic_id, tactic_name, realized_pnl, realized_pnl_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (trade_id, user_id, best_candidate, "SELL", buy_quantity, fill_price + pnl, "Market", 
              "completed", datetime.now().isoformat(), sell_order.get('order', {}).get('order_id', 'o1'), 'c1', tactic_id, tactic_name, pnl, return_pct))
"""

# Let's just do a regex sub for the c.execute block
import re

text = re.sub(r'c\.execute\(\"\"\"\n\s+INSERT INTO trade_history.*?\)\)', block.strip(), text, flags=re.DOTALL)

with open("webui/app.py", "w") as f:
    f.write(text)

