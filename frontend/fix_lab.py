import re
with open('/Users/supryo/Desktop/Kronos-master/webui/app.py', 'r') as f:
    text = f.read()

# Fix the db fetching 
old = """        data = _adapt_query(conn, "SELECT pr.id, pr.prediction, po.actual FROM prediction_runs pr JOIN prediction_outcomes po ON pr.id = po.prediction_id", fetchall=True)
        conn.close()"""
new = """        cursor = conn.cursor()
        cursor.execute(_adapt_query("SELECT pr.symbol, pr.expected_return, po.actual_return, po.prediction_outcome FROM prediction_runs pr JOIN prediction_outcomes po ON pr.id = po.prediction_id"))
        rows = cursor.fetchall()
        
        data = []
        for r in rows:
            data.append({
                "symbol": r[0],
                "forecast": {"expected_return_pct": r[1]},
                "pnl_pct": r[2],
                "outcome": r[3]
            })
        conn.close()"""
text = text.replace(old, new)

# And fix fetching the trades ledger
old2 = """        data = _adapt_query(conn, "SELECT * FROM trade_proposals tp JOIN paper_orders po ON tp.id = po.trade_id", fetchall=True)
        conn.close()"""
new2 = """        cursor = conn.cursor()
        cursor.execute(_adapt_query("SELECT tp.id, tp.symbol, tp.side, tp.proposed_quantity, tp.order_type, tp.limit_price, tp.risk_status, tp.confirmation_state, tp.created_at, po.alpaca_order_id, po.order_status, po.actual_fill_price, po.filled_quantity FROM trade_proposals tp JOIN paper_orders po ON tp.id = po.trade_id"))
        rows = cursor.fetchall()
        data = []
        for r in rows:
             data.append({
                 "id": r[0], "symbol": r[1], "side": r[2], "proposed_quantity": r[3],
                 "order_type": r[4], "limit_price": r[5], "risk_status": r[6],
                 "confirmation_state": r[7], "created_at": r[8], "alpaca_order_id": r[9],
                 "order_status": r[10], "actual_fill_price": r[11], "filled_quantity": r[12]
             })
        conn.close()"""
text = text.replace(old2, new2)

with open('/Users/supryo/Desktop/Kronos-master/webui/app.py', 'w') as f:
    f.write(text)
