with open("tests/test_user_isolation.py", 'r') as f:
    content = f.read()

content = content.replace('"AAPL"', '"TSLA"').replace("'AAPL'", "'TSLA'")

content = content.replace(
    "INSERT INTO orders (id, portfolio_id, symbol, side, order_type) VALUES (?, (SELECT id FROM portfolios WHERE user_id = ? LIMIT 1), ?, ?, ?)",
    "INSERT INTO orders (id, portfolio_id, symbol, side, order_type, quantity) VALUES (?, (SELECT id FROM portfolios WHERE user_id = ? LIMIT 1), ?, ?, ?, 10.0)"
)
with open("tests/test_user_isolation.py", 'w') as f:
    f.write(content)
