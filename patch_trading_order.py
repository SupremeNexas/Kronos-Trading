with open("webui/app.py", "r") as f:
    text = f.read()

import re

# Fix scanner_trades INSERT
old_sql_1 = '''            INSERT INTO scanner_trades (
                id, signal_scan_id, strategy, asset, signal_score, volume_ratio, 
                attention_score, momentum_7d, decision, user_action, alpaca_order_id, 
                fill_qty, position_size, outcome, timestamp_at'''
new_sql_1 = '''            INSERT INTO scanner_trades (
                id, signal_scan_id, strategy, asset, signal_score, volume_ratio, 
                attention_score, momentum_7d, decision, user_action, alpaca_order_id, 
                fill_qty, position_size, outcome, timestamp_at, user_id'''
                
old_sql_2 = ''') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)'''
new_sql_2 = ''') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)'''

if 'user_id' not in text[text.find('INSERT INTO scanner_trades'):text.find(')', text.find('INSERT INTO scanner_trades')+200)]:
    text = text.replace(old_sql_1, new_sql_1)
    text = text.replace(old_sql_2, new_sql_2)

    # find the execute call and append user_id
    text = re.sub(
        r'(outcome_status\s*\)\))',
        r'outcome_status, user_id))',
        text
    )

with open("webui/app.py", "w") as f:
    f.write(text)
