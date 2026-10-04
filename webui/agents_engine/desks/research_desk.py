import datetime
import logging
from typing import Optional
import pandas as pd
from webui.agents_engine.desk_schemas import MarketSnapshot
from webui.data_fetcher import fetch_symbol_data

logger = logging.getLogger(__name__)

class ResearchDesk:
    """
    Responsible for fetching market data and producing a typed MarketSnapshot.
    """

    def __init__(self):
        self.provider_name = "INFOWAY"

    def get_snapshot(self, symbol: str, timeframe: str = "1d") -> MarketSnapshot:
        try:
            df = fetch_symbol_data(symbol, timeframe)
            if df.empty:
                return MarketSnapshot(
                    symbol=symbol,
                    provider=self.provider_name,
                    timestamp=datetime.datetime.now(),
                    interval=timeframe,
                    current_price=0.0,
                    data_quality="INSUFFICIENT",
                    errors=["No data received from market data provider"]
                )

            current_price = float(df['close'].iloc[-1])
            data_time = df.index[-1] if isinstance(df.index, pd.DatetimeIndex) else datetime.datetime.now()

            # Additional features could be extracted here
            return MarketSnapshot(
                symbol=symbol,
                provider=self.provider_name,
                timestamp=datetime.datetime.now(),
                interval=timeframe,
                current_price=current_price,
                features={"last_close": current_price, "volume": float(df['volume'].iloc[-1])},
                data_quality="GOOD" if current_price > 0 else "STALE",
                source_timestamp=data_time if isinstance(data_time, datetime.datetime) else datetime.datetime.now()
            )
        except Exception as e:
            logger.error(f"ResearchDesk error for {symbol}: {e}")
            return MarketSnapshot(
                symbol=symbol,
                provider=self.provider_name,
                timestamp=datetime.datetime.now(),
                interval=timeframe,
                current_price=0.0,
                data_quality="INSUFFICIENT",
                errors=[str(e)]
            )
