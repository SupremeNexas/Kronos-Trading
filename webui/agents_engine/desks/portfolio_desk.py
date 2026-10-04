import datetime
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from dataclasses import replace
from skfolio.optimization import MeanRisk
from skfolio.prior import EmpiricalPrior
from webui.agents_engine.desk_schemas import ForecastDistribution, InvestmentView, PortfolioTarget
from webui.data_fetcher import fetch_symbol_data

logger = logging.getLogger(__name__)

class PortfolioDesk:
    """
    Uses skfolio for portfolio target optimization.
    Takes Forecast and InvestmentView to produce PortfolioTarget.
    """
    def __init__(self, cash_balance: float = 100000.0, current_positions: Dict[str, float] = None):
        self.cash_balance = cash_balance
        self.current_positions = current_positions or {}

    def get_view(self, forecast: ForecastDistribution) -> InvestmentView:
        if forecast.expected_return_pct > 0.0005:
            sig = "BUY"
        elif forecast.expected_return_pct < -0.0005:
            sig = "SELL"
        else:
            sig = "HOLD"

        return InvestmentView(
            symbol=forecast.symbol,
            forecast_reference=str(forecast.timestamp),
            view_return=forecast.expected_return_pct,
            view_uncertainty=forecast.uncertainty,
            confidence=forecast.confidence,
            signal=sig,
            supporting_evidence=f"Directional Prob: {forecast.directional_prob:.2f}",
            opposing_evidence=f"High uncertainty: {forecast.uncertainty:.2f}" if forecast.uncertainty > 0.05 else ""
        )

    def optimize(self, view: InvestmentView, forecast: ForecastDistribution) -> PortfolioTarget:
        current_weight = 0.0

        if view.signal == "HOLD" or forecast.data_quality != "GOOD":
            return PortfolioTarget(
                symbol=view.symbol,
                target_weight=0.0,
                current_weight=current_weight,
                weight_delta=0.0,
                current_price=forecast.current_price,
                risk_constraints={"reason": "No strong view or insufficient data"}
            )

        try:
            df = fetch_symbol_data(view.symbol, "1d")
            if len(df) < 30:
                raise ValueError("Not enough historical data for optimization")

            asset_returns = df['close'].pct_change().dropna().values
            cash_returns = np.random.normal(0, 1e-4, len(asset_returns))

            X = pd.DataFrame({
                view.symbol: asset_returns,
                "CASH": cash_returns
            })

            class AdjustedPrior(EmpiricalPrior):
                def fit(self_, X_, y=None, **fit_params):
                    super().fit(X_, y, **fit_params)
                    trust = view.confidence
                    adjusted_mu = self_.return_distribution_.mu.copy()
                    adjusted_mu[0] = (adjusted_mu[0] * (1 - trust)) + (view.view_return / 252.0) * trust
                    self_.return_distribution_ = replace(self_.return_distribution_, mu=adjusted_mu)
                    return self_

            prior = AdjustedPrior()
            model = MeanRisk(prior_estimator=prior, min_weights=0.0, max_weights=0.2, l2_coef=0.001)
            model.fit(X)

            weights = model.weights_
            target_weight = float(weights[0])

            if target_weight < 0.02:
                target_weight = 0.0

            return PortfolioTarget(
                symbol=view.symbol,
                target_weight=target_weight,
                current_weight=current_weight,
                weight_delta=target_weight - current_weight,
                current_price=forecast.current_price,
                risk_constraints={"max_weight": 0.2, "confidence_used": view.confidence}
            )

        except Exception as e:
            logger.warning(f"skfolio optimization failed or yielded fallback: {e}")
            target_weight = 0.2 if view.signal == "BUY" else (-0.2 if view.signal == "SELL" else 0.0)
            return PortfolioTarget(
                symbol=view.symbol,
                target_weight=target_weight,
                current_weight=current_weight,
                weight_delta=target_weight - current_weight,
                current_price=forecast.current_price,
                risk_constraints={"max_weight": 0.2, "confidence_used": view.confidence, "fallback": True}
            )
