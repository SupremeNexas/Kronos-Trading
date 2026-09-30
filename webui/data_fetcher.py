# Data fetcher module for live symbol feeds
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def map_timeframe_binance(timeframe: str) -> str:
    mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d", "1D": "1d"}
    return mapping.get(timeframe, "1h")

def map_timeframe_yahoo(timeframe: str) -> str:
    mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "1d": "1d", "1D": "1d"}
    return mapping.get(timeframe, "1d")

def fetch_binance(symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
    binance_tf = map_timeframe_binance(timeframe)
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": binance_tf, "limit": limit}
    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "count", "taker_buy_volume",
        "taker_buy_quote_volume", "ignore"
    ])
    df["timestamps"] = pd.to_datetime(df["open_time"], unit="ms")
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df[["timestamps", "open", "high", "low", "close", "volume"]]

def fetch_yahoo(symbol: str, timeframe: str) -> pd.DataFrame:
    yahoo_tf = map_timeframe_yahoo(timeframe)
    r_range = "7d" if timeframe == "1m" else "60d" if "m" in timeframe else "365d"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"interval": yahoo_tf, "range": r_range}
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, params=params, headers=headers, timeout=10)
    res.raise_for_status()
    data = res.json().get("chart", {}).get("result", [{}])[0]
    timestamps = pd.to_datetime(data.get("timestamp", []), unit="s")
    indicators = data.get("indicators", {}).get("quote", [{}])[0]
    df = pd.DataFrame({
        "timestamps": timestamps,
        "open": indicators.get("open", []),
        "high": indicators.get("high", []),
        "low": indicators.get("low", []),
        "close": indicators.get("close", []),
        "volume": indicators.get("volume", [])
    }).dropna()
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df

def fetch_symbol_data(symbol: str, timeframe: str) -> pd.DataFrame:
    clean_symbol = symbol.replace("/", "").replace("-", "").upper()

    # Check if CN Stock code (6 digits numeric)
    if clean_symbol.isdigit() and len(clean_symbol) == 6:
        if clean_symbol.startswith(('6', '9')):
            yahoo_symbol = f"{clean_symbol}.SS"
        else:
            yahoo_symbol = f"{clean_symbol}.SZ"
        return fetch_yahoo(yahoo_symbol, timeframe)

    # Check if Crypto
    is_crypto = any(word in clean_symbol for word in ["USDT", "USD", "BTC", "ETH", "BNB", "SOL"]) or symbol.endswith("USD")
    if is_crypto:
        if not clean_symbol.endswith("USDT") and clean_symbol.endswith("USD"):
            clean_symbol = clean_symbol + "T"
        try:
            return fetch_binance(clean_symbol, timeframe)
        except Exception:
            return fetch_yahoo(symbol, timeframe)

    return fetch_yahoo(symbol, timeframe)
