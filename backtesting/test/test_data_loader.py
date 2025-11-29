import pytest
import pandas as pd
from datetime import datetime
from src.data_loader import DataLoader
import os

def test_fetch_data_success(mock_yf_ticker, sample_stock_data, mocker):
    """Test successful data fetching"""
    # Arrange
    symbol = "AAPL"
    mock_ticker_instance = mock_yf_ticker(sample_stock_data)
    mocker.patch('yfinance.Ticker', return_value=mock_ticker_instance)
    data_loader = DataLoader()
    
    # Act
    result = data_loader.fetch_data(symbol)
    
    # Assert
    assert isinstance(result, pd.DataFrame)
    assert all(col in result.columns for col in ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    assert len(result) > 0

def test_fetch_data_with_dates(mock_yf_ticker, sample_stock_data, mocker):
    """Test data fetching with specific date range"""
    # Arrange
    symbol = "AAPL"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    mock_ticker_instance = mock_yf_ticker(sample_stock_data)
    mocker.patch('yfinance.Ticker', return_value=mock_ticker_instance)
    data_loader = DataLoader()
    
    # Act
    result = data_loader.fetch_data(symbol, start_date=start_date, end_date=end_date)
    
    # Assert
    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]['Date'].strftime('%Y-%m-%d') >= start_date
    assert result.iloc[-1]['Date'].strftime('%Y-%m-%d') <= end_date

def test_fetch_data_invalid_symbol(mocker):
    """Test behavior with invalid stock symbol"""
    # Arrange
    symbol = "INVALID"
    mocker.patch('yfinance.Ticker', side_effect=Exception("Invalid symbol"))
    data_loader = DataLoader()
    
    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        data_loader.fetch_data(symbol)
    assert "Error fetching data for INVALID" in str(exc_info.value)

def test_save_to_csv(sample_stock_data, tmp_path):
    """Test saving data to CSV file"""
    # Arrange
    symbol = "AAPL"
    data_loader = DataLoader()
    expected_filepath = f"data/{symbol}.csv"
    
    # Act
    filepath = data_loader.save_to_csv(sample_stock_data, symbol)
    
    # Assert
    assert filepath == expected_filepath
    assert os.path.exists(expected_filepath)
    
    # Read saved data and convert Date column to datetime
    saved_data = pd.read_csv(expected_filepath)
    saved_data['Date'] = pd.to_datetime(saved_data['Date'])
    
    # Compare DataFrames
    pd.testing.assert_frame_equal(saved_data, sample_stock_data)