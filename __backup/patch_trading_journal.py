import re

with open('webui/agents_engine/trading_journal.py', 'r') as f:
    content = f.read()

# Add user_id to record_prediction parameters
content = re.sub(r'def record_prediction\(self,\s*symbol:\s*str,', 'def record_prediction(self,\\n                          user_id: str = None,\\n                          symbol: str,', content)

# Add user_id to INSERT INTO prediction_runs
insert_old = """INSERT INTO prediction_runs (
                    id, run_id, symbol, timeframe, forecast_horizon,
                    model_name, model_version, forecast_direction, expected_return,
                    predicted_target, lower_bound, upper_bound, confidence,
                    decision, validation_status, risk_status, data_timestamp,
                    supporting_evidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

insert_new = """INSERT INTO prediction_runs (
                    id, user_id, run_id, symbol, timeframe, forecast_horizon,
                    model_name, model_version, forecast_direction, expected_return,
                    predicted_target, lower_bound, upper_bound, confidence,
                    decision, validation_status, risk_status, data_timestamp,
                    supporting_evidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

content = content.replace(insert_old, insert_new)

# Update values tuple for prediction_runs
old_values = """forecast.get("forecast_id", entry_id), run_id, symbol.upper(), "1D", forecast.get("horizon", 14),"""
new_values = """forecast.get("forecast_id", entry_id), user_id, run_id, symbol.upper(), "1D", forecast.get("horizon", 14),"""
content = content.replace(old_values, new_values)

# Also update trade_proposals
prop_old = """INSERT INTO trade_proposals (
                    id, prediction_id, run_id, symbol, side, proposed_quantity,
                    approved_quantity, target_weight, order_type, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
prop_new = """INSERT INTO trade_proposals (
                    id, user_id, prediction_id, run_id, symbol, side, proposed_quantity,
                    approved_quantity, target_weight, order_type, reasoning
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
content = content.replace(prop_old, prop_new)

old_prop_val = """f"prop_{entry_id}", forecast.get("forecast_id", entry_id), run_id, symbol.upper(), side,"""
new_prop_val = """f"prop_{entry_id}", user_id, forecast.get("forecast_id", entry_id), run_id, symbol.upper(), side,"""
content = content.replace(old_prop_val, new_prop_val)

with open('webui/agents_engine/trading_journal.py', 'w') as f:
    f.write(content)
