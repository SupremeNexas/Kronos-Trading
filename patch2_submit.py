import re

with open('webui/app.py', 'r') as f:
    text = f.read()

# I will find the EXACT string and replace it. I'll read it directly.
search_str = """            sql = '''
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity,
                order_type, limit_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity,
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW'
            ))"""

replace_str = """            sql = '''
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity,
                order_type, limit_price, status, tactic_id, tactic_name, reasoning, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            t_id = data.get('tactic_id', 'tactic_manual')
            t_name = data.get('tactic_name', 'MANUAL')
            reas = data.get('reasoning', '')
            notz = data.get('notes', '')

            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity,
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW',
                t_id, t_name, reas, notz
            ))"""

if search_str in text:
    print("Match found!")
    text = text.replace(search_str, replace_str)
else:
    print("No exact match.")

with open('webui/app.py', 'w') as f:
    f.write(text)
