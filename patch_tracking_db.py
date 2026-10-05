import re

with open("webui/app.py", "r") as f:
    content = f.read()

# Replace the early signal scanner tracking block
start_marker = "# === EARLY SIGNAL SCANNER TRACKING ==="
end_marker = "# ====================================="

idx_start = content.find(start_marker)
idx_end = content.find(end_marker) + len(end_marker)

new_block = """
    # === EARLY SIGNAL SCANNER TRACKING ===
    strategy = data.get("strategy")
    if strategy == "EARLY_SIGNAL_SCANNER":
        try:
            import uuid
            from webui.db import get_db_connection, _adapt_query
            
            conn, _ = get_db_connection()
            cursor = conn.cursor()
            
            order_info = res.get('order', {})
            alpaca_id = order_info.get('order_id', order_info.get('id', ''))
            
            trade_id = f"st_{uuid.uuid4().hex[:8]}"
            
            sql = '''
            INSERT INTO scanner_trades (
                id, signal_scan_id, strategy, asset, signal_score, volume_ratio, 
                attention_score, momentum_7d, decision, user_action, alpaca_order_id, 
                fill_qty, position_size, outcome, timestamp_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            '''
            
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
                "PENDING"
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Scanner trade DB tracking failed:", e)
    # =====================================
"""

content = content[:idx_start] + new_block.strip() + "\n" + content[idx_end:]

with open("webui/app.py", "w") as f:
    f.write(content)
print("Updated Early Signal Scanner tracking in webui/app.py")
