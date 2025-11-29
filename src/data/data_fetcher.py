import pandas as pd


class DataFetcher:
    """Minimal data utilities used by the test-suite.

    This implementation provides basic technical indicators required by tests:
    - sma_20
    - ema_12
    - macd
    - rsi
    """

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "close" not in out.columns:
            raise ValueError("DataFrame must contain 'close' column")

        out["sma_20"] = out["close"].rolling(window=20, min_periods=1).mean()
        out["ema_12"] = out["close"].ewm(span=12, adjust=False).mean()

        ema_26 = out["close"].ewm(span=26, adjust=False).mean()
        out["macd"] = out["ema_12"] - ema_26

        # RSI (14)
        delta = out["close"].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        # use EMA smoothing for RSI
        roll_up = up.ewm(span=14, adjust=False).mean()
        roll_down = down.ewm(span=14, adjust=False).mean()
        rs = roll_up / (roll_down.replace(0, 1e-8))
        out["rsi"] = 100 - (100 / (1 + rs))

        return out

    def calculate_returns(self, df: pd.DataFrame) -> pd.Series:
        return df["close"].pct_change().fillna(0)
