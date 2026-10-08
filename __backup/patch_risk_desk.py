with open("webui/agents_engine/desks/risk_desk.py", "r") as f:
    text = f.read()

text = text.replace(
    "if target.target_weight > 0.2:",
    "if target.target_weight > 0.2 or target.target_weight < -0.2:"
).replace(
    """        if delta_notional <= 0:
            return RiskDecision(
                status="ALLOW",
                decision="REDUCE_OR_HOLD",
                adjusted_quantity=0.0
            )

        adjusted_quantity = delta_notional / target.current_price if target.current_price > 0 else 0.0""",
    """        adjusted_quantity = abs(delta_notional) / target.current_price if target.current_price > 0 else 0.0
"""
)

with open("webui/agents_engine/desks/risk_desk.py", "w") as f:
    f.write(text)
