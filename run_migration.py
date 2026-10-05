import sqlite3
import os

db_path = os.path.join('webui', 'data', 'kronos.db')

def migrate(conn):
    cur = conn.cursor()
    # Find tables that need user_id added
    tables = [
        "scanner_history",
        "scanner_watchlist",
        "scanner_trades",
        "trade_proposals",
        "paper_orders",
        "orders",
        "executions",
        "trading_events"
    ]

    for table in tables:
        # check if it exists
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if cur.fetchone():
            # Check if user_id column exists
            cur.execute(f"PRAGMA table_info({table})")
            columns = [info[1] for info in cur.fetchall()]
            if 'user_id' not in columns:
                print(f"Adding user_id to {table}")
                cur.execute(f"ALTER TABLE {table} ADD COLUMN user_id TEXT")

                # Mark legacy unowned
                cur.execute(f"UPDATE {table} SET user_id = 'legacy_unowned' WHERE user_id IS NULL")

    # Add user_sessions table if missing
    cur.execute("""CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        hashed_token TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    print("Migration complete.")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    migrate(conn)
    conn.close()
else:
    print("db_path missing")
