import re

with open("webui/db.py", "r") as f:
    content = f.read()

# Restore PRIMARY KEY(user_id, asset) for scanner_watchlist
def repl(m):
    return m.group(0).replace("signal_scan_id VARCHAR(255) PRIMARY KEY", "signal_scan_id VARCHAR(255)").replace("reasons TEXT", "reasons TEXT,\n        PRIMARY KEY(user_id, asset)")

content = re.sub(r'(CREATE TABLE IF NOT EXISTS scanner_watchlist \([^;]*?reasons TEXT\n[ ]*\))', repl, content, flags=re.DOTALL)

with open("webui/db.py", "w") as f:
    f.write(content)

print("Fixed scanner_watchlist in db.py")
