import pytest
import pandas as pd
import numpy as np
from strategies.sma_crossover import SMACrossoverStrategy

def test_sma_crossover_initialization():
    """Test SMA Crossover strategy initialization"""
    # Arrange & Act
    strategy = SMACrossoverStrategy(short_period=20, long_period=50)
    
    # Assert
    assert strategy.short_period == 20
    assert strategy.long_period == 50
    assert len(strategy.positions) == 0

def test_generate_signals(sample_stock_data):
    """Test signal generation logic"""
    # Arrange
    strategy = SMACrossoverStrategy(short_period=20, long_period=50)
    strategy.initialize(sample_stock_data)
    
    # Act
    signals = strategy.generate_signals()
    
    # Assert
    assert isinstance(signals, pd.Series)
    assert len(signals) == len(sample_stock_data)
    assert all(signal in [1, -1, 0] for signal in signals.unique())
    assert 'SMA_Short' in strategy.data.columns
    assert 'SMA_Long' in strategy.data.columns

def test_crossover_signals(sample_stock_data):
    """Test if signals are generated at correct crossover points"""
    # Arrange
    strategy = SMACrossoverStrategy(short_period=20, long_period=50)
    strategy.initialize(sample_stock_data)
    
    # Act
    signals = strategy.generate_signals()
    
    # Assert
    # Find points where short SMA crosses long SMA
    for i in range(1, len(strategy.data)):
        if (strategy.data['SMA_Short'].iloc[i-1] <= strategy.data['SMA_Long'].iloc[i-1] and 
            strategy.data['SMA_Short'].iloc[i] > strategy.data['SMA_Long'].iloc[i]):
            assert signals.iloc[i] == 1  # Should be a buy signal
        elif (strategy.data['SMA_Short'].iloc[i-1] >= strategy.data['SMA_Long'].iloc[i-1] and 
              strategy.data['SMA_Short'].iloc[i] < strategy.data['SMA_Long'].iloc[i]):
            assert signals.iloc[i] == -1  # Should be a sell signal

def test_full_backtest_execution(sample_stock_data):
    """Test full backtest execution with SMA Crossover strategy"""
    # Arrange
    strategy = SMACrossoverStrategy(short_period=20, long_period=50)
    initial_capital = 100000
    
    # Act
    strategy.initialize(sample_stock_data, initial_capital)
    results, metrics = strategy.run_backtest()
    
    # Assert
    assert isinstance(results, pd.DataFrame)
    assert isinstance(metrics, dict)
    assert len(strategy.portfolio_value) == len(sample_stock_data)
    assert all(key in metrics for key in [
        'Total Return (%)',
        'Annual Return (%)',
        'Sharpe Ratio',
        'Max Drawdown (%)',
        'Final Portfolio Value'
    ])