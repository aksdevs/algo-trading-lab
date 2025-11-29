import pandas as pd
from .legacy_base import Strategy

class SMACrossoverStrategy(Strategy):
    def __init__(self, short_period: int = 20, long_period: int = 50):
        super().__init__()
        self.short_period = short_period
        self.long_period = long_period
        
    def generate_signals(self) -> pd.Series:
        self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_period).mean()
        self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_period).mean()
        signals = pd.Series(0, index=self.data.index)
        for i in range(1, len(self.data)):
            if (self.data['SMA_Short'].iloc[i-1] <= self.data['SMA_Long'].iloc[i-1] and 
                self.data['SMA_Short'].iloc[i] > self.data['SMA_Long'].iloc[i]):
                signals.iloc[i] = 1
            elif (self.data['SMA_Short'].iloc[i-1] >= self.data['SMA_Long'].iloc[i-1] and 
                  self.data['SMA_Short'].iloc[i] < self.data['SMA_Long'].iloc[i]):
                signals.iloc[i] = -1
        return signals
