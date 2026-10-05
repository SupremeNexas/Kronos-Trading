import re
with open("webui/verification_routes.py", "r") as f:
    content = f.read()

content = content.replace("ORDER BY created_at DESC LIMIT 1", "ORDER BY timestamp_at DESC LIMIT 1")

with open("webui/verification_routes.py", "w") as f:
    f.write(content)
