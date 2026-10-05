import re
with open("webui/db.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "CREATE TABLE IF NOT EXISTS scanner_trades" in line and not any("trade_history" in content for content in new_lines[-5:]):
        new_lines.append("""
    \"\"\"CREATE TABLE IF NOT EXISTS trade_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        alpaca_order_id TEXT NOT NULL,
        client_order_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        filled_quantity REAL DEFAULT 0.0,
        order_type TEXT NOT NULL,
        limit_price REAL,
        fill_price REAL,
        status TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        filled_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )\"\"\",
""")

with open("webui/db.py", "w") as f:
    f.writelines(new_lines)
