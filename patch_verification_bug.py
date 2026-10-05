import re
with open("webui/verification_routes.py", "r") as f:
    content = f.read()

content = content.replace(
    'cursor.execute("SELECT symbol, total_score, decision FROM scanner_history ORDER BY scanned_at DESC LIMIT 1")',
    'cursor.execute("SELECT asset, score, decision FROM scanner_history ORDER BY timestamp_at DESC LIMIT 1")'
)

# And add error output for trace failing
content = content.replace(
    'trace_feat["status"] = "FAILED"',
    'trace_feat["status"] = "FAILED"\n            trace_feat["evidence"]["error"] = str(e)'
)

with open("webui/verification_routes.py", "w") as f:
    f.write(content)
