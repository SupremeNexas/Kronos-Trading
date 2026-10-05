import re

with open('webui/app.py', 'r') as f:
    content = f.read()

# Replace api_agent_run
old_run = """@app.route('/api/agent_run', methods=['POST'])
def api_agent_run():
    ensure_model_loaded()
    data = request.get_json() or {}
    symbol = data.get('symbol', 'BTCUSD')
    timeframe = data.get('timeframe', '1d')
    allow_trading = data.get('allow_trading', True)
    analysis_id = data.get('analysis_id')

    try:
        from webui.agents_engine.orchestrator import AgentEngineOrchestrator
        orchestrator = AgentEngineOrchestrator(broker=broker, predictor=predictor)
        result = orchestrator.run_cycle(
            symbol=symbol,
            timeframe=timeframe,
            allow_trading=allow_trading,
            analysis_id=analysis_id
        )"""

new_run = """@app.route('/api/agent_run', methods=['POST'])
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
        result = orchestrator.run_cycle(
            symbol=symbol,
            timeframe=timeframe,
            allow_trading=allow_trading,
            analysis_id=analysis_id,
            user_id=user_id
        )"""

content = content.replace(old_run, new_run)

# Also patch /api/forecast endpoint, maybe it uses new_forecast_engine?
old_forecast = """@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    ensure_model_loaded()
    data = request.get_json() or {}"""

new_forecast = """@app.route('/api/forecast', methods=['POST'])
def api_forecast():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    # Right now forecast_engine doesn't write DB, it only reads. But just in case, we require auth.
    user_id = user['id']
    
    ensure_model_loaded()
    data = request.get_json() or {}"""

content = content.replace(old_forecast, new_forecast)

with open('webui/app.py', 'w') as f:
    f.write(content)
