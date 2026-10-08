
import json

with open('webui/app.py', 'r') as f:
    content = f.read()

tactics_endpoints = '''
# ==================== TACTICS & ATTRIBUTION API ====================
@app.route('/api/tactics', methods=['GET'])
@login_required
def api_tactics_list():
    try:
        from webui.db import get_db_connection, _adapt_query
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(_adapt_query("SELECT id, name, description, source, entry_rules, exit_rules, risk_rules, active FROM tactics ORDER BY name ASC"))
        tactics = []
        for r in cursor.fetchall():
            tactics.append({
                "id": r[0], "name": r[1], "description": r[2], "source": r[3],
                "entry_rules": r[4], "exit_rules": r[5], "risk_rules": r[6], "active": bool(r[7])
            })
        conn.close()
        return jsonify({"success": True, "tactics": tactics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tactics/performance', methods=['GET'])
@login_required
def api_tactics_performance():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']

    try:
        from webui.db import get_db_connection, _adapt_query
        conn, _ = get_db_connection()
        cursor = conn.cursor()

        # Calculate performance per tactic based on realized PnL
        sql = """
            SELECT
                tactic_id,
                tactic_name,
                COUNT(id) as total_trades,
                SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(realized_pnl) as total_pnl,
                AVG(realized_pnl) as avg_pnl
            FROM trade_history
            WHERE user_id = ? AND status IN ('FILLED', 'CLOSED') AND tactic_id IS NOT NULL
            GROUP BY tactic_id, tactic_name
        """
        cursor.execute(_adapt_query(sql), (user_id,))

        performance = []
        for r in cursor.fetchall():
            total = r[2] or 0
            win_rate = (r[3] / total * 100) if total > 0 else 0
            performance.append({
                "tactic_id": r[0],
                "tactic_name": r[1],
                "total_trades": total,
                "winning_trades": r[3] or 0,
                "losing_trades": r[4] or 0,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(r[5] or 0, 2),
                "avg_pnl": round(r[6] or 0, 2)
            })

        conn.close()
        return jsonify({"success": True, "performance": performance})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/trading/history', methods=['GET'])
@login_required
def api_trading_history():
    user = get_current_user()
    if not user: return jsonify({"error": "Unauthorized"}), 401
    user_id = user['id']

    try:
        from webui.db import get_db_connection, _adapt_query
        conn, _ = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(_adapt_query("""
            SELECT id, alpaca_order_id, symbol, side, quantity, filled_quantity,
                   order_type, fill_price, limit_price, status, submitted_at, filled_at,
                   tactic_id, tactic_name, reasoning, notes, realized_pnl, realized_pnl_pct
            FROM trade_history
            WHERE user_id = ?
            ORDER BY submitted_at DESC
        """), (user_id,))

        trades = []
        for r in cursor.fetchall():
            trades.append({
                "trade_id": r[0],
                "alpaca_order_id": r[1],
                "symbol": r[2],
                "side": r[3],
                "quantity": float(r[4] or 0),
                "filled_quantity": float(r[5] or 0),
                "order_type": r[6],
                "fill_price": float(r[7] or 0),
                "limit_price": float(r[8] or 0),
                "status": r[9],
                "submitted_at": r[10],
                "filled_at": r[11],
                "tactic_id": r[12],
                "tactic_name": r[13],
                "reasoning": r[14],
                "notes": r[15],
                "realized_pnl": float(r[16] or 0) if r[16] is not None else None,
                "realized_pnl_pct": float(r[17] or 0) if r[17] is not None else None,
            })

        conn.close()
        return jsonify({"success": True, "trades": trades})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
'''

if '# ==================== TACTICS & ATTRIBUTION API ====================' not in content:
    idx = content.find('# ==================== AI MARKET FORECASTING API ====================')
    content = content[:idx] + tactics_endpoints + content[idx:]
    with open('webui/app.py', 'w') as f:
        f.write(content)
    print("Added tactics endpoints.")
else:
    print("Already added.")
