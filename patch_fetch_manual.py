import re

with open('webui/app.py', 'r') as f:
    text = f.read()

fetch_manual_old = '''        # Fetch manual trades
        cursor.execute(_adapt_query("""
            SELECT submitted_at, symbol, side, quantity, filled_quantity, order_type,
                   limit_price, fill_price, status, alpaca_order_id
            FROM trade_history
            WHERE user_id = ?
            ORDER BY submitted_at DESC LIMIT 100
        """), (user_id,))

        trade_rows = cursor.fetchall()
        trades = []
        for r in trade_rows:
            trades.append({
                "date": str(r[0])[0:19],
                "symbol": r[1],
                "strategy": "MANUAL",
                "side": r[2],
                "quantity": float(r[3]),
                "filled_quantity": float(r[4]) if r[4] else 0.0,
                "order_type": r[5],
                "limit_price": float(r[6]) if r[6] else None,
                "fill_price": float(r[7]) if r[7] else None,
                "status": r[8],
                "order_id": r[9]
            })'''

fetch_manual_new = '''        # Fetch manual trades
        cursor.execute(_adapt_query("""
            SELECT submitted_at, symbol, side, quantity, filled_quantity, order_type,
                   limit_price, fill_price, status, alpaca_order_id,
                   tactic_name, realized_pnl, reasoning, notes
            FROM trade_history
            WHERE user_id = ?
            ORDER BY submitted_at DESC LIMIT 100
        """), (user_id,))

        trade_rows = cursor.fetchall()
        trades = []
        for r in trade_rows:
            trades.append({
                "date": str(r[0])[0:19] if r[0] else "",
                "symbol": r[1],
                "tactic": r[10] or "UNKNOWN",
                "side": r[2],
                "quantity": float(r[3] or 0),
                "filled_quantity": float(r[4] or 0),
                "order_type": r[5],
                "limit_price": float(r[6]) if r[6] else None,
                "fill_price": float(r[7]) if r[7] else None,
                "status": r[8],
                "order_id": r[9],
                "realized_pnl": float(r[11]) if r[11] is not None else None,
                "reasoning": r[12] or "",
                "notes": r[13] or ""
            })'''

text = text.replace(fetch_manual_old, fetch_manual_new)
with open('webui/app.py', 'w') as f:
    f.write(text)
