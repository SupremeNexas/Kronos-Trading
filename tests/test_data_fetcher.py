import pytest
import pandas as pd
from webui.data_fetcher import fetch_symbol_data

def test_fetch_crypto_data():
    df = fetch_symbol_data("BTCUSD", "1h")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    for col in ['timestamps', 'open', 'high', 'low', 'close', 'volume']:
        assert col in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df['timestamps'])

def test_fetch_us_stock_data():
    df = fetch_symbol_data("AAPL", "1d")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'close' in df.columns
