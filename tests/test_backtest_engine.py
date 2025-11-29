import pandas as pd
import numpy as np
from src.backtesting.backtest_engine import BacktestEngine
from src.strategies.sample_strategies import BuyAndHoldStrategy


def make_price_series(n=30, start_price=100.0):
    rng = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="D")
    rnd = np.random.default_rng(2)
    returns = rnd.normal(loc=0.0006, scale=0.01, size=n)
    prices = start_price * np.cumprod(1 + returns)
    df = pd.DataFrame({
        "open": prices * 0.995,
        "high": prices * 1.01,
        "low": prices * 0.99,
        "close": prices,
        "volume": rnd.integers(1000, 5000, size=n),
    }, index=rng)
    return df


def test_backtest_buy_and_hold():
    df = make_price_series(40)
    strat = BuyAndHoldStrategy()
    engine = BacktestEngine(initial_capital=10000, commission=0.0)
    res = engine.run_backtest(strat, df)
    assert "final_capital" in res or "final_capital" in res
    assert res["initial_capital"] == 10000
    # final capital should be non-negative
    assert res["final_capital"] >= 0
