import pandas as pd
import pandas as pd
from strategies.base_strategy import Strategy

class SMACrossoverStrategy(Strategy):
    def __init__(self, short_period: int = 20, long_period: int = 50):
        """
        Initialize the SMA Crossover Strategy.
        
        Args:
            short_period (int): Period for the short-term moving average
            long_period (int): Period for the long-term moving average
        """
        super().__init__()
        self.short_period = short_period
        self.long_period = long_period
        
    def generate_signals(self) -> pd.Series:
        """
        Generate trading signals based on SMA crossover.
        Buy when short SMA crosses above long SMA.
        Sell when short SMA crosses below long SMA.
        
        Returns:
            pd.Series: Series of trading signals (1 for buy, -1 for sell, 0 for hold)
        """
        # Calculate SMAs
        self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_period).mean()
        self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_period).mean()
        
        # Initialize signals series
        signals = pd.Series(0, index=self.data.index)
        
        # Generate signals based on crossovers
        for i in range(1, len(self.data)):
            if (self.data['SMA_Short'].iloc[i-1] <= self.data['SMA_Long'].iloc[i-1] and 
                self.data['SMA_Short'].iloc[i] > self.data['SMA_Long'].iloc[i]):
                signals.iloc[i] = 1  # Buy signal
            elif (self.data['SMA_Short'].iloc[i-1] >= self.data['SMA_Long'].iloc[i-1] and 
                  self.data['SMA_Short'].iloc[i] < self.data['SMA_Long'].iloc[i]):
                signals.iloc[i] = -1  # Sell signal
                
        return signals

