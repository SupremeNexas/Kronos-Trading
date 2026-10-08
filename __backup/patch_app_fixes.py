import re

with open('webui/app.py', 'r') as f:
    content = f.read()

# Fix the missing imports
if 'from webui.db import get_db_connection' not in content:
    content = content.replace(
        'from webui.db import DatabaseManager', 
        'from webui.db import DatabaseManager, get_db_connection, _adapt_query'
    )

# Fix the duplicate scanner history and replace old un-authed endpoints
# First, remove the two unprotected endpoints entirely.
old_unprotected = """@app.route('/api/scanner/history', methods=['GET'])
def api_scanner_history():
    return jsonify(scanner_instance.get_scan_history())"""

content = content.replace(old_unprotected, "")

old_unprotected_wl = """@app.route('/api/scanner/watchlist', methods=['GET'])
def api_scanner_watchlist():
    return jsonify(scanner_instance.get_watchlist())"""

content = content.replace(old_unprotected_wl, "")

# Now rename api_scanner_history_2 to api_scanner_history
content = content.replace("def api_scanner_history_2():", "def api_scanner_history():")

# Replace route path for api_scanner_history_2 which is /api/scanner-history to /api/scanner/history
content = content.replace("@app.route('/api/scanner-history', methods=['GET'])", "@app.route('/api/scanner/history', methods=['GET'])")

import_b = """@app.route('/api/scanner/watchlist', methods=['GET'])
@login_required
def api_scanner_watchlist():
    user = get_current_user()
    return jsonify(scanner_instance.get_watchlist(user_id=user['id']))"""

# Add api_scanner_watchlist back if it was removed
if "api_scanner_watchlist" not in content:
   content += "\n" + import_b

with open('webui/app.py', 'w') as f:
    f.write(content)
