import re

with open("webui/db.py", "r") as f:
    content = f.read()

# Fix get_db_connection
db_conn_orig = """    if IS_POSTGRES:
        try:
            import psycopg2
            import psycopg2.extras
            conn = psycopg2.connect(DB_URL)
            return conn, "postgres"
        except Exception as e:
            print(f"Warning: Failed to connect to PostgreSQL ({e}), falling back to SQLite.")"""

db_conn_new = """    if IS_POSTGRES:
        try:
            import psycopg2
            import psycopg2.extras
            conn = psycopg2.connect(DB_URL)
            return conn, "postgres"
        except Exception as e:
            import os
            if os.environ.get("FLASK_ENV") == "production" or os.environ.get("RENDER"):
                raise Exception(f"FAIL SAFE: PostgreSQL connection failed in production: {e}")
            print(f"Warning: Failed to connect to PostgreSQL ({e}), falling back to SQLite.")"""

content = content.replace(db_conn_orig, db_conn_new)

# Add trade_history to table creations
trade_history_sql = """
    \"\"\"CREATE TABLE IF NOT EXISTS trade_history (
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
    )\"\"\",
"""

if "trade_history (" not in content:
    # Insert after prediction_outcomes to be safe
    content = content.replace(
        '        lower_bound_hit BOOLEAN\n    )""",',
        '        lower_bound_hit BOOLEAN\n    )""",' + trade_history_sql
    )
    # the sqlite string
    content = content.replace(
        '        lower_bound_hit INTEGER\n    )""",',
        '        lower_bound_hit INTEGER\n    )""",' + trade_history_sql
    )

with open("webui/db.py", "w") as f:
    f.write(content)

print("db patched")
