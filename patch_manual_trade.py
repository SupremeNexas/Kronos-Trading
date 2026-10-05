import sys

def patch_app():
    with open('webui/app.py', 'r') as f:
        content = f.read()

    replacement = """
    if res.get("success"):
        try:
            import uuid
            from webui.db import get_db_connection, _adapt_query
            conn, _ = get_db_connection()
            cursor = conn.cursor()
            trade_id = f"mnl_{uuid.uuid4().hex[:8]}"
            prediction_id = "MANUAL_TRADE"
            run_id = "MANUAL"
            
            # Record proposal
            sql1 = "INSERT INTO trade_proposals (id, prediction_id, run_id, symbol, side, proposed_quantity, approved_quantity, order_type, limit_price, validation_status, risk_status, confirmation_state, reason, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)"
            cursor.execute(_adapt_query(sql1), (
                trade_id, prediction_id, run_id, symbol, side, quantity, quantity, order_type, price, "PASS", "ALLOW", "CONFIRMED", "Manual Terminal Action"
            ))
            
            # Record order
            order_info = res.get('order', {})
            alpaca_id = order_info.get('order_id', order_info.get('id', ''))
            
            sql2 = "INSERT INTO paper_orders (id, trade_id, alpaca_order_id, order_status, actual_fill_price, filled_quantity, submitted_at) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)"
            po_id = f"po_{uuid.uuid4().hex[:8]}"
            cursor.execute(_adapt_query(sql2), (
                po_id, trade_id, alpaca_id, "submitted", 0.0, 0.0
            ))
            conn.commit()
            conn.close()
        except Exception as ex:
            print("DB tracking failed:", ex)
        return jsonify(res)
"""
    new_content = content.replace('    if res.get("success"):\n        return jsonify(res)', replacement)
    
    with open('webui/app.py', 'w') as f:
        f.write(new_content)

patch_app()
