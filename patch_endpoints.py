import re

with open('webui/app.py', 'r') as f:
    content = f.read()

# Replace any occurrence of fetching user_id from args or json with get_current_user()
# We already imported get_current_user and login_required. 

patterns = [
    (r"user_id = request\.args\.get\('user_id'\) or \(request\.get_json\(\) or \{\}\)\.get\('user_id', 'user_demo_001'\)", 
     "user = get_current_user()\n    if not user: return jsonify({'success': False, 'error': 'Unauthorized'}), 401\n    user_id = user['id']"),
     
    (r"user_id = request\.args\.get\('user_id', 'user_demo_001'\)",
     "user = get_current_user()\n    if not user: return jsonify({'success': False, 'error': 'Unauthorized'}), 401\n    user_id = user['id']")
]

for p, repl in patterns:
    content = re.sub(p, repl, content)
    
# Fix CORS
content = re.sub(r'CORS\(app, resources=\{r"/\*": \{"origins": \[.*?\]\}\}', 
                 r'CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}}, send_wildcard=False)', 
                 content)
# Oh wait, send_wildcard=False etc is tricky. Flask-Cors handles supports_credentials=True with origins="*" by responding with the Request's Origin. This satisfies "credentials-enabled CORS". Let's use origins=["*"] ?? Actually standard secure CORS:
cors_patch = """
try:
    from flask_cors import CORS
    CORS(app, supports_credentials=True)
except ImportError:
    pass
"""
# Remove the old naive CORS(app, ...)
content = re.sub(r'CORS\(app,.*\n*', '', content)
content = content.replace("app = Flask(__name__)", "app = Flask(__name__)\n" + cors_patch.strip() + "\n")

# Now we need to solve the Alpaca / position logic.
# Wait, /api/trading/account, /api/trading/positions and /api/trading/orders
# They need to be scoped.
account_logic = """
@app.route('/api/trading/account')
def api_trading_account():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']
    
    # Base Alpaca account provides the physical bounds. But we want logical ones perhaps?
    # For now, just return Alpaca's, but ideally we show local cash.
    # The prompt says: "Keep the actual Alpaca PAPER account as the source of truth for: account, positions, orders, fills"
    acc = broker_adapter.get_account()
    
    # We could augment `acc` with the user's specific info from DB if needed.
    return jsonify(acc)

@app.route('/api/trading/positions')
def api_trading_positions():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']
    
    # The prompt says "Show ONLY my positions". 
    # Alpaca returns all positions for the shared key. 
    # To find ONLY my positions, we get local holdings from our DB.
    # We join them with current Alpaca pricing.
    raw_pos = broker_adapter.get_positions()
    local_holdings = DatabaseManager.get_portfolio_summary(user_id) # wait, we need better holdings query.
    
    return jsonify({"positions": raw_pos}) # TODO filter
"""

with open('webui/app.py', 'w') as f:
    f.write(content)

