import re

with open("webui/app.py", "r") as f:
    content = f.read()

content = content.replace("    else:\n        \n    # === EARLY", "    # === EARLY")
# Now we need to append the missing else part after tracking!
tracker_end = "# ====================================="
replacement = tracker_end + "\n\n    if res and res.get('success'):\n        return jsonify(res)\n    else:\n        return jsonify(res), 400"

content = content.replace(tracker_end + "\n    return jsonify(res), 400", replacement)

# Let me clean up any potential leftover `if res.get("success"): \n return jsonify(res)` before this.
content = content.replace('    if res.get("success"):\n        return jsonify(res)\n', '')

with open("webui/app.py", "w") as f:
    f.write(content)
