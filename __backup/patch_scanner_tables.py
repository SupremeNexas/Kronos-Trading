import re

with open("webui/db.py", "r") as f:
    content = f.read()

scanner_tables = """
    '''
    CREATE TABLE IF NOT EXISTS scanner_history (
        signal_scan_id VARCHAR(255) PRIMARY KEY,
        strategy_version VARCHAR(50),
        data_source VARCHAR(255),
        timestamp_at TIMESTAMP,
        asset VARCHAR(50),
        volume_ratio VARCHAR(50),
        attention_score VARCHAR(50),
        momentum_7d VARCHAR(50),
        score INTEGER,
        decision VARCHAR(50),
        reasons TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS scanner_watchlist (
        asset VARCHAR(50) PRIMARY KEY,
        signal_scan_id VARCHAR(255),
        timestamp_at TIMESTAMP,
        volume_ratio VARCHAR(50),
        attention_score VARCHAR(50),
        momentum_7d VARCHAR(50),
        score INTEGER,
        reasons TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS scanner_trades (
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
    '''
"""

if "scanner_history" not in content:
    # Append to BOTH _TABLES_SQL_SQLITE and _TABLES_SQL_POSTGRES
    
    # Locate end of _TABLES_SQL_SQLITE
    idx = content.find("_TABLES_SQL_POSTGRES = [")
    if idx != -1:
        # Find closing bracket of _TABLES_SQL_SQLITE
        close_bracket_sqlite = content.rfind("]", 0, idx)
        if close_bracket_sqlite != -1:
            content = content[:close_bracket_sqlite] + ", " + scanner_tables + "\n]\n" + content[idx:]
    
    # Locate end of _TABLES_SQL_POSTGRES
    idx2 = content.find("class DatabaseManager:")
    if idx2 != -1:
        close_bracket_pg = content.rfind("]", 0, idx2)
        if close_bracket_pg != -1:
            content = content[:close_bracket_pg] + ", " + scanner_tables + "\n]\n" + content[idx2:]
    
    with open("webui/db.py", "w") as f:
        f.write(content)
    print("Database schema patched.")
else:
    print("Already patched.")

