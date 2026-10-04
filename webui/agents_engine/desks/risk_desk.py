import logging
from typing import Dict, Any, List, Optional
from webui.agents_engine.desk_schemas import PortfolioTarget, ValidationState, RiskDecision

logger = logging.getLogger(__name__)

class RiskDesk:
    """
    Checks portfolio exposure, limits, size, max loss.
    """
    def __init__(self, cash_balance: float = 100000.0):
        self.cash_balance = cash_balance

    def evaluate(self, target: PortfolioTarget, validation: ValidationState, current_holdings: Dict[str, float] = None) -> RiskDecision:
        if validation.status in ["FAIL", "INSUFFICIENT_DATA"]:
            return RiskDecision(
                status="BLOCK",
                decision="BLOCK",
                reasons=[f"Validation failed: {validation.status}"],
                limits={"max_weight": 0.2},
                adjusted_quantity=0.0
            )

        current_holdings = current_holdings or {}
        # compute sizing
        holdings_value = 0.0
        if isinstance(current_holdings, dict):
            holdings_value = sum(float(v) for v in current_holdings.values() if isinstance(v, (int, float)))
        elif isinstance(current_holdings, list):
            for h in current_holdings:
                if isinstance(h, dict) and 'market_value' in h:
                    holdings_value += float(h['market_value'])
        portfolio_value = self.cash_balance + holdings_value
        proposed_notional = target.target_weight * portfolio_value
        current_notional = target.current_weight * portfolio_value

        delta_notional = proposed_notional - current_notional

        # Check maximum single position (e.g. 20%)
        if target.target_weight > 0.2 or target.target_weight < -0.2:
            return RiskDecision(
                status="BLOCK",
                decision="BLOCK",
                reasons=["Proposed weight exceeds 20% limit"],
                adjusted_quantity=0.0
            )

        adjusted_quantity = abs(delta_notional) / target.current_price if target.current_price > 0 else 0.0


        if delta_notional > self.cash_balance:
            adjusted_quantity = self.cash_balance / target.current_price
            return RiskDecision(
                status="WARN",
                decision="BUY",
                reasons=["Notional exceeds cash balance; capping at cash available."],
                adjusted_quantity=adjusted_quantity
            )

        return RiskDecision(
            status="ALLOW",
            decision="BUY",
            reasons=["All risk checks passed"],
            adjusted_quantity=adjusted_quantity
        )
