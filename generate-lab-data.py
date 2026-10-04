import sys
import os
import uuid
import datetime
import random

sys.path.append('/Users/supryo/Desktop/Kronos-master')
from webui.db import get_db_connection, _adapt_query

SYMBOLS = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"]
MODELS = ["KRONOS-V4", "KRONOS-V4-LIGHT"]
DECISIONS = ["BUY", "SELL", "HOLD"]

def generate_mock_data():
    conn, _ = get_db_connection()
    cursor = conn.cursor()

    try:
        # Create some prediction runs and outcomes
        for i in range(25):
            run_id = f"run_{uuid.uuid4().hex[:12]}"
            pred_id = f"pred_{uuid.uuid4().hex[:12]}"
            
            sym = random.choice(SYMBOLS)
            decision = random.choice(DECISIONS)
            
            market_price = random.uniform(100, 500)
            expected_ret = random.uniform(-5.0, 5.0)
            
            ts = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
            
            cursor.execute(_adapt_query("""
                INSERT INTO prediction_runs (
                    id, run_id, timestamp, symbol, timeframe, forecast_horizon,
                    market_price_at_prediction, model_name, forecast_direction,
                    expected_return, predicted_target, confidence, decision,
                    validation_status, risk_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), (
                pred_id, run_id, ts.isoformat(), sym, "1D", 14,
                market_price, random.choice(MODELS), "BULLISH" if expected_ret > 0 else "BEARISH",
                expected_ret, market_price * (1 + expected_ret/100),
                random.uniform(0.5, 0.95), decision,
                "PASS", "ALLOW" if decision != "HOLD" else "BLOCK"
            ))

            # Only 80% have outcomes
            if random.random() > 0.2:
                actual_ret = expected_ret + random.uniform(-2, 2)
                actual_price = market_price * (1 + actual_ret/100)
                outcome = "PROFIT" if (decision == "BUY" and actual_ret > 0) or (decision == "SELL" and actual_ret < 0) else "LOSS"
                
                cursor.execute(_adapt_query("""
                    INSERT INTO prediction_outcomes (
                        id, prediction_id, evaluated_at, actual_price, actual_return,
                        direction_correct, prediction_outcome
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """), (
                    str(uuid.uuid4()), pred_id, (ts + datetime.timedelta(days=14)).isoformat(),
                    actual_price, actual_ret, 1 if (expected_ret > 0 and actual_ret > 0) or (expected_ret < 0 and actual_ret < 0) else 0,
                    outcome
                ))

            # Trades
            if decision != "HOLD":
                trade_id = str(uuid.uuid4())
                cursor.execute(_adapt_query("""
                    INSERT INTO trade_proposals (
                        id, prediction_id, run_id, symbol, side, proposed_quantity,
                        confirmation_state, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """), (
                    trade_id, pred_id, run_id, sym, decision, random.uniform(5, 50),
                    "CONFIRMED", ts.isoformat()
                ))
                
                cursor.execute(_adapt_query("""
                    INSERT INTO paper_orders (
                        id, trade_id, alpaca_order_id, order_status, actual_fill_price, submitted_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """), (
                    str(uuid.uuid4()), trade_id, f"alp_{uuid.uuid4().hex[:8]}", "FILLED",
                    market_price + random.uniform(-0.1, 0.1), (ts + datetime.timedelta(minutes=1)).isoformat()
                ))

        conn.commit()
        print("Mock trading lab data generated successfully.")
    except Exception as e:
        print(f"Failed to generate mock data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    generate_mock_data()
