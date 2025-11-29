import pandas as pd
import numpy as np
from src.strategies.sample_strategies import MovingAverageCrossoverStrategy, SimpleRSIStrategy, BuyAndHoldStrategy


def make_price_series(n=100, start_price=50.0):
    rng = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="D")
    rnd = np.random.default_rng(1)
    returns = rnd.normal(loc=0.0004, scale=0.01, size=n)
    prices = start_price * np.cumprod(1 + returns)
    df = pd.DataFrame({
        "open": prices * 0.995,
        "high": prices * 1.01,
        "low": prices * 0.99,
        "close": prices,
        "volume": rnd.integers(100, 1000, size=n),
    }, index=rng)
    return df


def test_moving_average_signals():
    df = make_price_series(50)
    strat = MovingAverageCrossoverStrategy(short_window=3, long_window=7)
    df_ind = strat.calculate_indicators(df)
    out = strat.generate_signals(df_ind)
    assert "signal" in out.columns
    # signals should be integers in {-1,0,1}
    assert set(np.unique(out["signal"])) <= {-1, 0, 1}


def test_simple_rsi_signals():
    df = make_price_series(60)
    strat = SimpleRSIStrategy(rsi_period=7)
    df_ind = strat.calculate_indicators(df)
    out = strat.generate_signals(df_ind)
    assert "signal" in out.columns


def test_buy_and_hold_signal_first():
    df = make_price_series(10)
    strat = BuyAndHoldStrategy()
    df_ind = strat.calculate_indicators(df)
    out = strat.generate_signals(df_ind)
    # first valid index should have signal == 1
    first_idx = out.first_valid_index()
    assert out.loc[first_idx, "signal"] == 1
