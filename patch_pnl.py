def compute_realized_pnl(user_id):
    from webui.db import get_db_connection, _adapt_query
    conn, _ = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(_adapt_query("""
        SELECT id, symbol, side, filled_quantity, fill_price, realized_pnl
        FROM trade_history
        WHERE user_id = ? AND status IN ('filled', 'FILLED', 'closed', 'CLOSED')
        ORDER BY submitted_at ASC
    """), (user_id,))

    trades = cursor.fetchall()

    # symbol -> list of dicts: {'id': trade_id, 'qty': remaining_qty, 'price': fill_price}
    inventory = {}
    updates = []

    for r in trades:
        t_id, sym, side, qty, price, pnl = r[0], r[1], r[2].upper(), r[3], r[4], r[5]
        if qty <= 0: continue

        if sym not in inventory:
            inventory[sym] = {'LONG': [], 'SHORT': []}

        if side == 'BUY':
            if len(inventory[sym]['SHORT']) > 0:
                # Covering short
                left_to_cover = qty
                realized = 0.0
                while left_to_cover > 0 and len(inventory[sym]['SHORT']) > 0:
                    entry = inventory[sym]['SHORT'][0]
                    cover_qty = min(left_to_cover, entry['qty'])
                    # Short PnL: entry price - exit price
                    realized += (entry['price'] - price) * cover_qty
                    left_to_cover -= cover_qty
                    entry['qty'] -= cover_qty
                    if entry['qty'] <= 0:
                        inventory[sym]['SHORT'].pop(0)

                updates.append((realized, t_id))
                if left_to_cover > 0:
                    inventory[sym]['LONG'].append({'id': t_id, 'qty': left_to_cover, 'price': price})
            else:
                inventory[sym]['LONG'].append({'id': t_id, 'qty': qty, 'price': price})

        elif side == 'SELL':
            if len(inventory[sym]['LONG']) > 0:
                # Selling long
                left_to_sell = qty
                realized = 0.0
                while left_to_sell > 0 and len(inventory[sym]['LONG']) > 0:
                    entry = inventory[sym]['LONG'][0]
                    sell_qty = min(left_to_sell, entry['qty'])
                    # Long PnL: exit price - entry price
                    realized += (price - entry['price']) * sell_qty
                    left_to_sell -= sell_qty
                    entry['qty'] -= sell_qty
                    if entry['qty'] <= 0:
                        inventory[sym]['LONG'].pop(0)

                updates.append((realized, t_id))
                if left_to_sell > 0:
                    inventory[sym]['SHORT'].append({'id': t_id, 'qty': left_to_sell, 'price': price})
            else:
                inventory[sym]['SHORT'].append({'id': t_id, 'qty': qty, 'price': price})

    for pnl, t_id in updates:
        cursor.execute(_adapt_query("UPDATE trade_history SET realized_pnl = ? WHERE id = ?"), (pnl, t_id))

    conn.commit()
    conn.close()
