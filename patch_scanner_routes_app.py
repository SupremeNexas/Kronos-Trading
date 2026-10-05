import re

with open('webui/app.py', 'r') as f:
    content = f.read()

new_routes = """
@app.route('/api/scanner/history', methods=['GET'])
@login_required
def api_scanner_history_old():
    user = get_current_user()
    return jsonify(scanner_instance.get_scan_history(user_id=user['id']))

@app.route('/api/scanner/watchlist', methods=['GET'])
@login_required
def api_scanner_watchlist():
    user = get_current_user()
    return jsonify(scanner_instance.get_watchlist(user_id=user['id']))

@app.route('/api/scanner/scan', methods=['POST'])
@login_required
def api_scanner_scan():
    user = get_current_user()
    data = request.json or {}
    coin_ids = data.get("assets", [])
    manual_mentions = data.get("manual_mentions", {})
    if not isinstance(coin_ids, list) or not coin_ids:
        return jsonify({"error": "assets array required"}), 400
        
    results = scanner_instance.scan_assets(coin_ids, manual_mentions, user_id=user['id'])
    return jsonify(results)
"""

content = re.sub(
    r"@app\.route\('/api/scanner/history', methods=\\?\['GET'\\]\).*?def api_scanner_scan\(\):.*?return jsonify\(results\)",
    new_routes.strip(),
    content,
    flags=re.DOTALL
)

with open('webui/app.py', 'w') as f:
    f.write(content)
