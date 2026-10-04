import re

with open('webui/db.py', 'r') as f:
    original = f.read()

sqlite_tables = """
    \"\"\"CREATE TABLE IF NOT EXISTS prediction_runs (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        symbol TEXT NOT NULL,
        timeframe TEXT NOT NULL,
        forecast_horizon INTEGER NOT NULL,
        market_price_at_prediction REAL,
        model_name TEXT,
        model_version TEXT,
        forecast_direction TEXT,
        expected_return REAL,
        predicted_target REAL,
        lower_bound REAL,
        upper_bound REAL,
        forecast_uncertainty REAL,
        confidence REAL,
        market_regime TEXT,
        data_provider TEXT,
        data_timestamp TIMESTAMP,
        data_quality REAL,
        supporting_evidence TEXT,
        opposing_evidence TEXT,
        missing_information TEXT,
        conditions_that_would_change_decision TEXT,
        decision TEXT,
        validation_status TEXT,
        risk_status TEXT
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS prediction_outcomes (
        id TEXT PRIMARY KEY,
        prediction_id TEXT NOT NULL,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        actual_price REAL,
        actual_return REAL,
        absolute_error REAL,
        squared_error REAL,
        direction_correct INTEGER,
        target_hit INTEGER,
        lower_bound_hit INTEGER,
        upper_bound_hit INTEGER,
        forecast_bias REAL,
        prediction_outcome TEXT
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS trade_proposals (
        id TEXT PRIMARY KEY,
        prediction_id TEXT NOT NULL,
        run_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL,
        proposed_quantity REAL NOT NULL,
        approved_quantity REAL,
        target_weight REAL,
        current_weight REAL,
        order_type TEXT,
        limit_price REAL,
        estimated_notional REAL,
        validation_status TEXT,
        risk_status TEXT,
        confirmation_state TEXT,
        reason TEXT,
        model_version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS paper_orders (
        id TEXT PRIMARY KEY,
        trade_id TEXT NOT NULL,
        alpaca_order_id TEXT,
        order_status TEXT,
        actual_fill_price REAL,
        filled_quantity REAL,
        slippage REAL,
        fees REAL,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        filled_at TIMESTAMP
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS position_snapshots (
        id TEXT PRIMARY KEY,
        snapshot_id TEXT NOT NULL,
        symbol TEXT NOT NULL,
        quantity REAL,
        avg_entry_price REAL,
        current_price REAL,
        market_value REAL,
        unrealized_pnl REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS portfolio_snapshots (
        id TEXT PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cash REAL,
        equity REAL,
        buying_power REAL,
        gross_exposure REAL,
        net_exposure REAL,
        daily_pnl REAL,
        unrealized_pnl REAL,
        realized_pnl REAL,
        drawdown REAL,
        turnover REAL
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS trading_events (
        id TEXT PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        run_id TEXT,
        symbol TEXT,
        stage TEXT,
        status TEXT,
        metadata TEXT
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS model_evaluations (
        id TEXT PRIMARY KEY,
        prediction_id TEXT NOT NULL,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        actual_return REAL,
        prediction_error REAL,
        direction_correct INTEGER,
        trade_outcome TEXT
    )\"\"\",
    \"\"\"CREATE TABLE IF NOT EXISTS daily_trading_journals (
        id TEXT PRIMARY KEY,
        trading_day TEXT NOT NULL UNIQUE,
        predictions_count INTEGER,
        trades_count INTEGER,
        open_positions_count INTEGER,
        realized_pnl REAL,
        unrealized_pnl REAL,
        prediction_accuracy REAL,
        biggest_winner TEXT,
        biggest_loser TEXT,
        largest_prediction_error TEXT,
        most_confident_incorrect TEXT,
        most_accurate TEXT,
        kronos_belief TEXT,
        actual_happened TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )\"\"\"
"""

postgres_tables = sqlite_tables.replace("REAL", "DOUBLE PRECISION").replace("INTEGER", "BOOLEAN")

# In webui/db.py:
# _TABLES_SQL_SQLITE = [ ... ]
# _TABLES_SQL_POSTGRES = [ ... ]

# Finding the closing bracket for _TABLES_SQL_SQLITE
match1 = re.search(r'_TABLES_SQL_SQLITE = \[.*?(?=^\])', original, re.MULTILINE | re.DOTALL)
if match1:
    old_sqlite = match1.group(0)
    new_sqlite = old_sqlite + ",\n" + sqlite_tables
    original = original.replace(old_sqlite, new_sqlite)

match2 = re.search(r'_TABLES_SQL_POSTGRES = \[.*?(?=^\])', original, re.MULTILINE | re.DOTALL)
if match2:
    old_pg = match2.group(0)
    new_pg = old_pg + ",\n" + postgres_tables
    original = original.replace(old_pg, new_pg)

with open('webui/db.py', 'w') as f:
    f.write(original)

