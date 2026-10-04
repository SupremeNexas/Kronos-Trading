import logging
from typing import Dict, Any
from webui.market_data import InfowayMarketDataProvider
from webui.data_fetcher import fetch_symbol_data

logger = logging.getLogger(__name__)

class KronosResearchLayer:
    """
    Research Layer (Stage 1)
    """
    def __init__(self):
        self.provider = InfowayMarketDataProvider()

    def gather_context(self, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        
        # 1. Real-time price & Historical OHLCV
        # Fallback to yahoo if infoway fails
        data_status = "missing"
        bars = []
        try:
            bars_data = self.provider.get_historical_bars(symbol, timeframe=timeframe, limit=100)
            if bars_data.get("bars"):
                bars = bars_data.get("bars", [])
                data_status = bars_data.get("status", "missing")
        except Exception as e:
            logger.warning(f"Error fetching historical bars from Infoway: {e}")

        # Fallback
        if not bars:
            try:
                df = fetch_symbol_data(symbol, timeframe)
                if not df.empty:
                    bars = df.to_dict('records')
                    data_status = "live_fallback"
            except Exception as e:
                logger.error(f"Fallback Yahoo fetch failed: {e}")

        current_price = bars[-1]["close"] if bars else None
            
        research = {
            "source_data": {
                "symbol": symbol,
                "current_price": current_price,
                "historical_bars_count": len(bars),
                "data_quality": "HIGH" if data_status in ["live", "live_fallback"] else "LOW",
                
                "market_depth": "NOT SUPPLIED",
                "market_breadth": "NOT SUPPLIED",
                "market_temperature": "NOT SUPPLIED",
                "leading_industries": "NOT SUPPLIED",
                "sector_concept_context": "NOT SUPPLIED",
                "company_overview": "NOT SUPPLIED",
                "valuation": "NOT SUPPLIED",
                "analyst_ratings": "NOT SUPPLIED",
                "stock_drivers": "NOT SUPPLIED",
                "global_indexes": "NOT SUPPLIED"
            },
            "kronos_analysis": {
                "trend": "Up" if len(bars) > 1 and bars[-1]["close"] > bars[0]["close"] else "Down",
                "missing_information": "Fundamental and sector metadata not supplied by current Infoway feed."
            }
        }
        
        return research
