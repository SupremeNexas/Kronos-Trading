import sqlite3
import os
import psycopg2

DB_URL = os.environ.get("DATABASE_URL", "")
IS_POSTGRES = DB_URL.startswith("postgres://") or DB_URL.startswith("postgresql://")

def run_migration():
    if IS_POSTGRES:
        conn = psycopg2.connect(DB_URL)
    else:
        db_path = os.path.join("webui", "data", "kronos.db")
        if not os.path.exists(db_path):
            print("DB not found, no migration needed.")
            return
        conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    
    # Create user_sessions
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_sessions (
            session_token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    except Exception as e:
        print("user_sessions:", e)
        
    tables_to_patch = [
        "prediction_runs", "prediction_outcomes", "trade_proposals", "paper_orders",
        "position_snapshots", "portfolio_snapshots", "trading_events", "model_evaluations",
        "daily_trading_journals", "scanner_history", "scanner_trades"
    ]
    
    for table in tables_to_patch:
        # Check if table exists
        try:
            if IS_POSTGRES:
                cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = %s", (table,))
                exists = cursor.fetchone() is not None
            else:
                cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
                exists = cursor.fetchone() is not None
                
            if exists:
                # Add user_id column
                # In sqlite we can't easily check columns, just try ALTER and catch exception
                if IS_POSTGRES:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS user_id TEXT")
                else:
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id TEXT")
                    except sqlite3.OperationalError as e:
                        if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                            print(f"{table}: {e}")
        except Exception as e:
            print(f"Error checking {table}: {e}")
            
    conn.commit()
    conn.close()
    print("Migration complete!")

run_migration()
