import pytest
import pandas as pd
import numpy as np
from strategies.base_strategy import Strategy

class TestStrategy(Strategy):
    """A concrete implementation of Strategy for testing"""
    def __init__(self):
        super().__init__()
        
    def generate_signals(self) -> pd.Series:
        """Generate simple test signals"""
        signals = pd.Series(0, index=self.data.index)
        signals[10:20] = 1  # Buy signals
        signals[30:40] = -1  # Sell signals
        return signals

def test_strategy_initialization(sample_stock_data):
    """Test strategy initialization"""
    # Arrange
    strategy = TestStrategy()
    initial_capital = 100000
    
    # Act
    strategy.initialize(sample_stock_data, initial_capital)
    
    # Assert
    assert strategy.cash == initial_capital
    assert strategy.initial_capital == initial_capital
    assert len(strategy.positions) == 0
    assert isinstance(strategy.data, pd.DataFrame)
    assert len(strategy.portfolio_value) == 0

def test_calculate_position_size():
    """Test position size calculation"""
    # Arrange
    strategy = TestStrategy()
    strategy.cash = 100000
    test_price = 100
    
    # Act
    position_size = strategy.calculate_position_size(test_price)
    
    # Assert
    assert position_size > 0
    assert position_size * test_price <= strategy.cash
    assert isinstance(position_size, int)

def test_run_backtest(sample_stock_data):
    """Test full backtest execution"""
    # Arrange
    strategy = TestStrategy()
    strategy.initialize(sample_stock_data, 100000)
    
    # Act
    results, metrics = strategy.run_backtest()
    
    # Assert
    assert isinstance(results, pd.DataFrame)
    assert isinstance(metrics, dict)
    assert 'Total Return (%)' in metrics
    assert 'Sharpe Ratio' in metrics
    assert 'Max Drawdown (%)' in metrics
    assert len(strategy.portfolio_value) == len(sample_stock_data)

def test_calculate_metrics(sample_stock_data):
    """Test performance metrics calculation"""
    # Arrange
    strategy = TestStrategy()
    strategy.initialize(sample_stock_data, 100000)
    strategy.run_backtest()
    
    # Act
    metrics = strategy.calculate_metrics()
    
    # Assert
    assert isinstance(metrics, dict)
    assert all(key in metrics for key in [
        'Total Return (%)',
        'Annual Return (%)',
        'Sharpe Ratio',
        'Max Drawdown (%)',
        'Final Portfolio Value'
    ])
    assert all(isinstance(value, (int, float)) for value in metrics.values())