"""
Simple Trading Strategies

Collection of common algorithmic trading strategies including moving average crossover
and RSI strategies with proper pandas vectorized operations.
"""

import pandas as pd
from .base_strategy import BaseStrategy


class MovingAverageCrossoverStrategy(BaseStrategy):
    def __init__(self, short_window: int = 20, long_window: int = 50, **kwargs):
        parameters = {
            "short_window": short_window,
            "long_window": long_window,
            **kwargs,
        }

        super().__init__("MovingAverageCrossover", parameters)

        self.short_window = short_window
        self.long_window = long_window

        if self.short_window >= self.long_window:
            raise ValueError("Short window must be less than long window")

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()

        df[f"sma_{self.short_window}"] = (
            df["close"].rolling(window=self.short_window).mean()
        )
        df[f"sma_{self.long_window}"] = (
            df["close"].rolling(window=self.long_window).mean()
        )
        df["sma_short"] = df[f"sma_{self.short_window}"]
        df["sma_long"] = df[f"sma_{self.long_window}"]

        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df["signal"] = 0
        df["signal_reason"] = ""

        short_ma_col = f"sma_{self.short_window}"
        long_ma_col = f"sma_{self.long_window}"

        df["position"] = (df[short_ma_col] > df[long_ma_col]).astype(int)
        df["position_change"] = df["position"].diff()

        buy_condition = (
            (df["position_change"] == 1)
            & (~df[short_ma_col].isna())
            & (~df[long_ma_col].isna())
        )
        df.loc[buy_condition, "signal"] = 1
        df.loc[buy_condition, "signal_reason"] = "MA_BULLISH_CROSS"

        sell_condition = (
            (df["position_change"] == -1)
            & (~df[short_ma_col].isna())
            & (~df[long_ma_col].isna())
        )
        df.loc[sell_condition, "signal"] = -1
        df.loc[sell_condition, "signal_reason"] = "MA_BEARISH_CROSS"

        df = df.drop(["position", "position_change"], axis=1)

        return df


class SimpleRSIStrategy(BaseStrategy):
    def __init__(
        self,
        rsi_period: int = 14,
        oversold: float = 30,
        overbought: float = 70,
        **kwargs,
    ):
        parameters = {
            "rsi_period": rsi_period,
            "oversold": oversold,
            "overbought": overbought,
            **kwargs,
        }

        super().__init__("SimpleRSI", parameters)

        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        price_change = df["close"].pct_change(periods=self.rsi_period)
        momentum_std = price_change.rolling(window=self.rsi_period * 2).std()
        normalized_momentum = (price_change / (momentum_std + 1e-10)) * 10 + 50
        df["rsi"] = normalized_momentum.clip(0, 100)
        return df

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df["signal"] = 0
        df["signal_reason"] = ""

        df["rsi_prev"] = df["rsi"].shift(1)

        buy_condition = (
            (df["rsi_prev"] <= self.oversold)
            & (df["rsi"] > self.oversold)
            & (~df["rsi"].isna())
            & (~df["rsi_prev"].isna())
        )
        df.loc[buy_condition, "signal"] = 1
        df.loc[buy_condition, "signal_reason"] = "RSI_OVERSOLD_EXIT"

        sell_condition = (
            (df["rsi_prev"] >= self.overbought)
            & (df["rsi"] < self.overbought)
            & (~df["rsi"].isna())
            & (~df["rsi_prev"].isna())
        )
        df.loc[sell_condition, "signal"] = -1
        df.loc[sell_condition, "signal_reason"] = "RSI_OVERBOUGHT_EXIT"

        df = df.drop(["rsi_prev"], axis=1)

        return df


class BuyAndHoldStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__("BuyAndHold", kwargs)

    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.copy()

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df["signal"] = 0
        df["signal_reason"] = ""

        if len(df) > 0:
            first_valid_idx = df.first_valid_index()
            if first_valid_idx is not None:
                df.loc[first_valid_idx, "signal"] = 1
                df.loc[first_valid_idx, "signal_reason"] = "BUY_AND_HOLD"

        return df
