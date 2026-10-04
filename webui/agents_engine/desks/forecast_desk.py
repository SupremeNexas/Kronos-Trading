import numpy as np
import pandas as pd
import datetime
import logging
from typing import Dict, Any, List, Optional
from webui.agents_engine.desk_schemas import ForecastDistribution, MarketSnapshot
from webui.data_fetcher import fetch_symbol_data

logger = logging.getLogger(__name__)

class ForecastDesk:
    """
    Kronos forecasting layer. Returns uncertainty-aware ForecastDistribution.
    """
    def __init__(self, predictor=None):
        self.predictor = predictor

    def forecast(self, symbol: str, timeframe: str, snapshot: MarketSnapshot, pred_len: int = 14) -> ForecastDistribution:
        if snapshot.data_quality != "GOOD" or snapshot.current_price <= 0:
            return ForecastDistribution(
                symbol=symbol,
                forecast_model="KRONOS",
                forecast_version="1.0",
                timestamp=datetime.datetime.now(),
                current_price=snapshot.current_price,
                horizon=pred_len,
                expected_return_pct=0.0,
                median_return_pct=0.0,
                lower_range=0.0,
                upper_range=0.0,
                uncertainty=1.0,
                confidence=0.0,
                source_timestamp=datetime.datetime.now(),
                data_quality="INSUFFICIENT",
                missing_data_indicators=["No valid current price"]
            )

        try:
            df = fetch_symbol_data(symbol, timeframe)
            # Probabilistic forecasting: create multiple paths if possible.
            # Here we wrap the current AI predicting logic or mock with paths.
            paths = []
            num_paths = 100

            if self.predictor:
                # Assuming the real predictor can produce deterministic output, we'll
                # sample around it based on historical volatility if real path generation isn't supported.
                base_pred = self.predictor.predict(df)
            else:
                base_pred = np.random.normal(snapshot.current_price, snapshot.current_price * 0.01, pred_len)

            # Generate monte carlo paths based on standard deviation of the last 30 days
            if len(df) > 30:
                hist_vol = df['close'].pct_change().std()
            else:
                hist_vol = 0.02

            last_px = snapshot.current_price
            target_px_base = float(base_pred[-1])
            base_ret = (target_px_base - last_px) / last_px

            final_prices = []
            for _ in range(num_paths):
                # Random walk around the base prediction drift
                path = [last_px]
                for i in range(pred_len):
                    step_drift = base_ret / pred_len
                    shock = np.random.normal(0, hist_vol)
                    next_px = path[-1] * (1 + step_drift + shock)
                    path.append(next_px)
                paths.append(path[1:])
                final_prices.append(path[-1])

            expected_px = float(np.mean(final_prices))
            median_px = float(np.median(final_prices))
            lower_px = float(np.percentile(final_prices, 5))
            upper_px = float(np.percentile(final_prices, 95))

            sigma = float(np.std(final_prices) / last_px)
            confidence = max(0.0, min(1.0, 1.0 - (sigma * 2)))

            expected_return = (expected_px - last_px) / last_px
            median_return = (median_px - last_px) / last_px

            up_paths = sum(1 for p in final_prices if p > last_px)
            directional_prob = up_paths / num_paths

            return ForecastDistribution(
                symbol=symbol,
                forecast_model="KRONOS" if self.predictor else "MOCK_PATHS",
                forecast_version="1.1",
                timestamp=datetime.datetime.now(),
                current_price=last_px,
                horizon=pred_len,
                expected_return_pct=expected_return,
                median_return_pct=median_return,
                forecast_paths=paths[:10], # store a sample of paths
                lower_range=lower_px,
                upper_range=upper_px,
                uncertainty=sigma,
                confidence=confidence,
                directional_prob=directional_prob,
                source_timestamp=datetime.datetime.now()
            )
        except Exception as e:
            logger.error(f"Forecast error for {symbol}: {e}")
            return ForecastDistribution(
                symbol=symbol,
                forecast_model="ERROR",
                forecast_version="1.0",
                timestamp=datetime.datetime.now(),
                current_price=snapshot.current_price,
                horizon=pred_len,
                expected_return_pct=0.0,
                median_return_pct=0.0,
                lower_range=0.0,
                upper_range=0.0,
                uncertainty=1.0,
                confidence=0.0,
                source_timestamp=datetime.datetime.now(),
                data_quality="INSUFFICIENT",
                missing_data_indicators=[f"Forecast exception: {e}"]
            )
