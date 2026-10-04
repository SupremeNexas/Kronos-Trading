with open("acceptance_test.py", "r") as f:
    text = f.read()

text = text.replace('"order_state": entry.get("order_id")', '"order_state": entry.get("paper_order_id")')

with open("acceptance_test.py", "w") as f:
    f.write(text)
