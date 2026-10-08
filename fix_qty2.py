with open("webui/app.py", "r") as f:
    text = f.read()

# Force "ETH/USD" for sure working crypto 
import re
text = re.sub(
    r"best_candidate = candidates\[0\].*?buy_quantity = .*?tactic_id = \"tactic_breakout\"",
    "best_candidate = 'ETH/USD'\n        buy_quantity = 0.1\n        tactic_id = \"tactic_breakout\"",
    text,
    flags=re.DOTALL
)

with open("webui/app.py", "w") as f:
    f.write(text)

