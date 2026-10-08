import re

with open('webui/db.py', 'r') as f:
    content = f.read()

if 'import bcrypt' not in content:
    content = content.replace('import hashlib', 'import hashlib\nimport bcrypt\nimport time')

hash_func = """def hash_password(password: str) -> str:
    \"\"\"Secure bcrypt password hashing.\"\"\"
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(stored_password: str, provided_password: str) -> bool:
    \"\"\"Verify password using bcrypt. Fallback to SHA-256 for existing users.\"\"\"
    if stored_password.startswith("$2b$") or stored_password.startswith("$2a$"):
        try:
            return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password.encode("utf-8"))
        except Exception:
            return False
    else:
        # Fallback to old sha256 method
        try:
            if ":" not in stored_password:
                return False
            salt, hashed = stored_password.split(":", 1)
            import hashlib, hmac
            test_hash = hashlib.sha256((provided_password + salt).encode("utf-8")).hexdigest()
            return hmac.compare_digest(hashed, test_hash)
        except Exception:
            return False
"""

content = re.sub(
    r'def hash_password.*?return False', 
    hash_func.strip(), 
    content, 
    flags=re.DOTALL
)

schema_updates = {
    "CREATE TABLE IF NOT EXISTS prediction_runs (": "CREATE TABLE IF NOT EXISTS prediction_runs (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS prediction_outcomes (": "CREATE TABLE IF NOT EXISTS prediction_outcomes (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS trade_proposals (": "CREATE TABLE IF NOT EXISTS trade_proposals (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS paper_orders (": "CREATE TABLE IF NOT EXISTS paper_orders (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS position_snapshots (": "CREATE TABLE IF NOT EXISTS position_snapshots (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS portfolio_snapshots (": "CREATE TABLE IF NOT EXISTS portfolio_snapshots (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS trading_events (": "CREATE TABLE IF NOT EXISTS trading_events (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS model_evaluations (": "CREATE TABLE IF NOT EXISTS model_evaluations (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS daily_trading_journals (": "CREATE TABLE IF NOT EXISTS daily_trading_journals (\n        user_id TEXT,",
    "CREATE TABLE IF NOT EXISTS scanner_history (": "CREATE TABLE IF NOT EXISTS scanner_history (\n        user_id VARCHAR(255),",
    "CREATE TABLE IF NOT EXISTS scanner_trades (": "CREATE TABLE IF NOT EXISTS scanner_trades (\n        user_id VARCHAR(255),"
}

for k, v in schema_updates.items():
    content = content.replace(k, v)

session_schema = (
    '    """CREATE TABLE IF NOT EXISTS user_sessions (\n'
    '        session_token TEXT PRIMARY KEY,\n'
    '        user_id TEXT NOT NULL,\n'
    '        expires_at TIMESTAMP NOT NULL,\n'
    '        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n'
    '    )""",'
)

content = content.replace('    """CREATE TABLE IF NOT EXISTS users (', session_schema + '\n    """CREATE TABLE IF NOT EXISTS users (')

# Add session management to DatabaseManager
session_code = """
    @classmethod
    def create_session(cls, user_id: str) -> str:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            token = secrets.token_hex(32)
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            cursor.execute(_adapt_query("INSERT INTO user_sessions (session_token, user_id, expires_at) VALUES (?, ?, ?)"), 
                           (token, user_id, expires_at))
            conn.commit()
            return token
        finally:
            conn.close()

    @classmethod
    def get_user_from_session(cls, session_token: str) -> Optional[Dict[str, Any]]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            now = datetime.datetime.utcnow()
            cursor.execute(_adapt_query("SELECT user_id, expires_at FROM user_sessions WHERE session_token = ?"), (session_token,))
            row = cursor.fetchone()
            if not row:
                return None
            user_id = row[0]
            expires_at = row[1]
            if isinstance(expires_at, str):
                expires_at = datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S.%f") if "." in expires_at else datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            if expires_at < now:
                cls.delete_session(session_token)
                return None
            return cls.get_user_by_id(user_id)
        finally:
            conn.close()

    @classmethod
    def delete_session(cls, session_token: str):
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("DELETE FROM user_sessions WHERE session_token = ?"), (session_token,))
            conn.commit()
        finally:
            conn.close()
"""
if "def create_session" not in content:
    content = content.replace("    # Watchlist Operations", session_code + "\n\n    # Watchlist Operations")

with open('webui/db.py', 'w') as f:
    f.write(content)
