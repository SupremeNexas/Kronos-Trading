import re

with open("webui/db.py", "r") as f:
    content = f.read()

# Fix scanner_history (remove trailing commas carefully)
content = re.sub(r'signal_scan_id VARCHAR\(255\)[ \n]*,', r'signal_scan_id VARCHAR(255) PRIMARY KEY,', content)
content = re.sub(r'reasons TEXT,[ \n]*PRIMARY KEY\(user_id, asset\)', r'reasons TEXT', content)

with open("webui/db.py", "w") as f:
    f.write(content)

print("Fixed scanner_history PK in db.py")
