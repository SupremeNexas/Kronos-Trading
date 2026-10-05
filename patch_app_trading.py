import re

with open("webui/app.py", "r") as f:
    content = f.read()

# 1. Update api_trading_place_order to store in trade_history
place_order_snippet = """    # === EARLY SIGNAL SCANNER TRACKING ==="""

place_order_new = """
    # === SAVE TO TRADE HISTORY ===
    if res and res.get('success'):
        try:
            from webui.db import get_db_connection, _adapt_query
            import uuid
            conn, _ = get_db_connection()
            cursor = conn.cursor()
            
            order_info = res.get('order', {})
            alpaca_id = order_info.get('order_id', order_info.get('id', ''))
            trade_id = f"trt_{uuid.uuid4().hex[:8]}"
            
            sql = '''
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity, 
                order_type, limit_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity, 
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW'
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Trade history DB tracking failed:", e)

    # === EARLY SIGNAL SCANNER TRACKING ==="""
content = content.replace(place_order_snippet, place_order_new)

# 2. Update api_trades to combine and sync
api_trades_orig = """@app.route('/api/trading/trades', methods=['GET'])
@login_required
def api_trades():
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
        return jsonify({"trades": [], "error": str(e)})"""

api_trades_new_code = """@app.route('/api/trading/trades', methods=['GET'])
@login_required
def api_trades():
    user = get_current_user()
    user_id = user['id']
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    try:
        # Sync open orders from Alpaca to maintain accurate status
        alpaca_orders = broker_adapter.get_orders(status="all") 
        alpaca_dict = {}
        for o in alpaca_orders:
            if o.get('idempotency_key', '').endswith(f"_{user_id}") or not o.get('idempotency_key'):
                # fallback: we match by alpaca order id
                alpaca_dict[o['order_id']] = o

        # Update trade_history from alpaca_dict
        for oid, odata in alpaca_dict.items():
            cursor.execute(_adapt_query(
                "UPDATE trade_history SET status=?, filled_quantity=?, fill_price=? WHERE alpaca_order_id=? AND user_id=?"
            ), (odata['status'], odata['filled_quantity'], odata.get('fill_price', 0.0), oid, user_id))
        conn.commit()

        # Fetch manual trades
        cursor.execute(_adapt_query(\"\"\"
            SELECT submitted_at, symbol, side, quantity, filled_quantity, order_type, 
                   limit_price, fill_price, status, alpaca_order_id
            FROM trade_history
            WHERE user_id = ?
            ORDER BY submitted_at DESC LIMIT 100
        \"\"\"), (user_id,))
        
        trade_rows = cursor.fetchall()
        trades = []
        for r in trade_rows:
            trades.append({
                "date": str(r[0]),
                "symbol": r[1],
                "strategy": "MANUAL",
                "side": r[2],
                "quantity": float(r[3]),
                "filled_quantity": float(r[4]),
                "order_type": r[5],
                "limit_price": float(r[6]) if r[6] else None,
                "fill_price": float(r[7]) if r[7] else None,
                "status": r[8],
                "alpaca_order_id": r[9]
            })

        # Fetch scanner trades (optional legacy compatibility or scanner usage)
        cursor.execute(_adapt_query(\"\"\"
            SELECT timestamp_at, asset, strategy, user_action, position_size, decision, outcome, alpaca_order_id, fill_qty
            FROM scanner_trades
            WHERE user_id = ?
            ORDER BY timestamp_at DESC LIMIT 100
        \"\"\"), (user_id,))
        scanner_rows = cursor.fetchall()
        for r in scanner_rows:
            # check if alpaca_order_id already in trades to avoid duplicates
            if r[7] and any(t['alpaca_order_id'] == r[7] for t in trades):
                continue
                
            qty = abs(float(r[4])) if r[4] else 0.0
            trades.append({
                "date": str(r[0]),
                "symbol": r[1],
                "strategy": r[2] or "SCANNER",
                "side": r[3].split()[0] if r[3] else "UNKNOWN",
                "quantity": qty,
                "filled_quantity": float(r[8] or 0.0),
                "order_type": "MARKET",
                "limit_price": None,
                "fill_price": None, 
                "status": r[6] or "UNKNOWN",
                "alpaca_order_id": r[7] or ""
            })
            
        trades.sort(key=lambda x: x['date'], reverse=True)
            
        return jsonify({"trades": trades})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"trades": [], "error": str(e)})"""

if "SELECT submitted_at" not in content:
    content = content.replace(api_trades_orig, api_trades_new_code)
    
with open("webui/app.py", "w") as f:
    f.write(content)

print("trading logic patched in app.py")
