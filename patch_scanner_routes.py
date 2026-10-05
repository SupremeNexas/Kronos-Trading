with open("webui/app.py", "r") as f:
    text = f.read()

import re

# Patch scanner history
hist_pattern = r"def api_scanner_history\(\):\n.*?conn\.close\(\)"
new_hist = """def api_scanner_history():
    user = get_current_user()
    try:
        res = scanner_instance.get_scan_history(user_id=user['id'])
        return jsonify({"scanner_history": res})
    except Exception as e:
        return jsonify({"scanner_history": [], "error": str(e)})"""
text = re.sub(hist_pattern, new_hist, text, flags=re.DOTALL)

# Patch scanner watchlist
wl_pattern = r"def api_scanner_watchlist\(\):\n\s+user = get_current_user\(\)\n\s+return jsonify\(scanner_instance\.get_watchlist\(user_id=user\['id'\]\)\)"
new_wl = """def api_scanner_watchlist():
    user = get_current_user()
    try:
        res = scanner_instance.get_watchlist(user_id=user['id'])
        return jsonify({"watchlist": res})
    except Exception as e:
        return jsonify({"watchlist": [], "error": str(e)})"""
text = re.sub(wl_pattern, new_wl, text, flags=re.DOTALL)

with open("webui/app.py", "w") as f:
    f.write(text)
