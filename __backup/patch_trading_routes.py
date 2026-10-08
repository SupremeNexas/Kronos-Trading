import re

with open('webui/app.py', 'r') as f:
    content = f.read()

# Replace api_trading_positions, orders, account
new_trading = """
@app.route('/api/trading/account')
def api_trading_account():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']
    
    acc = broker_adapter.get_account()
    # Ideally, override cash/equity with user's specific split. 
    user_pf = DatabaseManager.get_portfolio_summary(user_id)
    if acc.get('status') == 'ACTIVE':
        # Overwrite with user's local balance
        acc['cash'] = str(user_pf.get('cash', 0.0))
        acc['buying_power'] = str(user_pf.get('cash', 0.0))
        # Equity we compute from positions
    return jsonify(acc)

@app.route('/api/trading/positions')
def api_trading_positions():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']
    
    raw_pos = broker_adapter.get_positions()
    user_pf = DatabaseManager.get_portfolio_summary(user_id)
    local_pos = user_pf.get('positions', {})
    
    my_positions = []
    total_market_value = 0.0
    for p in raw_pos:
        sym = p.get('symbol')
        if sym in local_pos:
            local_qty = local_pos[sym]['quantity']
            if local_qty > 0:
                p_copy = dict(p)
                # Scale values
                alpaca_qty = float(p.get('qty', 1.0) or 1.0)
                if alpaca_qty == 0: alpaca_qty = 1.0 # avoid div/0
                ratio = local_qty / alpaca_qty
                p_copy['qty'] = str(local_qty)
                p_copy['market_value'] = str(float(p.get('market_value', 0.0)) * ratio)
                p_copy['unrealized_pl'] = str(float(p.get('unrealized_pl', 0.0)) * ratio)
                p_copy['avg_entry_price'] = str(local_pos[sym].get('avg_entry_price', p.get('avg_entry_price', 0)))
                my_positions.append(p_copy)
                total_market_value += float(p_copy['market_value'])
                
    return jsonify({"positions": my_positions})

@app.route('/api/trading/orders')
def api_trading_orders():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']
    
    status = request.args.get('status')
    orders = broker_adapter.get_orders(status=status)
    
    # Filter by user suffix in client_order_id
    # When we place order, we should suffix client_order_id with f"_{user_id}"
    my_orders = [o for o in orders if o.get('client_order_id', '').endswith(f"_{user_id}")]
    return jsonify({"orders": my_orders})

@app.route('/api/trading/executions')
def api_trading_executions():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']
    
    return jsonify({"executions": []}) # Optional, can be derived from DB
"""

content = re.sub(r"@app\.route\('/api/trading/account'\).*?def api_trading_executions\(\):\n.*?return jsonify\([^)]+\)", new_trading.strip(), content, flags=re.DOTALL)

with open('webui/app.py', 'w') as f:
    f.write(content)
