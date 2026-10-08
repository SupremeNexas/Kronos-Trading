import re
import secrets
import hashlib
import datetime
from typing import Optional, Dict

with open('webui/db.py', 'r') as f:
    text = f.read()

# 1. Add user_sessions table to both DDLs
session_table_ddl = """    \"\"\"CREATE TABLE IF NOT EXISTS user_sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        hashed_token TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )\"\"\""""

if "user_sessions" not in text:
    text = text.replace('    """CREATE TABLE IF NOT EXISTS users (', 
                        session_table_ddl + ',\n    """CREATE TABLE IF NOT EXISTS users (')
                        
# 2. Add user_id to other tables that were missing it
tables_to_add_user_id = [
    "trade_proposals",
    "paper_orders",
    "position_snapshots",
    "portfolio_snapshots",
    "trading_events",
    "daily_trading_journals",
    "scanner_history",
    "scanner_watchlist",
    "scanner_trades"
]

def add_user_id(table_name, content):
    pattern = r'(CREATE TABLE IF NOT EXISTS ' + table_name + r' \(\n)'
    if not re.search(pattern, content):
        pattern = r'(CREATE TABLE IF NOT EXISTS ' + table_name + r' \(\n\s+)'
    
    # Check if user_id is already there
    m = re.search(pattern + r'(user_id)', content)
    if not m:
        content = re.sub(pattern, r'\1        user_id TEXT,\n', content)
    return content

for t in tables_to_add_user_id:
    text = add_user_id(t, text)

# orders and executions don't need it because they relate to portfolio_id / order_id, 
# but the instruction said "At minimum ensure personal ownership for: trade_proposals, paper_orders, orders, executions, trading_events, scanner_trades. Every manual trade must be traceable to the logged-in user."
text = add_user_id("orders", text)
text = add_user_id("executions", text)


# 3. Add session methods
session_methods = """
    @classmethod
    def create_session(cls, user_id: str) -> str:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            raw_token = secrets.token_hex(32)
            hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
            session_id = secrets.token_hex(16)
            
            now = datetime.datetime.utcnow()
            expires_at = now + datetime.timedelta(days=7)
            exp_str = expires_at.strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(_adapt_query(
                "INSERT INTO user_sessions (session_id, user_id, hashed_token, expires_at) VALUES (?, ?, ?, ?)"
            ), (session_id, user_id, hashed_token, exp_str))
            
            conn.commit()
            return f"{session_id}:{raw_token}"
        finally:
            conn.close()

    @classmethod
    def get_user_from_session(cls, session_token: str) -> Optional[Dict]:
        if not session_token or ":" not in session_token:
            return None
        session_id, raw_token = session_token.split(":", 1)
        hashed_token = hashlib.sha256(raw_token.encode()).hexdigest()
        
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query(
                "SELECT user_id, expires_at FROM user_sessions WHERE session_id = ? AND hashed_token = ?"
            ), (session_id, hashed_token))
            row = cursor.fetchone()
            if not row:
                return None
                
            user_id, expires_at = row
            if isinstance(expires_at, str):
                # parse datetime
                try:
                    expires_at = datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    expires_at = datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            
            if expires_at < datetime.datetime.utcnow():
                # expired
                cls.delete_session(session_token)
                return None
                
            return cls.get_user_by_id(user_id)
        finally:
            conn.close()

    @classmethod
    def delete_session(cls, session_token: str):
        if not session_token or ":" not in session_token:
            return
        session_id, _ = session_token.split(":", 1)
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("DELETE FROM user_sessions WHERE session_id = ?"), (session_id,))
            conn.commit()
        finally:
            conn.close()
"""

if "def create_session" not in text:
    text = text.replace("    # User Auth Operations", session_methods + "\n    # User Auth Operations")

with open('webui/db.py', 'w') as f:
    f.write(text)
