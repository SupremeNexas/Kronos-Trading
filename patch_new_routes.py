import re

with open('webui/app.py', 'r') as f:
    content = f.read()

new_routes = """
@app.route('/api/forecast-history', methods=['GET'])
@login_required
def api_forecast_history():
    user = get_current_user()
    history = DatabaseManager.get_forecast_history(user['id'])
    return jsonify({"forecasts": history})

@app.route('/api/scanner-history', methods=['GET'])
@login_required
def api_scanner_history():
    user = get_current_user()
    # Simple query for scanner history
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(_adapt_query("SELECT signal_scan_id, asset, score, decision, timestamp_at, strategy_version FROM scanner_history WHERE user_id = ? ORDER BY timestamp_at DESC LIMIT 100"), (user['id'],))
        history = []
        for r in cursor.fetchall():
            history.append({
                "signal_scan_id": r[0],
                "asset": r[1],
                "score": r[2],
                "decision": r[3],
                "timestamp": str(r[4]) if r[4] else None,
                "strategy_version": r[5]
            })
        return jsonify({"scanner_history": history})
    finally:
        conn.close()

@app.route('/api/trading/trades', methods=['GET'])
@login_required
def api_trades():
    user = get_current_user()
    # Fetch from orders / executions / paper_orders
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    try:
        # Simplistic mapping mostly fetching from `orders` and `executions` 
        cursor.execute(_adapt_query(\"\"\"
            SELECT o.created_at, o.symbol, o.order_type, o.side, o.quantity, 
                   o.filled_quantity, o.status, o.alpaca_order_id, 
                   e.price, o.id
            FROM orders o
            LEFT JOIN executions e ON o.id = e.order_id
            WHERE o.portfolio_id IN (SELECT id FROM portfolios WHERE user_id = ?)
            ORDER BY o.created_at DESC LIMIT 100
        \"\"\"), (user['id'],))
        
        res = []
        for r in cursor.fetchall():
            res.append({
                "date": str(r[0]),
                "symbol": r[1],
                "strategy": "MANUAL" if r[2] == "Market" else r[2],
                "side": r[3],
                "quantity": r[4],
                "filled": r[5],
                "status": r[6],
                "alpaca_order_id": r[7],
                "price": r[8],
                "order_id": r[9]
            })
        return jsonify({"trades": res})
    finally:
        conn.close()

@app.route('/api/trading/my-stocks', methods=['GET'])
@login_required
def api_my_stocks():
    user = get_current_user()
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    try:
        pf_sum = DatabaseManager.get_portfolio_summary(user['id'])
        positions = pf_sum.get("positions", {})
        
        # Also grab watched
        cursor.execute(_adapt_query("SELECT symbol FROM watchlist_items WHERE watchlist_id IN (SELECT id FROM watchlists WHERE user_id = ?)"), (user['id'],))
        watched = [r[0] for r in cursor.fetchall()]
        
        # Merge unique
        all_syms = set(positions.keys()).union(set(watched))
        stocks = []
        for s in all_syms:
            stocks.append({
                "symbol": s,
                "position": positions.get(s, {}).get("quantity", 0),
                "avg_entry": positions.get(s, {}).get("avg_entry_price", 0),
                "watched": s in watched
            })
        return jsonify({"stocks": stocks})
    finally:
        conn.close()
"""

if "def api_forecast_history" not in content:
    content += "\n" + new_routes

with open('webui/app.py', 'w') as f:
    f.write(content)
