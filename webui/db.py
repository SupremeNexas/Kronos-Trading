import os
import sqlite3
import json
import datetime
import uuid
import hashlib
import hmac
import secrets
from typing import Dict, Any, List, Optional, Tuple

DB_URL = os.environ.get("DATABASE_URL", "")
IS_POSTGRES = DB_URL.startswith("postgres://") or DB_URL.startswith("postgresql://")

# Default SQLite database path
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "kronos.db")
os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)

SECRET_KEY = os.environ.get("SECRET_KEY", "kronos-production-secret-key-market-intelligence-2026")


def _ph(name: str = "") -> str:
    """Return parameter placeholder for the active database engine."""
    return "%s" if IS_POSTGRES else "?"


def _adapt_query(sql: str) -> str:
    """Convert SQLite-style ? placeholders to %s when using PostgreSQL."""
    if IS_POSTGRES:
        return sql.replace("?", "%s").replace("INSERT OR REPLACE", "INSERT").replace("INSERT OR IGNORE", "INSERT")
    return sql


def hash_password(password: str) -> str:
    """Secure SHA-256 password hashing with salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify password against stored salt:hash format."""
    try:
        if ":" not in stored_password:
            return False
        salt, hashed = stored_password.split(":", 1)
        test_hash = hashlib.sha256((provided_password + salt).encode("utf-8")).hexdigest()
        return hmac.compare_digest(hashed, test_hash)
    except Exception:
        return False


