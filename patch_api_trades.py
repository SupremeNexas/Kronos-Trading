with open("webui/app.py", "r") as f:
    text = f.read()

import re

new_api_trades = """def api_trades():
    user = get_current_user()
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(_adapt_query(\"\"\"
            SELECT timestamp_at, asset, strategy, user_action, position_size, decision, outcome, alpaca_order_id, signal_scan_id
            FROM scanner_trades
            WHERE user_id = ?
            ORDER BY timestamp_at DESC LIMIT 100
        \"\"\"), (user['id'],))
        
        res = []
        for r in cursor.fetchall():
            res.append({
                "date": str(r[0]),
                "symbol": r[1],
                "strategy": r[2] or "MANUAL",
                "side": r[3] if r[3] else "UNKNOWN",
                "quantity": abs(float(r[4])) if r[4] else 0.0,
                "status": r[6] or "UNKNOWN",
                "price": None, # Price ideally from alpaca execution or other storage
                "alpaca_order_id": r[7] or "",
                "signal_scan_id": r[8] or ""
            })
        return jsonify({"trades": res})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "trades": []})
    finally:
        conn.close()"""

text = re.sub(r'def api_trades\(\):.*?(?=def api_my_stocks\(\):)', new_api_trades + '\n\n@app.route(\'/api/trading/my-stocks\', methods=[\'GET\'])\n@login_required\n', text, flags=re.DOTALL)

with open("webui/app.py", "w") as f:
    f.write(text)
