import re
import psycopg2
import sqlite3
import os

# Patch early_signal_scanner.py
with open('webui/strategies/early_signal_scanner.py', 'r') as f:
    content = f.read()

content = content.replace(
    'def get_watchlist(self) -> List[Dict[str, Any]]:',
    'def get_watchlist(self, user_id=None) -> List[Dict[str, Any]]:'
)
content = content.replace(
    'SELECT asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons FROM scanner_watchlist ORDER BY timestamp_at DESC',
    'SELECT asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons FROM scanner_watchlist WHERE user_id = %s ORDER BY timestamp_at DESC'
)
# Fix for sqlite/postgres param passing
content = re.sub(
    r'cursor\.execute\(_adapt_query\("([^"]+WHERE user_id = )%s([^"]+)"\)\)',
    r'cursor.execute(_adapt_query("\1?\2"), (user_id,))',
    content
)

# Insert logic for _update_watchlist
content = content.replace(
    'def _update_watchlist(self, results: List[Dict[str, Any]]):',
    'def _update_watchlist(self, results: List[Dict[str, Any]], user_id=None):'
)

old_sw_insert = 'INSERT INTO scanner_watchlist (asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
new_sw_insert = 'INSERT INTO scanner_watchlist (user_id, asset, signal_scan_id, timestamp_at, volume_ratio, attention_score, momentum_7d, score, reasons) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
content = content.replace(old_sw_insert, new_sw_insert)
content = content.replace(
    '(r["asset"], r["signal_scan_id"], r["timestamp"],',
    '(user_id, r["asset"], r["signal_scan_id"], r["timestamp"],'
)

# Replace the call to _update_watchlist inside scan_assets
content = content.replace(
    'self._update_watchlist(res)',
    'self._update_watchlist(res, user_id=user_id)'
)

with open('webui/strategies/early_signal_scanner.py', 'w') as f:
    f.write(content)

# Patch db.py to add user_id to scanner_watchlist
with open('webui/db.py', 'r') as f:
    db_content = f.read()

db_content = db_content.replace(
    'CREATE TABLE IF NOT EXISTS scanner_watchlist (\n        asset VARCHAR(50) PRIMARY KEY,',
    'CREATE TABLE IF NOT EXISTS scanner_watchlist (\n        user_id VARCHAR(255),\n        asset VARCHAR(50) PRIMARY KEY,'
)
with open('webui/db.py', 'w') as f:
    f.write(db_content)

# Migrate the database to add user_id to scanner_watchlist
DB_URL = os.environ.get("DATABASE_URL", "")
IS_POSTGRES = DB_URL.startswith("postgres://") or DB_URL.startswith("postgresql://")

if IS_POSTGRES:
    conn = psycopg2.connect(DB_URL)
else:
    db_path = os.path.join("webui", "data", "kronos.db")
    conn = sqlite3.connect(db_path)
    
cursor = conn.cursor()
try:
    if IS_POSTGRES:
        cursor.execute("ALTER TABLE scanner_watchlist ADD COLUMN IF NOT EXISTS user_id TEXT")
    else:
        cursor.execute("ALTER TABLE scanner_watchlist ADD COLUMN user_id TEXT")
except Exception as e:
    pass
conn.commit()
conn.close()

