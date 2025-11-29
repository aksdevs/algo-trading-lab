import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@pytest.fixture
def sample_stock_data():
    """
    Create a sample DataFrame that mimics stock market data.
    """
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)  # For reproducibility
    
    # Generate sample price data
    closes = np.random.randn(len(dates)).cumsum() + 100
    opens = closes + np.random.randn(len(dates)) * 0.1
    highs = np.maximum(opens, closes) + np.random.rand(len(dates)) * 0.5
    lows = np.minimum(opens, closes) - np.random.rand(len(dates)) * 0.5
    volumes = np.random.randint(1000000, 10000000, size=len(dates), dtype=np.int64)
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    })
    
    return df

@pytest.fixture
def mock_yf_ticker():
    """
    Create a mock yfinance Ticker object for testing.
    """
    class MockTicker:
        def __init__(self, sample_data):
            self.sample_data = sample_data
            
        def history(self, start=None, end=None, period=None, interval=None):
            return self.sample_data.set_index('Date')
    
    return MockTicker