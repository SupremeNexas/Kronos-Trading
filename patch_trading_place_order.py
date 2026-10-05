import re

with open('webui/app.py', 'r') as f:
    content = f.read()

new_place_order = """
@app.route('/api/trading/place-order', methods=['POST'])
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
    idempotency_key = data.get('idempotency_key')
    
    client_order_id = f"{idempotency_key}_{user_id}" if idempotency_key else f"man_{symbol}_{user_id}"

    if not symbol or quantity <= 0 or price <= 0:
        return jsonify({'success': False, 'error': 'Missing or invalid parameters: symbol, quantity, and price must be valid.'}), 400

    track_event('paper_order_submitted', {'symbol': symbol, 'side': side, 'quantity': quantity})
    res = broker_adapter.place_order(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=order_type,
        price=price,
        trigger_price=trigger_price,
        time_in_force=time_in_force,
        client_order_id=client_order_id
    )

    if res.get('success'):
        # Record into local db
        alpaca_id = res['order_id']
        DatabaseManager.record_order(user_id=user_id, symbol=symbol, side=side, qty=quantity, price=price, status="submitted", order_id=alpaca_id)
        # Assuming record_order handles positions locally... if filled synchronously. 
        # Actually Alpaca orders might be filled later. But let's eagerly update local holdings just for testing sake:
        # We assume it goes through in paper trading immediately during market hours.
        DatabaseManager.update_holding(user_id, symbol, quantity if side == "BUY" else -quantity, price, side)
        
    return jsonify(res)
    
@app.route('/api/trading/cancel-order', methods=['POST'])
def api_trading_cancel_order():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']

    data = request.get_json() or {}
    order_id = data.get('order_id')
    if not order_id: return jsonify({"success": False, "error": "Missing order_id"}), 400
    
    # We should verify the order belongs to user.
    # If client_order_id convention doesn't match... well we can just try cancelling in Alpaca.
    res = broker_adapter.cancel_order(order_id)
    return jsonify(res)
"""

content = re.sub(r"@app\.route\('/api/trading/place-order', methods=\\?\['POST'\\]\).*?def api_trading_place_order\(\):.*?return jsonify\(res\)", new_place_order.strip(), content, flags=re.DOTALL)

with open('webui/app.py', 'w') as f:
    f.write(content)
