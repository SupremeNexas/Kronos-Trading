import re

with open('webui/app.py', 'r') as f:
    content = f.read()

new_agent_run = """
@app.route('/api/agent_run', methods=['POST'])
def api_agent_run():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']

    ensure_model_loaded()
    data = request.get_json() or {}
    symbol = data.get('symbol', 'BTCUSD')
    timeframe = data.get('timeframe', '1d')
    allow_trading = data.get('allow_trading', True)
    analysis_id = data.get('analysis_id')

    try:
        from webui.agents_engine.orchestrator import AgentEngineOrchestrator
        orchestrator = AgentEngineOrchestrator(broker=broker_adapter, predictor=predictor)
        result = orchestrator.execute(symbol=symbol, timeframe=timeframe, user_id=user_id)
        
        # Avoid direct trading logic unless handled by orchestrator 
        # (the orchestrator might execute paper trades).
        
        # ... wait, existing api_agent_run returns result.
"""

# Let's cleanly replace the start of api_agent_run to inject user_id and pass it down.
content = re.sub(
    r"@app\.route\('/api/agent_run', methods=\\?\['POST'\\]\).*?def api_agent_run\(\):.*?ensure_model_loaded\(\).*?analysis_id = data\.get\('analysis_id'\).*?try:.*?orchestrator = AgentEngineOrchestrator\(broker=broker_adapter, predictor=predictor\).*?result = orchestrator\.execute\(symbol=symbol, timeframe=timeframe\)",
    r"@app.route('/api/agent_run', methods=['POST'])\ndef api_agent_run():\n    user = get_current_user()\n    if not user: return jsonify({'error': 'Unauthorized'}), 401\n    user_id = user['id']\n    ensure_model_loaded()\n    data = request.get_json() or {}\n    symbol = data.get('symbol', 'BTCUSD')\n    timeframe = data.get('timeframe', '1d')\n    allow_trading = data.get('allow_trading', True)\n    analysis_id = data.get('analysis_id')\n    try:\n        from webui.agents_engine.orchestrator import AgentEngineOrchestrator\n        orchestrator = AgentEngineOrchestrator(broker=broker_adapter, predictor=predictor)\n        result = orchestrator.execute(symbol=symbol, timeframe=timeframe, user_id=user_id)",
    content,
    flags=re.DOTALL
)

with open('webui/app.py', 'w') as f:
    f.write(content)
