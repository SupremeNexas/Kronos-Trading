import sqlite3
import os

db_path = os.path.join('webui', 'data', 'kronos.db')
if not os.path.exists(db_path):
    print("No db")
    exit(0)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check schema for scanner_watchlist
cur.execute("PRAGMA table_info(scanner_watchlist)")
cols = [c[1] for c in cur.fetchall()]
if 'asset' in cols:
    print("Fixing scanner_watchlist PK")
    # dump data
    cur.execute("SELECT * FROM scanner_watchlist")
    rows = cur.fetchall()
    
    cur.execute("DROP TABLE scanner_watchlist")
    # recreate with user_id, asset as composite PK
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scanner_watchlist (
        user_id VARCHAR(255),
        asset VARCHAR(50),
        signal_scan_id VARCHAR(255),
        timestamp_at TIMESTAMP,
        volume_ratio VARCHAR(50),
        attention_score VARCHAR(50),
        momentum_7d VARCHAR(50),
        score INTEGER,
        reasons TEXT,
        PRIMARY KEY(user_id, asset)
    )
    """)
    for r in rows:
        user_id = r[0] if r[0] else 'legacy_unowned'
        try:
            cur.execute("INSERT INTO scanner_watchlist VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]))
        except sqlite3.IntegrityError:
            pass # duplicate user_id, asset
    
    conn.commit()

conn.close()
