with open("webui/broker_service_alpaca.py", "r") as f:
    content = f.read()

content = content.replace(
    '                    "filled_quantity": float(o.filled_qty) if o.filled_qty else 0.0,',
    '                    "filled_quantity": float(o.filled_qty) if o.filled_qty else 0.0,\n                    "fill_price": float(o.filled_avg_price) if getattr(o, "filled_avg_price", None) else 0.0,'
)

with open("webui/broker_service_alpaca.py", "w") as f:
    f.write(content)

print("broker patched")