def get_db_connection():
    """Get database connection (PostgreSQL if DATABASE_URL set, else SQLite)."""
    if IS_POSTGRES:
        try:
            import psycopg2
            import psycopg2.extras
            conn = psycopg2.connect(DB_URL)
            return conn, "postgres"
        except Exception as e:
            print(f"Warning: Failed to connect to PostgreSQL ({e}), falling back to SQLite.")

    conn = sqlite3.connect(SQLITE_DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


# Shared schema DDL — compatible with both SQLite and PostgreSQL
_TABLES_SQL_SQLITE = [
    """CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'investor',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS watchlists (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS watchlist_items (
        id TEXT PRIMARY KEY,
        watchlist_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        name TEXT,
        notes TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(watchlist_id, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        target_price REAL,
        condition TEXT,
        active INTEGER DEFAULT 1,
        triggered INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS portfolios (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        cash_balance REAL DEFAULT 100000.0,
        currency TEXT DEFAULT 'USD',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS holdings (
        id TEXT PRIMARY KEY,
        portfolio_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        quantity REAL NOT NULL,
        avg_entry_price REAL NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(portfolio_id, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        portfolio_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        order_type TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        trigger_price REAL,
        status TEXT DEFAULT 'FILLED',
        time_in_force TEXT DEFAULT 'DAY',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS executions (
        id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        fee REAL DEFAULT 0.0,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS research_reports (
        id TEXT PRIMARY KEY,
        symbol TEXT NOT NULL,
        report_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
]

_TABLES_SQL_POSTGRES = [
    """CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'investor',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS watchlists (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS watchlist_items (
        id TEXT PRIMARY KEY,
        watchlist_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        name TEXT,
        notes TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(watchlist_id, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        alert_type TEXT NOT NULL,
        target_price DOUBLE PRECISION,
        condition TEXT,
        active BOOLEAN DEFAULT TRUE,
        triggered BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS portfolios (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        cash_balance DOUBLE PRECISION DEFAULT 100000.0,
        currency TEXT DEFAULT 'USD',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS holdings (
        id TEXT PRIMARY KEY,
        portfolio_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        quantity DOUBLE PRECISION NOT NULL,
        avg_entry_price DOUBLE PRECISION NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(portfolio_id, symbol)
    )""",
    """CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        portfolio_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        order_type TEXT NOT NULL,
        quantity DOUBLE PRECISION NOT NULL,
        price DOUBLE PRECISION NOT NULL,
        trigger_price DOUBLE PRECISION,
        status TEXT DEFAULT 'FILLED',
        time_in_force TEXT DEFAULT 'DAY',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS executions (
        id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity DOUBLE PRECISION NOT NULL,
        price DOUBLE PRECISION NOT NULL,
        fee DOUBLE PRECISION DEFAULT 0.0,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS research_reports (
        id TEXT PRIMARY KEY,
        symbol TEXT NOT NULL,
        report_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
]


class DatabaseManager:
    """
    Unified database manager handling schema migrations, users,
    watchlists, alerts, portfolio holdings, orders, executions, and research reports.
    Supports both SQLite and PostgreSQL via DATABASE_URL.
    """

    @classmethod
    def init_db(cls):
        """Initialize database tables with schema migrations."""
        conn, db_type = get_db_connection()
        cursor = conn.cursor()

        tables = _TABLES_SQL_POSTGRES if db_type == "postgres" else _TABLES_SQL_SQLITE
        for ddl in tables:
            cursor.execute(ddl)
        conn.commit()

        # Seed default demo user and watchlist if not exist
        cls._seed_demo_data(conn, db_type)
        conn.close()

    @classmethod
    def _seed_demo_data(cls, conn, db_type):
        cursor = conn.cursor()
        demo_email = "demo@kronos.ai"

        cursor.execute(_adapt_query("SELECT id FROM users WHERE email = ?"), (demo_email,))
        row = cursor.fetchone()
        if not row:
            demo_id = "user_demo_001"
            pwd_hash = hash_password("KronosDemo2026!")
            cursor.execute(
                _adapt_query("INSERT INTO users (id, email, password_hash, name, role) VALUES (?, ?, ?, ?, ?)"),
                (demo_id, demo_email, pwd_hash, "Demo Investor", "demo")
            )

            # Create default watchlist
            wl_id = "wl_demo_001"
            cursor.execute(
                _adapt_query("INSERT INTO watchlists (id, user_id, name) VALUES (?, ?, ?)"),
                (wl_id, demo_id, "Tech & Market Leaders")
            )

            # Seed watchlist items
            items = [
                ("AAPL", "Apple Inc."),
                ("NVDA", "NVIDIA Corp."),
                ("MSFT", "Microsoft Corp."),
                ("BTCUSD", "Bitcoin / USD"),
                ("ETHUSD", "Ethereum / USD"),
                ("TSLA", "Tesla Inc."),
                ("AMZN", "Amazon.com Inc."),
                ("^NSEI", "NIFTY 50 Index")
            ]
            for sym, name in items:
                cursor.execute(
                    _adapt_query("INSERT INTO watchlist_items (id, watchlist_id, symbol, name) VALUES (?, ?, ?, ?)"),
                    (str(uuid.uuid4())[:8], wl_id, sym, name)
                )

            # Create default portfolio
            pf_id = "pf_demo_001"
            cursor.execute(
                _adapt_query("INSERT INTO portfolios (id, user_id, name, cash_balance) VALUES (?, ?, ?, ?)"),
                (pf_id, demo_id, "Primary Trading Account", 100000.0)
            )

            # Seed sample holdings
            sample_holdings = [
                ("AAPL", 50, 182.50),
                ("NVDA", 80, 120.40),
                ("BTCUSD", 0.5, 62100.0)
            ]
            for sym, qty, price in sample_holdings:
                cursor.execute(
                    _adapt_query("INSERT INTO holdings (id, portfolio_id, symbol, quantity, avg_entry_price) VALUES (?, ?, ?, ?, ?)"),
                    (str(uuid.uuid4())[:8], pf_id, sym, qty, price)
                )

            # Seed default alerts
            cursor.execute(
                _adapt_query("INSERT INTO alerts (id, user_id, symbol, alert_type, target_price, condition) VALUES (?, ?, ?, ?, ?, ?)"),
                (str(uuid.uuid4())[:8], demo_id, "AAPL", "PRICE_ABOVE", 200.0, "Breakout Target")
            )
            cursor.execute(
                _adapt_query("INSERT INTO alerts (id, user_id, symbol, alert_type, target_price, condition) VALUES (?, ?, ?, ?, ?, ?)"),
                (str(uuid.uuid4())[:8], demo_id, "NVDA", "PRICE_BELOW", 115.0, "Dip Buy Zone")
            )

            conn.commit()

    # User Auth Operations
    @classmethod
    def create_user(cls, email: str, password: str, name: str) -> Dict[str, Any]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("SELECT id FROM users WHERE email = ?"), (email.lower().strip(),))
            if cursor.fetchone():
                return {"success": False, "error": "User with this email already exists"}

            user_id = f"user_{uuid.uuid4().hex[:12]}"
            pwd_hash = hash_password(password)
            cursor.execute(
                _adapt_query("INSERT INTO users (id, email, password_hash, name, role) VALUES (?, ?, ?, ?, ?)"),
                (user_id, email.lower().strip(), pwd_hash, name.strip(), "investor")
            )

            # Initialize portfolio & watchlist for new user
            pf_id = f"pf_{uuid.uuid4().hex[:10]}"
            cursor.execute(
                _adapt_query("INSERT INTO portfolios (id, user_id, name, cash_balance) VALUES (?, ?, ?, ?)"),
                (pf_id, user_id, "Main Portfolio", 100000.0)
            )

            wl_id = f"wl_{uuid.uuid4().hex[:10]}"
            cursor.execute(
                _adapt_query("INSERT INTO watchlists (id, user_id, name) VALUES (?, ?, ?)"),
                (wl_id, user_id, "My Watchlist")
            )
            cursor.execute(
                _adapt_query("INSERT INTO watchlist_items (id, watchlist_id, symbol, name) VALUES (?, ?, ?, ?)"),
                (str(uuid.uuid4())[:8], wl_id, "AAPL", "Apple Inc.")
            )
            cursor.execute(
                _adapt_query("INSERT INTO watchlist_items (id, watchlist_id, symbol, name) VALUES (?, ?, ?, ?)"),
                (str(uuid.uuid4())[:8], wl_id, "NVDA", "NVIDIA Corp.")
            )

            conn.commit()
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email.lower().strip(),
                    "name": name.strip(),
                    "role": "investor"
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @classmethod
    def authenticate_user(cls, email: str, password: str) -> Dict[str, Any]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("SELECT id, email, password_hash, name, role FROM users WHERE email = ?"), (email.lower().strip(),))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": "Invalid email or password"}

            user_id, user_email, pwd_hash, name, role = row[0], row[1], row[2], row[3], row[4]
            if not verify_password(pwd_hash, password):
                return {"success": False, "error": "Invalid email or password"}

            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": user_email,
                    "name": name,
                    "role": role
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("SELECT id, email, name, role, created_at FROM users WHERE id = ?"), (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "email": row[1],
                "name": row[2],
                "role": row[3],
                "created_at": str(row[4])
            }
        finally:
            conn.close()

    # Watchlist Operations
    @classmethod
    def get_watchlists(cls, user_id: str) -> List[Dict[str, Any]]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("SELECT id, name, created_at FROM watchlists WHERE user_id = ? ORDER BY created_at ASC"), (user_id,))
            watchlists = []
            for w_row in cursor.fetchall():
                wl_id, name, created_at = w_row[0], w_row[1], str(w_row[2])
                cursor.execute(
                    _adapt_query("SELECT id, symbol, name, notes, added_at FROM watchlist_items WHERE watchlist_id = ? ORDER BY added_at ASC"),
                    (wl_id,)
                )
                items = [
                    {"id": i[0], "symbol": i[1], "name": i[2], "notes": i[3], "added_at": str(i[4])}
                    for i in cursor.fetchall()
                ]
                watchlists.append({
                    "id": wl_id,
                    "name": name,
                    "created_at": created_at,
                    "items": items
                })
            return watchlists
        finally:
            conn.close()

    @classmethod
    def add_watchlist_item(cls, user_id: str, symbol: str, name: Optional[str] = None) -> Dict[str, Any]:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("SELECT id FROM watchlists WHERE user_id = ? LIMIT 1"), (user_id,))
            row = cursor.fetchone()
            if not row:
                wl_id = f"wl_{uuid.uuid4().hex[:10]}"
                cursor.execute(_adapt_query("INSERT INTO watchlists (id, user_id, name) VALUES (?, ?, ?)"), (wl_id, user_id, "Default Watchlist"))
            else:
                wl_id = row[0]

            item_id = str(uuid.uuid4())[:8]
            if db_type == "postgres":
                cursor.execute(
                    "INSERT INTO watchlist_items (id, watchlist_id, symbol, name) VALUES (%s, %s, %s, %s) ON CONFLICT (watchlist_id, symbol) DO UPDATE SET name = EXCLUDED.name",
                    (item_id, wl_id, symbol.upper(), name or symbol.upper())
                )
            else:
                cursor.execute(
                    "INSERT OR REPLACE INTO watchlist_items (id, watchlist_id, symbol, name) VALUES (?, ?, ?, ?)",
                    (item_id, wl_id, symbol.upper(), name or symbol.upper())
                )
            conn.commit()
            return {"success": True, "item": {"id": item_id, "symbol": symbol.upper(), "name": name or symbol.upper()}}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @classmethod
    def remove_watchlist_item(cls, user_id: str, symbol: str) -> Dict[str, Any]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("""
                DELETE FROM watchlist_items
                WHERE symbol = ? AND watchlist_id IN (SELECT id FROM watchlists WHERE user_id = ?)
            """), (symbol.upper(), user_id))
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # Alerts Operations
    @classmethod
    def get_alerts(cls, user_id: str) -> List[Dict[str, Any]]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("""
                SELECT id, symbol, alert_type, target_price, condition, active, triggered, created_at
                FROM alerts WHERE user_id = ? ORDER BY created_at DESC
            """), (user_id,))
            return [
                {
                    "id": r[0],
                    "symbol": r[1],
                    "alert_type": r[2],
                    "target_price": r[3],
                    "condition": r[4],
                    "active": bool(r[5]),
                    "triggered": bool(r[6]),
                    "created_at": str(r[7])
                }
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    @classmethod
    def create_alert(cls, user_id: str, symbol: str, alert_type: str, target_price: float, condition: str) -> Dict[str, Any]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            alert_id = f"alt_{uuid.uuid4().hex[:8]}"
            cursor.execute(_adapt_query("""
                INSERT INTO alerts (id, user_id, symbol, alert_type, target_price, condition, active, triggered)
                VALUES (?, ?, ?, ?, ?, ?, 1, 0)
            """), (alert_id, user_id, symbol.upper(), alert_type, target_price, condition))
            conn.commit()
            return {
                "success": True,
                "alert": {
                    "id": alert_id,
                    "symbol": symbol.upper(),
                    "alert_type": alert_type,
                    "target_price": target_price,
                    "condition": condition,
                    "active": True
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @classmethod
    def delete_alert(cls, user_id: str, alert_id: str) -> Dict[str, Any]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("DELETE FROM alerts WHERE id = ? AND user_id = ?"), (alert_id, user_id))
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    # Portfolio Operations
    @classmethod
    def get_portfolio_summary(cls, user_id: str) -> Dict[str, Any]:
        conn, _ = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(_adapt_query("SELECT id, cash_balance, currency FROM portfolios WHERE user_id = ? LIMIT 1"), (user_id,))
            pf = cursor.fetchone()
            if not pf:
                # Default fallback portfolio
                return {"cash": 100000.0, "positions": {}, "portfolio_id": "default"}

            pf_id, cash, currency = pf[0], pf[1], pf[2]
            cursor.execute(_adapt_query("SELECT symbol, quantity, avg_entry_price FROM holdings WHERE portfolio_id = ?"), (pf_id,))
            positions = {}
            for h in cursor.fetchall():
                positions[h[0]] = {
                    "symbol": h[0],
                    "quantity": h[1],
                    "avg_price": h[2],
                    "total_cost": round(h[1] * h[2], 2)
                }

            return {
                "portfolio_id": pf_id,
                "cash": cash,
                "currency": currency,
                "positions": positions
            }
        finally:
            conn.close()

    @classmethod
    def update_holding(cls, user_id: str, symbol: str, quantity: float, price: float, side: str) -> bool:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(cls._adapt_query_static("SELECT id FROM portfolios WHERE user_id = ? LIMIT 1"), (user_id,))
            pf = cursor.fetchone()
            if not pf:
                return False
            pf_id = pf[0]

            cursor.execute(cls._adapt_query_static("SELECT quantity, avg_entry_price FROM holdings WHERE portfolio_id = ? AND symbol = ?"), (pf_id, symbol))
            holding = cursor.fetchone()

            if holding:
                current_qty, avg_price = holding[0], holding[1]
                if side.upper() == 'BUY':
                    new_qty = current_qty + quantity
                    new_avg = ((current_qty * avg_price) + (quantity * price)) / new_qty
                    cursor.execute(cls._adapt_query_static("UPDATE holdings SET quantity = ?, avg_entry_price = ?, updated_at = CURRENT_TIMESTAMP WHERE portfolio_id = ? AND symbol = ?"), (new_qty, new_avg, pf_id, symbol))
                else: # SELL
                    new_qty = current_qty - quantity
                    if new_qty <= 0:
                        cursor.execute(cls._adapt_query_static("DELETE FROM holdings WHERE portfolio_id = ? AND symbol = ?"), (pf_id, symbol))
                    else:
                        cursor.execute(cls._adapt_query_static("UPDATE holdings SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE portfolio_id = ? AND symbol = ?"), (new_qty, pf_id, symbol))
            else:
                if side.upper() == 'BUY':
                    h_id = f"h_{uuid.uuid4().hex[:8]}"
                    cursor.execute(
                        cls._adapt_query_static("INSERT INTO holdings (id, portfolio_id, symbol, quantity, avg_entry_price) VALUES (?, ?, ?, ?, ?)"),
                        (h_id, pf_id, symbol, quantity, price)
                    )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating holding: {e}")
            return False
        finally:
            conn.close()

    @classmethod
    def record_order(cls, user_id: str, symbol: str, side: str, qty: float, price: float, status: str, order_id: str = None) -> str:
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(cls._adapt_query_static("SELECT id FROM portfolios WHERE user_id = ? LIMIT 1"), (user_id,))
            pf = cursor.fetchone()
            if not pf:
                return None
            pf_id = pf[0]

            if not order_id:
                order_id = f"ord_{uuid.uuid4().hex[:10]}"

            cursor.execute(
                cls._adapt_query_static("INSERT INTO orders (id, portfolio_id, symbol, side, order_type, quantity, price, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"),
                (order_id, pf_id, symbol, side, "MARKET", qty, price, status)
            )
            
            if status == "FILLED":
                exec_id = f"exec_{uuid.uuid4().hex[:10]}"
                cursor.execute(
                    cls._adapt_query_static("INSERT INTO executions (id, order_id, symbol, side, quantity, price) VALUES (?, ?, ?, ?, ?, ?)"),
                    (exec_id, order_id, symbol, side, qty, price)
                )

            conn.commit()
            return order_id
        except Exception as e:
            print(f"Error recording order: {e}")
            return None
        finally:
            conn.close()

    @classmethod
    def _adapt_query_static(cls, sql: str) -> str:
        if IS_POSTGRES:
            return sql.replace("?", "%s").replace("INSERT OR REPLACE", "INSERT").replace("INSERT OR IGNORE", "INSERT")
        return sql
