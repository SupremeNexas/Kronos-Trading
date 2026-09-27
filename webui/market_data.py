import os
import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from webui.data_fetcher import fetch_symbol_data

class MockMarketDataProvider:
    """Generates realistic, deterministic OHLCV historical bars per symbol and timeframe."""

    BASE_PRICES = {
        "AAPL": 185.50,
        "MSFT": 415.20,
        "NVDA": 125.80,
        "AMZN": 178.40,
        "GOOGL": 165.10,
        "TSLA": 220.30,
        "META": 490.50,
        "RELIANCE.NS": 2980.00,
        "HDFCBANK.NS": 1640.00,
        "^NSEI": 24500.00,
        "BTCUSD": 64500.00,
        "ETHUSD": 3450.00,
        "INR=X": 83.90
    }

    TIMEFRAME_FREQS = {
        "1m": ("1min", 300),
        "5m": ("5min", 300),
        "15m": ("15min", 300),
        "30m": ("30min", 300),
        "1h": ("1h", 300),
        "4h": ("4h", 300),
        "1d": ("D", 250),
        "1w": ("W", 120),
        "1M": ("ME", 60)
    }

    def generate_bars(self, symbol: str, timeframe: str = "1d", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        symbol_upper = symbol.upper()
        tf_key = timeframe
        freq, default_limit = self.TIMEFRAME_FREQS.get(tf_key, ("D", 250))
        n_bars = limit or default_limit

        base_price = self.BASE_PRICES.get(symbol_upper, 150.0)

        # Deterministic seed based on symbol name so render is consistent
        seed = sum(ord(c) for c in symbol_upper) * 17 + len(symbol_upper) * 31 + sum(ord(c) for c in tf_key)
        rng = np.random.RandomState(seed)

        volatility = 0.015 if "BTC" in symbol_upper or "ETH" in symbol_upper else 0.009
        if tf_key in ["1m", "5m"]:
            volatility *= 0.35
        elif tf_key in ["1w", "1m"]:
            volatility *= 2.2

        returns = rng.normal(0.0003, volatility, size=n_bars)
        price_path = base_price * np.exp(np.cumsum(returns) - (returns.var() / 2))

        # Generate timestamps ending at current time
        end_time = pd.Timestamp.now().floor('min')
        dates = pd.date_range(end=end_time, periods=n_bars, freq=freq)

        bars = []
        prev_close = price_path[0]

        for i in range(n_bars):
            ts = dates[i]
            gap = rng.normal(0, base_price * 0.0008)
            open_px = prev_close + gap if i > 0 else price_path[i] * 0.998
            close_px = price_path[i]

            # High and Low strictly wrap Open and Close
            high_extra = abs(rng.normal(0, base_price * volatility * 0.8))
            low_extra = abs(rng.normal(0, base_price * volatility * 0.8))

            high_px = max(open_px, close_px) + high_extra
            low_px = min(open_px, close_px) - low_extra
            low_px = max(0.01, low_px)

            volume = int(abs(rng.normal(45000, 15000)) + 2000)
            if "BTC" in symbol_upper:
                volume = float(round(volume / 100, 4))

            prev_close = close_px

            # Standardized timestamp string ISO format
            is_intraday = tf_key in ["1m", "5m", "15m", "30m", "1h", "4h"]
            time_str = ts.strftime('%Y-%m-%d %H:%M:%S') if is_intraday else ts.strftime('%Y-%m-%d')

            bars.append({
                "time": time_str,
                "open": round(float(open_px), 2),
                "high": round(float(high_px), 2),
                "low": round(float(low_px), 2),
                "close": round(float(close_px), 2),
                "volume": volume
            })

        # Ensure bars are sorted strictly ascending by timestamp
        bars.sort(key=lambda b: b["time"])
        return bars

class BaseMarketDataProvider:
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        raise NotImplementedError
    def get_historical_bars(self, symbol: str, timeframe: str = "1d", limit: int = 300) -> Dict[str, Any]:
        raise NotImplementedError
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

class MarketDataProvider(BaseMarketDataProvider):
    """
    Market Data Provider supporting MockMarketDataProvider as default (MARKET_DATA_PROVIDER=mock).
    Supports live symbol feeds when requested.
    """

    POPULAR_SYMBOLS = [
        {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "type": "Stock"},
        {"symbol": "MSFT", "name": "Microsoft Corp.", "exchange": "NASDAQ", "type": "Stock"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "type": "Stock"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "type": "Stock"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "type": "Stock"},
        {"symbol": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "type": "Stock"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "type": "Stock"},
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd", "exchange": "NSE India", "type": "Stock"},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Ltd", "exchange": "NSE India", "type": "Stock"},
        {"symbol": "^NSEI", "name": "NIFTY 50 Index", "exchange": "NSE India", "type": "Index"},
        {"symbol": "BTCUSD", "name": "Bitcoin / US Dollar", "exchange": "Crypto", "type": "Crypto"},
        {"symbol": "ETHUSD", "name": "Ethereum / US Dollar", "exchange": "Crypto", "type": "Crypto"},
        {"symbol": "INR=X", "name": "USD / INR Forex Rate", "exchange": "Forex", "type": "Forex"}
    ]

    def __init__(self, provider_mode: Optional[str] = None):
        self.provider_mode = provider_mode or os.environ.get("MARKET_DATA_PROVIDER", "mock").lower()
        self.mock_generator = MockMarketDataProvider()

    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        if not query:
            return self.POPULAR_SYMBOLS
        q = query.upper()
        results = [s for s in self.POPULAR_SYMBOLS if q in s["symbol"].upper() or q in s["name"].upper()]
        if not results and len(query) >= 1:
            results.append({
                "symbol": q,
                "name": f"{q} Security",
                "exchange": "Global",
                "type": "Equity / Asset"
            })
        return results

    def get_historical_bars(self, symbol: str, timeframe: str = "1d", limit: int = 300) -> Dict[str, Any]:
        """Fetch historical bars using configured provider"""
        data_status = "SIMULATED"
        bars = []

        if self.provider_mode != "mock":
            try:
                df = fetch_symbol_data(symbol, timeframe)
                if not df.empty and len(df) >= 10:
                    data_status = "LIVE" if symbol.endswith(".NS") or "BTC" in symbol or "ETH" in symbol else "DELAYED"
                    if len(df) > limit:
                        df = df.iloc[-limit:]
                    for i, row in df.reset_index().iterrows():
                        ts = row['timestamps']
                        bars.append({
                            'time': ts.strftime('%Y-%m-%d %H:%M:%S') if hasattr(ts, 'strftime') else str(ts),
                            'open': round(float(row['open']), 2),
                            'high': round(float(row['high']), 2),
                            'low': round(float(row['low']), 2),
                            'close': round(float(row['close']), 2),
                            'volume': float(row['volume']) if 'volume' in row else 0.0
                        })
            except Exception as e:
                print(f"Live market data fetch warning for {symbol}: {e}")

        # Fallback to Mock provider
        if not bars:
            data_status = "SIMULATED"
            bars = self.mock_generator.generate_bars(symbol, timeframe, limit=limit)

        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "data_status": data_status,
            "bars": bars
        }

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current quote and daily change for a symbol"""
        bars_resp = self.get_historical_bars(symbol, "1d", limit=2)
        bars = bars_resp.get("bars", [])
        if not bars:
            return {
                "symbol": symbol.upper(),
                "price": 185.50,
                "change": 2.45,
                "change_pct": 1.34,
                "volume": 50000,
                "data_status": "SIMULATED",
                "timestamp": datetime.datetime.now().isoformat()
            }

        last_bar = bars[-1]
        prev_bar = bars[-2] if len(bars) >= 2 else last_bar
        price = last_bar["close"]
        prev_close = prev_bar["close"]
        change = round(price - prev_close, 2)
        change_pct = round((change / (prev_close or 1.0)) * 100, 2)

        return {
            "symbol": symbol.upper(),
            "price": price,
            "open": last_bar["open"],
            "high": last_bar["high"],
            "low": last_bar["low"],
            "close": price,
            "prev_close": prev_close,
            "change": change,
            "change_pct": change_pct,
            "volume": last_bar["volume"],
            "data_status": bars_resp.get("data_status", "SIMULATED"),
            "timestamp": datetime.datetime.now().isoformat()
        }
