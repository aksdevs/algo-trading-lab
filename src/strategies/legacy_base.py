from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class Strategy(ABC):
    def __init__(self):
        self.positions: List[Dict] = []
        self.cash: float = 0
        self.initial_capital: float = 0
        self.data: pd.DataFrame = None
        self.portfolio_value: List[float] = []
        
    def initialize(self, data: pd.DataFrame, initial_capital: float = 100000):
        self.data = data
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.positions = []
        self.portfolio_value = []
        
    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        pass
    
    def calculate_position_size(self, price: float) -> int:
        return int(self.cash * 0.95 / price)
    
    def run_backtest(self) -> Tuple[pd.DataFrame, Dict]:
        signals = self.generate_signals()
        self.data['Signal'] = signals
        for i in range(len(self.data)):
            current_price = self.data.iloc[i]['Close']
            signal = signals.iloc[i]
            if signal == 1 and self.cash > current_price:
                position_size = self.calculate_position_size(current_price)
                if position_size > 0:
                    self.positions.append({
                        'size': position_size,
                        'entry_price': current_price,
                        'entry_date': self.data.iloc[i]['Date']
                    })
                    self.cash -= position_size * current_price
            elif signal == -1 and self.positions:
                for position in self.positions:
                    self.cash += position['size'] * current_price
                self.positions = []
            portfolio_value = self.cash
            for position in self.positions:
                portfolio_value += position['size'] * current_price
            self.portfolio_value.append(portfolio_value)
        self.data['Portfolio_Value'] = self.portfolio_value
        return self.data, self.calculate_metrics()
    
    def calculate_metrics(self) -> Dict:
        returns = pd.Series(self.portfolio_value).pct_change()
        metrics = {
            'Total Return (%)': ((self.portfolio_value[-1] - self.initial_capital) / self.initial_capital) * 100,
            'Annual Return (%)': (((self.portfolio_value[-1] / self.initial_capital) ** (252 / len(self.data))) - 1) * 100,
            'Sharpe Ratio': np.sqrt(252) * (returns.mean() / returns.std()) if returns.std() != 0 else 0,
            'Max Drawdown (%)': ((pd.Series(self.portfolio_value).cummax() - pd.Series(self.portfolio_value)) / 
                               pd.Series(self.portfolio_value).cummax()).max() * 100,
            'Final Portfolio Value': self.portfolio_value[-1]
        }
        return metrics
