with open("webui/app.py", "r") as f:
    text = f.read()

text = text.replace("broker_order_id, client_order_id, alpaca_order_id", "alpaca_order_id, client_order_id")
text = text.replace("sell_order.get('order', {}).get('order_id', 'o1'), 'c1', 'a1', tactic_id,", "sell_order.get('order', {}).get('order_id', 'o1'), 'c1', tactic_id,")

with open("webui/app.py", "w") as f:
    f.write(text)

