import re

with open('webui/app.py', 'r') as f:
    content = f.read()

# Replace place_order endpoint with proper tactic handling
old_place_order = '''@app.route('/api/trading/place-order', methods=['POST'])
@login_required
def api_trading_place_order():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']

    data = request.get_json() or {}
    symbol = data.get('symbol')
    side = data.get('side', 'BUY')
    quantity = float(data.get('quantity', 0))
    order_type = data.get('order_type', 'Market')
    price = float(data.get('price', 0))
    trigger_price = float(data.get('trigger_price', 0))
    time_in_force = data.get('time_in_force', 'DAY')
    idempotency_key = data.get('idempotency_key') or f"m_{uuid.uuid4().hex[:8]}"

    # Add user_id to idempotency_key for filtering later
    if not idempotency_key.endswith(f"_{user_id}"):
        idempotency_key = f"{idempotency_key}_{user_id}"

    if not symbol or quantity <= 0 or (order_type.lower() != 'market' and price <= 0):
        return jsonify({'success': False, 'error': 'Missing or invalid parameters: symbol, quantity must be valid, and limit orders require price > 0.'}), 400

    track_event('paper_order_submitted', {'symbol': symbol, 'side': side, 'quantity': quantity})
    res = broker_adapter.place_order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=order_type,
        price=price,
        trigger_price=trigger_price,
        time_in_force=time_in_force,
        idempotency_key=idempotency_key
    )


    # === SAVE TO TRADE HISTORY ===
    if res and res.get('success'):
        try:
            from webui.db import get_db_connection, _adapt_query
            conn, _ = get_db_connection()
            cursor = conn.cursor()

            order_info = res.get('order', {})
            alpaca_id = order_info.get('order_id', order_info.get('id', ''))
            trade_id = f"trt_{uuid.uuid4().hex[:8]}"

            sql = \'\'\'
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity,
                order_type, limit_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \'\'\'
            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity,
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW'
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Trade history DB tracking failed:", e)


    # === SAVE TO TRADE HISTORY ===
    if res and res.get('success'):
        try:
            from webui.db import get_db_connection, _adapt_query
            conn, _ = get_db_connection()
            cursor = conn.cursor()

            order_info = res.get('order', {})
            alpaca_id = order_info.get('order_id', order_info.get('id', ''))
            trade_id = f"trt_{uuid.uuid4().hex[:8]}"

            sql = \'\'\'
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity,
                order_type, limit_price, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \'\'\'
            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity,
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW'
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Trade history DB tracking failed:", e)'''

new_place_order = '''@app.route('/api/trading/place-order', methods=['POST'])
@login_required
def api_trading_place_order():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']

    data = request.get_json() or {}
    symbol = data.get('symbol')
    side = data.get('side', 'BUY')
    quantity = float(data.get('quantity', 0))
    order_type = data.get('order_type', 'Market')
    price = float(data.get('price', 0))
    trigger_price = float(data.get('trigger_price', 0))
    time_in_force = data.get('time_in_force', 'DAY')
    idempotency_key = data.get('idempotency_key') or f"m_{uuid.uuid4().hex[:8]}"

    # Tactic params
    tactic_id = data.get('tactic_id')
    tactic_name = data.get('tactic_name')
    reasoning = data.get('reasoning')
    notes = data.get('notes')

    # Add user_id to idempotency_key for filtering later
    if not idempotency_key.endswith(f"_{user_id}"):
        idempotency_key = f"{idempotency_key}_{user_id}"

    if not symbol or quantity <= 0 or (order_type.lower() != 'market' and price <= 0):
        return jsonify({'success': False, 'error': 'Missing or invalid parameters: symbol, quantity must be valid, and limit orders require price > 0.'}), 400

    track_event('paper_order_submitted', {'symbol': symbol, 'side': side, 'quantity': quantity})
    res = broker_adapter.place_order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=order_type,
        price=price,
        trigger_price=trigger_price,
        time_in_force=time_in_force,
        idempotency_key=idempotency_key
    )

    # === SAVE TO TRADE HISTORY ===
    if res and res.get('success'):
        try:
            from webui.db import get_db_connection, _adapt_query
            conn, _ = get_db_connection()
            cursor = conn.cursor()

            order_info = res.get('order', {})
            alpaca_id = order_info.get('order_id', order_info.get('id', ''))
            trade_id = f"trt_{uuid.uuid4().hex[:8]}"

            sql = \'\'\'
            INSERT INTO trade_history (
                id, user_id, alpaca_order_id, client_order_id, symbol, side, quantity,
                order_type, limit_price, status, tactic_id, tactic_name, reasoning, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            \'\'\'
            cursor.execute(_adapt_query(sql), (
                trade_id, user_id, alpaca_id, idempotency_key, symbol, side, quantity,
                order_type, price if order_type.upper() != 'MARKET' else 0.0, 'NEW',
                tactic_id, tactic_name, reasoning, notes
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Trade history DB tracking failed:", e)'''

content = content.replace(old_place_order, new_place_order)

with open('webui/app.py', 'w') as f:
    f.write(content)
print("Updated api_trading_place_order in app.py")
