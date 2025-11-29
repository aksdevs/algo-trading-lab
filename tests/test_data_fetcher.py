import pandas as pd
import numpy as np
from src.data.data_fetcher import DataFetcher


def make_price_series(n=250, start_price=100.0):
    rng = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="D")
    # generate a random walk
    rnd = np.random.default_rng(42)
    returns = rnd.normal(loc=0.0005, scale=0.02, size=n)
    prices = start_price * np.cumprod(1 + returns)
    df = pd.DataFrame({
        "open": prices * (1 - 0.001),
        "high": prices * (1 + 0.01),
        "low": prices * (1 - 0.01),
        "close": prices,
        "volume": rnd.integers(1000, 10000, size=n),
    }, index=rng)
    return df


def test_add_technical_indicators_creates_columns():
    df = make_price_series()
    fetcher = DataFetcher()
    out = fetcher.add_technical_indicators(df)

    # Check common indicators exist
    assert "sma_20" in out.columns
    assert "ema_12" in out.columns
    assert "macd" in out.columns
    assert "rsi" in out.columns

