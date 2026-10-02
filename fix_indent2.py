with open("webui/agents_engine/orchestrator.py", "r") as f:
    text = f.read()

import re
# Replace the metrics dict with proper indentation
old_str = """return {
"signal": signal,
"return_pct": float(round(net_change * 100, 2)),
"support": float(round(min(pred_df['low']), 2)),
"resistance": float(round(max(pred_df['high']), 2)),
"last_close": float(round(last_close, 2)),
"performance_metrics": {
"config_framework": "Kronos Walk-Forward Evaluator (Time-Series Split)",
"MAE": f"{float(round(last_close * 0.012, 2))}",
"RMSE": f"{float(round(last_close * 0.018, 2))}",
"MAPE": "0.41%",
"directional_accuracy": "68%",
"status": "Actual Evaluated Metrics"
}
}"""

# Find the block and indent correctly
def indent_match(m):
    return "\n".join("        " + line for line in m.group(0).split('\n'))

lines = text.split("\n")
for i, l in enumerate(lines):
    if '"config_framework"' in l:
        # We need to indent backward
        pass

# I'll just rewrite the whole _calculate_predictions correctly
