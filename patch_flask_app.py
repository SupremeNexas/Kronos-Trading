import re
with open('webui/app.py', 'r') as f:
    content = f.read()

trading_lab_routes = """
# Trading Lab APIs
@app.route('/api/lab/system-status', methods=['GET'])
def api_lab_system_status():
    from webui.agents_engine.trading_journal import TradingJournal
    journal = TradingJournal()
    entries = journal.get_entries(limit=100)
    
    # Calculate some basic pnl from recent
    realized_pnl = 0
    wins = 0
    losses = 0
    for e in entries:
        if e.get("outcome") == "PROFIT":
            wins += 1
            realized_pnl += e.get("pnl_pct", 0)
        elif e.get("outcome") == "LOSS":
            losses += 1
            realized_pnl += e.get("pnl_pct", 0)

    try:
        broker_positions = broker.get_positions()
    except:
        broker_positions = {}
        
    try:
        broker_balance = broker.get_balance()
    except:
        broker_balance = 100000

    return jsonify({
        "status": {
            "mode": "PAPER_CONFIRM",
            "paper_trading": True,
            "live_locked": True,
            "provider": "Infoway",
            "broker": "Alpaca Simulation",
            "model": "KRONOS-V4",
            "health": "OPERATIONAL"
        },
        "today": {
            "predictions": len(entries),
            "trade_proposals": sum(1 for e in entries if e.get("user_confirmation")),
            "open_positions": len(broker_positions),
            "realized_pnl": realized_pnl,
            "unrealized_pnl": sum(((p.get("current_price",0) - p.get("avg_entry_price",0))/p.get("avg_entry_price",1))*100 for p in broker_positions.values()) if broker_positions else 0,
            "wins": wins,
            "losses": losses
        }
    })

@app.route('/api/lab/predictions', methods=['GET'])
def api_lab_predictions():
    from webui.agents_engine.trading_journal import TradingJournal
    journal = TradingJournal()
    entries = journal.get_entries(limit=100)
    return jsonify({"predictions": entries})
"""

# inject right before `if __name__ == '__main__':`
if "if __name__ == '__main__':" in content:
    content = content.replace("if __name__ == '__main__':", trading_lab_routes + "\nif __name__ == '__main__':")
else:
    # app.py might not have it at the very bottom (it does actually)
    content += "\n" + trading_lab_routes

with open('webui/app.py', 'w') as f:
    f.write(content)
