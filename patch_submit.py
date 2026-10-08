import re

with open('webui/app.py', 'r') as f:
    content = f.read()

old_block = '''            sql = \'\'\'
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity,
                order_type, limit_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \'\'\'
            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity,
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW'
            ))'''

new_block = '''            sql = \'\'\'
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity,
                order_type, limit_price, status, tactic_id, tactic_name, reasoning, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \'\'\'
            # Actually get tactic fields from data
            t_id = data.get('tactic_id', 'tactic_manual')
            t_name = data.get('tactic_name', 'MANUAL')
            reas = data.get('reasoning', '')
            notz = data.get('notes', '')

            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity,
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW',
                t_id, t_name, reas, notz
            ))'''

content = content.replace(old_block, new_block)

with open('webui/app.py', 'w') as f:
    f.write(content)
print("Updated successfully.")
