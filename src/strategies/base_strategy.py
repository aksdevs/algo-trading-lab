"""
Base strategy class for algorithmic trading system.
All trading strategies should inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from enum import Enum


class SignalType(Enum):
    """Enum for different signal types."""

    BUY = 1
    SELL = -1
    HOLD = 0


class PositionType(Enum):
    """Enum for position types."""

    NONE = 0
    LONG = 1
    SHORT = -1


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    """

    def __init__(self, name: str, parameters: Optional[Dict[str, Any]] = None):
        self.name = name
        self.parameters = parameters or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Strategy state
        self.current_position = PositionType.NONE
        self.entry_price = 0.0
        self.entry_date = None
        self.signals = []
        self.trades = []
        self.performance_metrics = {}

        # Data storage
        self.data = pd.DataFrame()
        self.processed_data = pd.DataFrame()

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def validate_data(self, data: pd.DataFrame) -> bool:
        required_columns = ["open", "high", "low", "close", "volume"]

        if not all(col in data.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in data.columns]
            self.logger.error(f"Missing required columns: {missing_cols}")
            return False

        if data.empty:
            self.logger.error("Data is empty")
            return False

        if data.isnull().any().any():
            self.logger.warning("Data contains NaN values")
            data.ffill(inplace=True)

        return True

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if not self.validate_data(data):
            raise ValueError("Invalid input data")

        processed_data = self.calculate_indicators(data.copy())
        self.processed_data = processed_data
        return processed_data

    def run_strategy(self, data: pd.DataFrame) -> pd.DataFrame:
        self.logger.info(f"Running strategy: {self.name}")
        processed_data = self.preprocess_data(data)
        signal_data = self.generate_signals(processed_data)
        self.data = signal_data
        return signal_data

    def get_current_signal(self, data: pd.DataFrame, index: int) -> SignalType:
        if "signal" not in data.columns or index >= len(data):
            return SignalType.HOLD

        signal_value = data.iloc[index]["signal"]

        if signal_value > 0:
            return SignalType.BUY
        elif signal_value < 0:
            return SignalType.SELL
        else:
            return SignalType.HOLD

    # Additional helper methods omitted for brevity in __init__ copy
