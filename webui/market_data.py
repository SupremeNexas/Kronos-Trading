import os
import datetime
import pandas as pd
from typing import Dict, Any, List, Optional
try:
    from infoway import InfowayClient
    INFOWAY_AVAILABLE = True
except ImportError:
    INFOWAY_AVAILABLE = False
import logging

class BaseMarketDataProvider:
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError
    def get_historical_bars(self, symbol: str, timeframe: str = "1d", limit: int = 300) -> Dict[str, Any]:
        raise NotImplementedError
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

class InfowayMarketDataProvider(BaseMarketDataProvider):
    """
    Market Data Provider using genuine Infoway API.
    Handles symbol lookup, real-time price, OHLCV.
    """
    def __init__(self):
        self.api_key = os.environ.get("INFOWAY_API_KEY", "")
        logging.info(f"[DIAGNOSTICS] INFOWAY_API_KEY is present: {bool(self.api_key)}, length: {len(self.api_key)}")
        if INFOWAY_AVAILABLE:
            self.client = InfowayClient(api_key=self.api_key)
        else:
            self.client = None

    def _determine_market_type(self, symbol: str) -> str:
        # Simple heuristic to translate symbol to infoway market type
        upper_sym = symbol.upper()
        if "BTC" in upper_sym or "ETH" in upper_sym or "USDT" in upper_sym:
            return "crypto"
        elif "=" in upper_sym:
            return "common" # Forex
        elif upper_sym.endswith(".NS") or upper_sym.endswith(".BO"):
            return "india"
        elif upper_sym.endswith(".HK"):
            return "stock" # HK handled in stock
        else:
            return "stock"

    def _get_infoway_symbol(self, symbol: str) -> str:
        # Standardize for infoway
        upper_sym = symbol.upper()
        if upper_sym.endswith(".NS"):
            return upper_sym.replace(".NS", ".IN")
        if "BTC" in upper_sym and not "USDT" in upper_sym:
            if upper_sym == "BTCUSD":
                return "BTCUSDT"
        if "ETH" in upper_sym and not "USDT" in upper_sym:
            if upper_sym == "ETHUSD":
                return "ETHUSDT"
        # Convert standard US stocks like AAPL to AAPL.US
        if "." not in upper_sym and "USD" not in upper_sym:
            return f"{upper_sym}.US"
        return upper_sym

    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        if not self.client:
            return [{"symbol": query, "name": query.upper(), "exchange": "US", "type": "Equity"}]
        try:
            # Type must be one of: STOCK_US, STOCK_CN, STOCK_HK, STOCK_JP, STOCK_KS, STOCK_IN, CRYPTO, FOREX, FUTURES
            res = self.client.basic.get_symbols("STOCK_US")
            results = []
            q = query.upper()
            for item in res:
                if q in item.get("symbol", "").upper() or q in item.get("name_en", "").upper():
                    results.append({
                        "symbol": item["symbol"].replace(".US", ""),
                        "name": item.get("name_en") or item.get("name_cn"),
                        "exchange": "US",
                        "type": "Stock"
                    })
                    if len(results) >= 20:
                        break
            return results
        except Exception as e:
            logging.error(f"Infoway search error: {e}")
            return []

    def get_historical_bars(self, symbol: str, timeframe: str = "1d", limit: int = 300) -> Dict[str, Any]:
        market_type = self._determine_market_type(symbol)
        infoway_sym = self._get_infoway_symbol(symbol)
        
        # Infoway interval mapping
        # 1=1min, 2=5min, 3=15min, 4=30min, 5=1hour, 6=2hour, 7=4hour, 8=daily
        tf_map = {
            "1m": 1, "5m": 2, "15m": 3, "30m": 4, 
            "1h": 5, "2h": 6, "4h": 7, "1d": 8
        }
        kline_type = tf_map.get(timeframe, 8)
        
        bars = []
        data_status = "missing"
        
        if self.client:
            try:
                subclient = getattr(self.client, market_type)
                res = subclient.get_kline(codes=infoway_sym, kline_type=kline_type, count=limit)
                
                if res and isinstance(res, list) and len(res) > 0:
                    data_status = "live"
                    # Infoway returns newest first. We need oldest first.
                    candles = res[0].get("respList", [])
                    candles.reverse()
                    
                    for row in candles:
                        bars.append({
                            'time': datetime.datetime.fromtimestamp(int(row['t'])).strftime('%Y-%m-%d %H:%M:%S'),
                            'open': float(row['o']),
                            'high': float(row['h']),
                            'low': float(row['l']),
                            'close': float(row['c']),
                            'volume': float(row.get('v', 0.0))
                        })
            except Exception as e:
                logging.error(f"Infoway get_kline error: {e}")
                data_status = f"error: {str(e)}"
                
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "data_status": data_status,
            "bars": bars
        }

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        market_type = self._determine_market_type(symbol)
        infoway_sym = self._get_infoway_symbol(symbol)
        
        price = 0.0
        change = 0.0
        change_pct = 0.0
        volume = 0.0
        data_status = "missing"
        
        if self.client:
            try:
                subclient = getattr(self.client, market_type)
                trade = subclient.get_trade(infoway_sym)
                
                if trade and len(trade) > 0:
                    data_status = "live"
                    row = trade[0]
                    price = float(row.get('p', 0.0))
                    volume = float(row.get('v', 0.0))
                    
                    # We might need kline to get prev close
                    kline_res = subclient.get_kline(codes=infoway_sym, kline_type=8, count=2)
                    if kline_res and len(kline_res) > 0:
                        candles = kline_res[0].get("respList", [])
                        if len(candles) > 0:
                            current_kline = candles[0]
                            prev_close = float(current_kline.get('o', 0.0))
                            if len(candles) > 1:
                                prev_close = float(candles[1].get('c', 0.0))
                            change = price - prev_close
                            if prev_close > 0:
                                change_pct = (change / prev_close) * 100
                            
            except Exception as e:
                logging.error(f"Infoway get_quote error: {e}")
                
        return {
            "symbol": symbol.upper(),
            "price": price,
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "data_status": data_status,
            "timestamp": datetime.datetime.now().isoformat()
        }


    def get_asset_context(self, symbol: str) -> Dict[str, Any]:
        context = {
            "company_overview": "NOT_AVAILABLE",
            "valuation": "NOT_AVAILABLE",
            "analyst_ratings": "NOT_AVAILABLE",
            "stock_drivers": "NOT_AVAILABLE",
            "sector_industry": "NOT_AVAILABLE",
            "concept_context": "NOT_AVAILABLE"
        }
        if not self.client:
            return context
        infoway_sym = self._get_infoway_symbol(symbol)
        market_type = self._determine_market_type(symbol)
        if market_type == "stock":
            try:
                subclient = getattr(self.client, market_type)
                try:
                    context["company_overview"] = subclient.get_company_overview(infoway_sym) or "NOT_AVAILABLE"
                except: pass
                try:
                    context["valuation"] = subclient.get_stock_valuation(infoway_sym) or "NOT_AVAILABLE"
                except: pass
                try:
                    context["analyst_ratings"] = subclient.get_stock_ratings(infoway_sym) or "NOT_AVAILABLE"
                except: pass
                try:
                    context["stock_drivers"] = subclient.get_stock_drivers(infoway_sym) or "NOT_AVAILABLE"
                except: pass
            except Exception as e:
                logging.error(f"Infoway get_asset_context error: {e}")
        return context

    def get_market_context(self) -> Dict[str, Any]:
        context = {
            "market_breadth": "NOT_AVAILABLE",
            "market_temperature": "NOT_AVAILABLE",
            "leading_industries": "NOT_AVAILABLE",
            "global_indexes": "NOT_AVAILABLE"
        }
        if not self.client:
            return context
        try:
            subclient = getattr(self.client, "stock", None)
            if subclient:
                try: context["market_breadth"] = subclient.get_market_breadth() or "NOT_AVAILABLE"
                except: pass
                try: context["market_temperature"] = subclient.get_market_temperature() or "NOT_AVAILABLE"
                except: pass
                try: context["leading_industries"] = subclient.get_leading_industries() or "NOT_AVAILABLE"
                except: pass
                try: context["global_indexes"] = subclient.get_global_indexes() or "NOT_AVAILABLE"
                except: pass
        except Exception as e:
            logging.error(f"Infoway get_market_context error: {e}")
        return context

class MarketDataProvider(BaseMarketDataProvider):
    """
    KRONOS Default Abstraction over specific providers.
    Uses Infoway if API key is provided, gracefully handling failures.
    """
    def __init__(self, provider_mode: Optional[str] = None):
        self.infoway = InfowayMarketDataProvider()

    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        return self.infoway.search_symbols(query)

    def get_historical_bars(self, symbol: str, timeframe: str = "1d", limit: int = 300) -> Dict[str, Any]:
        return self.infoway.get_historical_bars(symbol, timeframe, limit)

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        return self.infoway.get_quote(symbol)


    def get_asset_context(self, symbol: str) -> Dict[str, Any]:
        return self.infoway.get_asset_context(symbol)
        
    def get_market_context(self) -> Dict[str, Any]:
        return self.infoway.get_market_context()
