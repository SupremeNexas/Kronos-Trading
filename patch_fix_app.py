import re

with open('webui/app.py', 'r') as f:
    content = f.read()

# Delete old scanner history and watchlist and scan methods (they are unprotected)
content = re.sub(
    r"@app\.route\('/api/scanner/history', methods=\\?\['GET'\\]\).*?def api_scanner_scan\(\):.*?return jsonify\(results\)",
    "",
    content,
    flags=re.DOTALL
)

# Replace the protected /api/scanner-history to also be accessible.
# Actually I already added /api/scanner/history in my previous patch_scanner_routes_app.py but that must have failed or appended duplicates.
# Let's just fix the remaining duplicates.

content = content.replace("def api_scanner_history_2():", "def api_scanner_history():")

with open('webui/app.py', 'w') as f:
    f.write(content)
