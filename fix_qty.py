with open("webui/app.py", "r") as f:
    text = f.read()

# Replace buy_quantity
text = text.replace("buy_quantity = 0.05 if \"ETH/USD\" in best_candidate else 5.0",
"buy_quantity = 0.05 if \"ETH/USD\" in best_candidate else 1000.0")  # larger quantity for cheap coins

with open("webui/app.py", "w") as f:
    f.write(text)

