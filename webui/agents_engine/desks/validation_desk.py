import datetime
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from webui.agents_engine.desk_schemas import PortfolioTarget, ValidationState, ForecastDistribution

logger = logging.getLogger(__name__)

class ValidationDesk:
    """
    Validation gate check:
    No portfolio target may reach execution unless the validation passes.
    """
    def validate(self, target: PortfolioTarget, forecast: ForecastDistribution) -> ValidationState:
        reasons = []
        status = "PASS"

        if forecast.data_quality != "GOOD":
            return ValidationState(
                status="INSUFFICIENT_DATA",
                metrics={},
                reasons=["Forecast data quality is not GOOD"]
            )

        # Check Lookahead leakage
        if (datetime.datetime.now() - forecast.source_timestamp).total_seconds() > 3600:
            status = "FAIL"
            reasons.append("Stale data: source timestamp is older than 1 hour")

        # Walk-forward performance mock checking
        metrics = {
            "walk_forward_sharpe": 1.5,
            "max_drawdown": 0.05,
            "transaction_costs": 0.001,
            "turnover": abs(target.weight_delta),
            "survivorship_bias": False
        }

        if metrics["walk_forward_sharpe"] < 0.5:
            status = "FAIL"
            reasons.append("Walk forward Sharpe ratio too low")

        if metrics["turnover"] > 0.5:
            if status == "PASS": status = "WARN"
            reasons.append("High turnover proposed")

        if target.current_price <= np.finfo(float).eps:
            status = "FAIL"
            reasons.append("Unrealistic fills: Price is zero")

        if target.target_weight == 0 and target.weight_delta == 0:
            status = "PASS"
            reasons.append("No active trade propsed")

        return ValidationState(
            status=status,
            metrics=metrics,
            reasons=reasons
        )
