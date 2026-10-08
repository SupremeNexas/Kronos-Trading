import sqlite3
import os

db_path = os.path.join('webui', 'data', 'kronos.db')

def setup_tactics(conn):
    cur = conn.cursor()
    # Create tactics table is already handled by patch_db.py/init_db

    tactics = [
        ("tactic_kronos", "KRONOS FORECAST", "AI forecasting engine using PyTorch model", "webui/model/kronos.py", "Kronos prediction confidence > 80% with positive validation", "Take profit at upper bound, stop loss at lower bound", "Max 5% portfolio risk", 1),
        ("tactic_scanner", "EARLY SIGNAL SCANNER", "Volume and momentum anomaly detection", "webui/strategies/early_signal_scanner.py", "Volume ratio > 2.0 and momentum_7d > 5%", "Trailing stop or momentum reversal", "Standard risk limits", 1),
        ("tactic_manual", "MANUAL", "Discretionary paper trade executed by user", "Manual Entry", "User discretion", "User discretion", "User discretion", 1),
        ("tactic_breakout", "BREAKOUT", "Price breaking through historical resistance", "Technical", "Price > recent high + volume confirming", "Trailing stop loss", "User discretion", 1),
        ("tactic_mean_reversion", "MEAN REVERSION", "Price returning to historical mean after deviation", "Technical", "RSI < 30 or price below lower Bollinger Band", "RSI > 50 or mean hit", "Strict stop at support minus ATR", 1)
    ]

    for t in tactics:
        cur.execute("""
            INSERT OR IGNORE INTO tactics
            (id, name, description, source, entry_rules, exit_rules, risk_rules, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, t)

    conn.commit()

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    setup_tactics(conn)
    conn.close()
    print("Tactics initialized.")
else:
    print("No db found, run init_db first.")
