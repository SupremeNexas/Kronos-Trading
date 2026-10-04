import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PortfolioDecisionEngine:
    """
    Portfolio Decision Engine (Stage 3)
    Output:
    BUY, HOLD, SELL, WAIT, NO_TRADE
    """
    
    def decide(self, research_data: Dict[str, Any], forecast_data: Dict[str, Any]) -> Dict[str, Any]:
        
        decision = "WAIT"
        
        source_data = research_data.get("source_data", {})
        data_quality = source_data.get("data_quality", "LOW")
        confidence = forecast_data.get("confidence", 0.0)
        direction = forecast_data.get("direction", forecast_data.get("signal", "HOLD"))
        expected_return = forecast_data.get("expected_return_pct", forecast_data.get("return_pct", 0.0))
        
        # Logic to determine BUYS/SELLS
        if data_quality == "LOW" or source_data.get("historical_bars_count", 0) < 50:
            decision = "WAIT"
            opposing = "Data quality is LOW or insufficient historical context."
            missing = "Require fresh live data for historical OHLCV."
        elif direction == "UP" and confidence >= 0.5 and expected_return >= 0.01:
            decision = "BUY"
            opposing = "Potential macro market downturns not factored in without sector context."
            missing = "Detailed valuation and analyst ratings."
        elif direction == "DOWN" and confidence >= 0.5 and expected_return <= -0.01:
            decision = "SELL"
            opposing = "Strong market breadth could overpower individual bearish signals."
            missing = "Detailed sector/concept context."
        else:
            decision = "NO_TRADE"
            opposing = "Forecast confidence is too low or expected return is marginal."
            missing = "Additional predictive confidence."

        supporting = f"KRONOS model forecast {direction} with {round(confidence*100, 1)}% confidence, expected return {round(expected_return*100, 2)}%."
        conditions = "A drop in data freshness or sudden reversal in market regime."
        
        return {
            "decision": decision,
            "supporting_evidence": supporting,
            "opposing_evidence": opposing,
            "missing_information": missing,
            "conditions_that_would_change_decision": conditions,
            "data_quality": data_quality,
            "confidence": confidence
        }
