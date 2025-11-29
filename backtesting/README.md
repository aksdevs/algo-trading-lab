# Financial Backtesting Framework

A comprehensive Python framework for backtesting trading strategies using historical market data. This project provides a modular architecture for implementing, testing, and analyzing trading strategies with real market data from Yahoo Finance.

## Features

- **Data Fetching**: Automated data retrieval using Yahoo Finance API
- **Strategy Framework**: Extensible base class for implementing custom trading strategies
- **Built-in Strategies**: SMA Crossover strategy implementation
- **Performance Analytics**: Comprehensive metrics including returns, Sharpe ratio, and drawdown analysis
- **Visualization**: Interactive plots showing price action, signals, and portfolio performance
- **Testing Suite**: Complete unit and integration test coverage
- **Modular Design**: Easy to extend with new strategies and indicators

## Project Structure

```
backtesting/
├── src/
│   ├── __init__.py
│   ├── data_loader.py      # Market data fetching and processing
│   └── main.py             # Main execution and example usage
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py    # Abstract base class for all strategies
│   └── sma_crossover.py    # Simple Moving Average crossover strategy
├── test/
│   ├── __init__.py
│   ├── conftest.py         # Test fixtures and utilities
│   ├── test_data_loader.py # Tests for data loading functionality
│   ├── test_strategy.py    # Tests for base strategy class
│   ├── test_sma_crossover.py # Tests for SMA crossover strategy
│   └── test_integration.py # Integration tests
├── data/                   # Directory for storing CSV data files
├── plots/                  # Directory for saving generated plots
├── requirements.txt        # Project dependencies
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd backtesting
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from src.main import run_backtest

# Run a simple backtest
results, metrics = run_backtest(
    symbol="SPY",
    start_date="2020-01-01",
    end_date="2023-12-31",
    initial_capital=100000,
    short_period=20,
    long_period=50
)

print("Performance Metrics:")
for metric, value in metrics.items():
    print(f"{metric}: {value:.2f}")
```

### Multiple Symbols Analysis

```python
from src.main import run_multiple_symbols

symbols = ["AAPL", "MSFT", "GOOGL", "SPY"]
results = run_multiple_symbols(
    symbols,
    start_date="2022-01-01",
    end_date="2023-12-31",
    initial_capital=100000
)
```

### Custom Strategy Implementation

```python
from strategies.base_strategy import Strategy
import pandas as pd

class MyCustomStrategy(Strategy):
    def __init__(self, parameter1=10, parameter2=20):
        super().__init__()
        self.param1 = parameter1
        self.param2 = parameter2
    
    def generate_signals(self) -> pd.Series:
        # Implement your strategy logic here
        signals = pd.Series(0, index=self.data.index)
        
        # Example: Simple momentum strategy
        returns = self.data['Close'].pct_change()
        signals[returns > 0.02] = 1    # Buy signal
        signals[returns < -0.02] = -1  # Sell signal
        
        return signals

# Use your custom strategy
strategy = MyCustomStrategy(parameter1=15, parameter2=25)
strategy.initialize(data, initial_capital=100000)
results, metrics = strategy.run_backtest()
```

## Available Strategies

### SMA Crossover Strategy

The Simple Moving Average crossover strategy generates signals based on the intersection of short-term and long-term moving averages:

- **Buy Signal**: When short-term SMA crosses above long-term SMA
- **Sell Signal**: When short-term SMA crosses below long-term SMA

**Parameters:**
- `short_period`: Period for short-term SMA (default: 20)
- `long_period`: Period for long-term SMA (default: 50)

## Performance Metrics

The framework calculates the following performance metrics:

- **Total Return (%)**: Overall percentage return from start to finish
- **Annual Return (%)**: Annualized return rate
- **Sharpe Ratio**: Risk-adjusted return measure
- **Max Drawdown (%)**: Maximum peak-to-trough decline
- **Final Portfolio Value**: End value of the portfolio

## Data Sources

- **Primary**: Yahoo Finance API via `yfinance` library
- **Supported Assets**: Stocks, ETFs, indices, cryptocurrencies
- **Data Frequency**: Daily, weekly, monthly intervals
- **Historical Range**: Up to maximum available history per symbol

## Testing

Run the complete test suite:

```bash
# Run all tests with coverage
pytest -v --cov=src --cov=strategies

# Run specific test file
pytest test/test_data_loader.py -v

# Run tests with detailed output
pytest -v -s
```

Test Coverage:
- Data loading and validation: 93%
- Base strategy framework: 98% 
- SMA crossover strategy: 100%
- Integration tests: Full workflow coverage

## Configuration

### Environment Variables

You can set the following environment variables for configuration:

```bash
export DATA_DIR="./custom_data"      # Custom data directory
export PLOTS_DIR="./custom_plots"   # Custom plots directory
```

### Strategy Parameters

Modify strategy parameters in your code:

```python
# SMA Crossover with custom parameters
strategy = SMACrossoverStrategy(
    short_period=10,    # Faster signals
    long_period=30      # More responsive
)
```

## Examples

### Example 1: Technology Stocks Analysis

```python
from src.main import run_multiple_symbols

tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
results = run_multiple_symbols(
    tech_stocks,
    start_date="2021-01-01",
    end_date="2023-12-31",
    initial_capital=50000,
    short_period=15,
    long_period=35
)

# Analyze best performer
best_return = max(results.items(), 
                  key=lambda x: x[1]['metrics']['Total Return (%)'])
print(f"Best performer: {best_return[0]} with {best_return[1]['metrics']['Total Return (%)']:.2f}% return")
```

### Example 2: Market Index Comparison

```python
indices = ["SPY", "QQQ", "IWM", "VTI"]
results = run_multiple_symbols(
    indices,
    start_date="2020-01-01",
    end_date="2023-12-31",
    initial_capital=100000
)
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Add your changes with tests
4. Run the test suite: `pytest`
5. Submit a pull request

### Adding New Strategies

1. Create a new file in the `strategies/` directory
2. Inherit from `Strategy` base class
3. Implement the `generate_signals()` method
4. Add corresponding tests in `test/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. It should not be used for actual trading without proper testing and risk management. Past performance does not guarantee future results.
