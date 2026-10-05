import re

with open("webui/app.py", "r") as f:
    content = f.read()

new_routes = """
# ==========================================
# SEBAI EARLY SIGNAL SCANNER (Independent)
# ==========================================
from webui.strategies.early_signal_scanner import EarlySignalScanner

scanner_instance = EarlySignalScanner()

@app.route('/api/scanner/history', methods=['GET'])
def api_scanner_history():
    return jsonify(scanner_instance.get_scan_history())

@app.route('/api/scanner/watchlist', methods=['GET'])
def api_scanner_watchlist():
    return jsonify(scanner_instance.get_watchlist())

@app.route('/api/scanner/scan', methods=['POST'])
def api_scanner_scan():
    data = request.json or {}
    coin_ids = data.get("assets", [])
    manual_mentions = data.get("manual_mentions", {})
    if not isinstance(coin_ids, list) or not coin_ids:
        return jsonify({"error": "assets array required"}), 400
        
    results = scanner_instance.scan_assets(coin_ids, manual_mentions)
    return jsonify(results)
"""

if "# SEBAI EARLY SIGNAL SCANNER" not in content:
    content = content.replace("if __name__ == '__main__':", new_routes + "\nif __name__ == '__main__':")

# Now patch api_trading_place_order
# Find 'def api_trading_place_order():'
idx = content.find("def api_trading_place_order():")
if idx != -1:
    end_of_func = content.find("def ", idx + 10)
    func_content = content[idx:end_of_func]
    
    tracker_code = """
    # === EARLY SIGNAL SCANNER TRACKING ===
    strategy = data.get("strategy")
    if strategy == "EARLY_SIGNAL_SCANNER":
        try:
            import uuid
            from webui.db import get_db_connection, _adapt_query
            
            conn, _ = get_db_connection()
            cursor = conn.cursor()
            
            order_info = res.get('order', {}) if res else {}
            # Allow saving even if res failed, but store outcome
            alpaca_id = order_info.get('order_id', order_info.get('id', ''))
            
            trade_id = f"st_{uuid.uuid4().hex[:8]}"
            
            sql = '''
            INSERT INTO scanner_trades (
                id, signal_scan_id, strategy, asset, signal_score, volume_ratio, 
                attention_score, momentum_7d, decision, user_action, alpaca_order_id, 
                fill_qty, position_size, outcome, timestamp_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            
            outcome_status = "PENDING" if res and res.get("success") else "REJECTED"
            
            cursor.execute(_adapt_query(sql), (
                trade_id,
                data.get("signal_scan_id"),
                "EARLY_SIGNAL_SCANNER",
                symbol,
                int(data.get("signal_score") or 0),
                str(data.get("volume_ratio", "UNKNOWN")),
                str(data.get("attention_score", "UNKNOWN")),
                str(data.get("momentum_7d", "UNKNOWN")),
                data.get("decision", "MANUAL_TRADE"),
                f"{side} {quantity}",
                alpaca_id,
                float(order_info.get('filled_qty', 0)),
                float(quantity if side.upper() == "BUY" else -quantity),
                outcome_status
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Scanner trade DB tracking failed:", e)
    # =====================================
"""
    
    # We will insert it right before `return jsonify(res)` at the end of `api_trading_place_order`.
    # Find the end of `if res.get("success"):` block by looking for the last return before end_of_func
    return_idx = func_content.rfind("return jsonify(res")
    if return_idx != -1:
        new_func_content = func_content[:return_idx] + tracker_code + "    " + func_content[return_idx:]
        content = content[:idx] + new_func_content + content[end_of_func:]

with open("webui/app.py", "w") as f:
    f.write(content)

print("Properly patched webui/app.py")
