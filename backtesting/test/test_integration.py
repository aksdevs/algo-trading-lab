import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
from src.main import run_backtest, run_multiple_symbols, plot_results

def test_run_backtest_integration(sample_stock_data, mock_yf_ticker, mocker):
    """Test the complete backtest workflow"""
    # Arrange
    symbol = "AAPL"
    mock_ticker_instance = mock_yf_ticker(sample_stock_data)
    mocker.patch('yfinance.Ticker', return_value=mock_ticker_instance)
    
    # Mock matplotlib to avoid display issues in tests
    mocker.patch('matplotlib.pyplot.show')
    mocker.patch('matplotlib.pyplot.savefig')
    
    # Act
    results, metrics = run_backtest(
        symbol=symbol,
        start_date="2023-01-01",
        end_date="2023-12-31",
        initial_capital=100000,
        short_period=20,
        long_period=50
    )
    
    # Assert
    assert results is not None
    assert metrics is not None
    assert isinstance(results, pd.DataFrame)
    assert isinstance(metrics, dict)
    assert 'Total Return (%)' in metrics
    assert 'Signal' in results.columns
    assert 'Portfolio_Value' in results.columns

def test_run_backtest_with_error_handling(mocker):
    """Test error handling in run_backtest"""
    # Arrange
    symbol = "INVALID"
    mocker.patch('yfinance.Ticker', side_effect=Exception("API Error"))
    
    # Act
    results, metrics = run_backtest(symbol=symbol)
    
    # Assert
    assert results is None
    assert metrics is None

def test_run_multiple_symbols(sample_stock_data, mock_yf_ticker, mocker):
    """Test running backtests for multiple symbols"""
    # Arrange
    symbols = ["AAPL", "MSFT"]
    mock_ticker_instance = mock_yf_ticker(sample_stock_data)
    mocker.patch('yfinance.Ticker', return_value=mock_ticker_instance)
    
    # Mock matplotlib and file operations to prevent display issues
    mocker.patch('matplotlib.pyplot.show')
    mocker.patch('matplotlib.pyplot.savefig')
    mocker.patch('matplotlib.pyplot.figure')
    mocker.patch('os.makedirs')
    
    # Mock the entire plot_results function to avoid matplotlib backend issues
    mocker.patch('src.main.plot_results')
    
    # Act
    results = run_multiple_symbols(
        symbols,
        start_date="2023-01-01",
        end_date="2023-12-31",
        initial_capital=50000
    )
    
    # Assert - Should have successful results for symbols that work
    assert isinstance(results, dict)
    assert len(results) >= 1  # At least one should succeed
    
    # Check that successful results have the expected structure
    for symbol, data in results.items():
        assert symbol in symbols
        assert 'data' in data
        assert 'metrics' in data
        assert isinstance(data['data'], pd.DataFrame)
        assert isinstance(data['metrics'], dict)

def test_plot_results(sample_stock_data, mocker):
    """Test the plotting functionality"""
    # Arrange
    # Add required columns for plotting
    sample_stock_data['Signal'] = 0
    sample_stock_data['SMA_Short'] = sample_stock_data['Close'].rolling(20).mean()
    sample_stock_data['SMA_Long'] = sample_stock_data['Close'].rolling(50).mean()
    sample_stock_data['Portfolio_Value'] = 100000
    
    # Add some signals
    sample_stock_data.loc[100:102, 'Signal'] = 1  # Buy signals
    sample_stock_data.loc[200:202, 'Signal'] = -1  # Sell signals
    
    # Mock matplotlib functions
    mock_figure = mocker.patch('matplotlib.pyplot.figure')
    mock_subplot = mocker.patch('matplotlib.pyplot.subplot')
    mock_plot = mocker.patch('matplotlib.pyplot.plot')
    mock_scatter = mocker.patch('matplotlib.pyplot.scatter')
    mock_title = mocker.patch('matplotlib.pyplot.title')
    mock_ylabel = mocker.patch('matplotlib.pyplot.ylabel')
    mock_xlabel = mocker.patch('matplotlib.pyplot.xlabel')
    mock_legend = mocker.patch('matplotlib.pyplot.legend')
    mock_grid = mocker.patch('matplotlib.pyplot.grid')
    mock_tight_layout = mocker.patch('matplotlib.pyplot.tight_layout')
    mock_savefig = mocker.patch('matplotlib.pyplot.savefig')
    mock_show = mocker.patch('matplotlib.pyplot.show')
    mock_makedirs = mocker.patch('os.makedirs')
    
    symbol = "AAPL"
    
    # Act
    plot_results(sample_stock_data, symbol)
    
    # Assert
    mock_figure.assert_called_once_with(figsize=(15, 10))
    assert mock_subplot.call_count == 2
    assert mock_plot.call_count >= 3  # Price + 2 SMAs + Portfolio value
    mock_savefig.assert_called_once()
    mock_show.assert_called_once()
    mock_makedirs.assert_called_once_with('plots', exist_ok=True)