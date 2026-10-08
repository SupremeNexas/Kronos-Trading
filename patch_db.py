import re

with open('webui/db.py', 'r') as f:
    content = f.read()

# Fix the broken SQLite schema section
bad_sqlite_block = '''    \'\'\'
    CREATE TABLE IF NOT EXISTS scanner_trades (

    """CREATE TABLE IF NOT EXISTS trade_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        alpaca_order_id TEXT NOT NULL,
        client_order_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        filled_quantity REAL DEFAULT 0.0,
        order_type TEXT NOT NULL,
        limit_price REAL,
        fill_price REAL,
        status TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        filled_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
        user_id TEXT,
        id VARCHAR(255) PRIMARY KEY,
        signal_scan_id VARCHAR(255),
        strategy VARCHAR(100),
        asset VARCHAR(50),
        signal_score INTEGER,
        volume_ratio VARCHAR(50),
        attention_score VARCHAR(50),
        momentum_7d VARCHAR(50),
        decision VARCHAR(50),
        user_action VARCHAR(100),
        alpaca_order_id VARCHAR(255),
        fill_qty FLOAT,
        position_size FLOAT,
        outcome VARCHAR(50),
        timestamp_at TIMESTAMP
    )
    \'\'\''''

good_sqlite_block = '''    """CREATE TABLE IF NOT EXISTS scanner_trades (
        user_id TEXT,
        id VARCHAR(255) PRIMARY KEY,
        signal_scan_id VARCHAR(255),
        strategy VARCHAR(100),
        asset VARCHAR(50),
        signal_score INTEGER,
        volume_ratio VARCHAR(50),
        attention_score VARCHAR(50),
        momentum_7d VARCHAR(50),
        decision VARCHAR(50),
        user_action VARCHAR(100),
        alpaca_order_id VARCHAR(255),
        fill_qty FLOAT,
        position_size FLOAT,
        outcome VARCHAR(50),
        timestamp_at TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS trade_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        alpaca_order_id TEXT NOT NULL,
        client_order_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        filled_quantity REAL DEFAULT 0.0,
        order_type TEXT NOT NULL,
        limit_price REAL,
        fill_price REAL,
        status TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        filled_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tactic_id TEXT,
        tactic_name TEXT,
        reasoning TEXT,
        notes TEXT,
        realized_pnl REAL,
        realized_pnl_pct REAL,
        market_price_at_entry REAL,
        market_price_at_exit REAL
    )""",
    """CREATE TABLE IF NOT EXISTS tactics (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        source TEXT,
        entry_rules TEXT,
        exit_rules TEXT,
        risk_rules TEXT,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""'''

# Fix the broken PostgreSQL schema section (virtually identical mess)
bad_postgres_block = '''    \'\'\'
    CREATE TABLE IF NOT EXISTS scanner_trades (

    """CREATE TABLE IF NOT EXISTS trade_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        alpaca_order_id TEXT NOT NULL,
        client_order_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        filled_quantity REAL DEFAULT 0.0,
        order_type TEXT NOT NULL,
        limit_price REAL,
        fill_price REAL,
        status TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        filled_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
        user_id TEXT,
        id VARCHAR(255) PRIMARY KEY,
        signal_scan_id VARCHAR(255),
        strategy VARCHAR(100),
        asset VARCHAR(50),
        signal_score INTEGER,
        volume_ratio VARCHAR(50),
        attention_score VARCHAR(50),
        momentum_7d VARCHAR(50),
        decision VARCHAR(50),
        user_action VARCHAR(100),
        alpaca_order_id VARCHAR(255),
        fill_qty FLOAT,
        position_size FLOAT,
        outcome VARCHAR(50),
        timestamp_at TIMESTAMP
    )
    \'\'\''''

good_postgres_block = '''    """CREATE TABLE IF NOT EXISTS scanner_trades (
        user_id TEXT,
        id VARCHAR(255) PRIMARY KEY,
        signal_scan_id VARCHAR(255),
        strategy VARCHAR(100),
        asset VARCHAR(50),
        signal_score INTEGER,
        volume_ratio VARCHAR(50),
        attention_score VARCHAR(50),
        momentum_7d VARCHAR(50),
        decision VARCHAR(50),
        user_action VARCHAR(100),
        alpaca_order_id VARCHAR(255),
        fill_qty DOUBLE PRECISION,
        position_size DOUBLE PRECISION,
        outcome VARCHAR(50),
        timestamp_at TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS trade_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        alpaca_order_id TEXT NOT NULL,
        client_order_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        quantity DOUBLE PRECISION NOT NULL,
        filled_quantity DOUBLE PRECISION DEFAULT 0.0,
        order_type TEXT NOT NULL,
        limit_price DOUBLE PRECISION,
        fill_price DOUBLE PRECISION,
        status TEXT NOT NULL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        filled_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tactic_id TEXT,
        tactic_name TEXT,
        reasoning TEXT,
        notes TEXT,
        realized_pnl DOUBLE PRECISION,
        realized_pnl_pct DOUBLE PRECISION,
        market_price_at_entry DOUBLE PRECISION,
        market_price_at_exit DOUBLE PRECISION
    )""",
    """CREATE TABLE IF NOT EXISTS tactics (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        source TEXT,
        entry_rules TEXT,
        exit_rules TEXT,
        risk_rules TEXT,
        active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""'''

content = content.replace(bad_sqlite_block, good_sqlite_block)
content = content.replace(bad_postgres_block, good_postgres_block)

with open('webui/db.py', 'w') as f:
    f.write(content)
print("Schema patched.")
