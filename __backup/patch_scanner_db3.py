import re

with open("webui/db.py", "r") as f:
    content = f.read()

# Remove PRIMARY KEY from signal_scan_id in scanner_trades
def repl(m):
    return m.group(0).replace("signal_scan_id VARCHAR(255) PRIMARY KEY,", "signal_scan_id VARCHAR(255),")

content = re.sub(r'(CREATE TABLE IF NOT EXISTS scanner_trades \([^;]*?timestamp_at TIMESTAMP\n[ ]*\))', repl, content, flags=re.DOTALL)

with open("webui/db.py", "w") as f:
    f.write(content)

print("Fixed scanner_trades in db.py")
