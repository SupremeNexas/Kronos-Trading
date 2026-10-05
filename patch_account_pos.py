import re

with open("webui/app.py", "r") as f:
    content = f.read()

account_orig = """def api_trading_account():
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
    return jsonify(acc)"""

account_new = """def api_trading_account():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    
    acc = broker_adapter.get_account()
    return jsonify(acc)"""

content = content.replace(account_orig, account_new)

positions_orig = """def api_trading_positions():
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
                
    return jsonify({"positions": my_positions})"""

positions_new = """def api_trading_positions():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    
    raw_pos = broker_adapter.get_positions()
    return jsonify({"positions": raw_pos})"""

content = content.replace(positions_orig, positions_new)

with open("webui/app.py", "w") as f:
    f.write(content)

print("patched")
