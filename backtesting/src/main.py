from src.data_loader import DataLoader
from strategies.sma_crossover import SMACrossoverStrategy
from src.visualizer import AdvancedVisualizer
from src.interactive_viz import InteractiveVisualizer
from src.risk_analyzer import RiskAnalyzer
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_backtest(symbol: str, start_date: str = None, end_date: str = None, 
                initial_capital: float = 100000, short_period: int = 20, 
                long_period: int = 50) -> None:
    """
    Run a backtest for the SMA Crossover strategy.
    
    Args:
        symbol (str): Stock symbol to backtest
        start_date (str, optional): Start date for backtesting
        end_date (str, optional): End date for backtesting
        initial_capital (float): Initial capital for the strategy
        short_period (int): Short-term SMA period
        long_period (int): Long-term SMA period
    """
    # Fetch data
    data_loader = DataLoader()
    try:
        print(f"Fetching data for {symbol}...")
        if start_date and end_date:
            data = data_loader.fetch_data(symbol, start_date=start_date, end_date=end_date)
        else:
            data = data_loader.fetch_data(symbol)
            
        print(f"Data fetched: {len(data)} rows")
            
        # Initialize and run strategy
        strategy = SMACrossoverStrategy(short_period=short_period, long_period=long_period)
        strategy.initialize(data, initial_capital=initial_capital)
        results, metrics = strategy.run_backtest()
        
        # Print performance metrics
        print(f"\nBacktesting Results for {symbol}:")
        print("=" * 40)
        for metric, value in metrics.items():
            print(f"{metric}: {value:.2f}")
            
        # Create advanced visualizations
        visualizer = AdvancedVisualizer()
        interactive_viz = InteractiveVisualizer()
        risk_analyzer = RiskAnalyzer()
        
        # Create comprehensive dashboard
        dashboard_path = f"plots/{symbol}_dashboard.png"
        visualizer.create_comprehensive_dashboard(results, symbol, metrics, dashboard_path)
        
        # Create interactive dashboard
        interactive_path = f"plots/{symbol}_interactive.html"
        interactive_viz.create_interactive_dashboard(results, symbol, metrics, interactive_path)
        
        # Create risk analysis
        risk_path = f"plots/{symbol}_risk_analysis.png"
        risk_metrics = risk_analyzer.comprehensive_risk_analysis(results, symbol, save_path=risk_path)
        
        # Print risk metrics
        print(f"\nRisk Analysis for {symbol}:")
        print("-" * 30)
        for metric, value in risk_metrics.items():
            if isinstance(value, float):
                if '%' in metric or 'Ratio' in metric:
                    print(f"{metric}: {value:.4f}")
                else:
                    print(f"{metric}: {value:.6f}")
            else:
                print(f"{metric}: {value}")
        
        # Also create traditional plot for compatibility
        plot_results(results, symbol)
        
        # Save results
        output_file = data_loader.save_to_csv(results, f"{symbol}_backtest_results")
        print(f"\nResults saved to: {output_file}")
        
        return results, metrics
        
    except Exception as e:
        print(f"Error during backtesting: {str(e)}")
        return None, None

def plot_results(results: pd.DataFrame, symbol: str) -> None:
    """
    Plot the backtest results.
    
    Args:
        results (pd.DataFrame): DataFrame containing backtest results
        symbol (str): Stock symbol
    """
    plt.figure(figsize=(15, 10))
    
    # Plot price and moving averages
    plt.subplot(2, 1, 1)
    plt.plot(results['Date'], results['Close'], label='Price', alpha=0.7, linewidth=1)
    plt.plot(results['Date'], results['SMA_Short'], label=f'Short SMA ({results.iloc[0]["SMA_Short"]:.0f})', alpha=0.8)
    plt.plot(results['Date'], results['SMA_Long'], label=f'Long SMA ({results.iloc[0]["SMA_Long"]:.0f})', alpha=0.8)
    
    # Plot buy/sell signals
    buy_signals = results[results['Signal'] == 1]
    sell_signals = results[results['Signal'] == -1]
    
    if not buy_signals.empty:
        plt.scatter(buy_signals['Date'], buy_signals['Close'], 
                   marker='^', color='green', label='Buy Signal', s=100, zorder=5)
    if not sell_signals.empty:
        plt.scatter(sell_signals['Date'], sell_signals['Close'], 
                   marker='v', color='red', label='Sell Signal', s=100, zorder=5)
    
    plt.title(f'{symbol} - Price Action and Trading Signals')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot portfolio value
    plt.subplot(2, 1, 2)
    plt.plot(results['Date'], results['Portfolio_Value'], label='Portfolio Value', color='purple', linewidth=2)
    plt.title('Portfolio Value Over Time')
    plt.ylabel('Portfolio Value ($)')
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create plots directory if it doesn't exist
    os.makedirs('plots', exist_ok=True)
    plt.savefig(f'plots/{symbol}_backtest_plot.png', dpi=300, bbox_inches='tight')
    print(f"Plot saved to: plots/{symbol}_backtest_plot.png")
    plt.show()

def run_multiple_symbols(symbols: list, **kwargs) -> dict:
    """
    Run backtests for multiple symbols.
    
    Args:
        symbols (list): List of stock symbols to backtest
        **kwargs: Additional arguments for run_backtest
        
    Returns:
        dict: Dictionary with results for each symbol
    """
    results = {}
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"Running backtest for {symbol}")
        print('='*50)
        
        result, metrics = run_backtest(symbol, **kwargs)
        if result is not None and metrics is not None:
            results[symbol] = {
                'data': result,
                'metrics': metrics
            }
    
    # Create comparison visualizations if we have multiple results
    if len(results) > 1:
        print(f"\nCreating comparison visualizations...")
        
        # Static comparison chart
        visualizer = AdvancedVisualizer()
        comparison_path = "plots/multi_symbol_comparison.png"
        visualizer.create_comparison_chart(results, comparison_path)
        print(f"Comparison chart saved to: {comparison_path}")
        
        # Interactive performance heatmap
        interactive_viz = InteractiveVisualizer()
        heatmap_path = "plots/performance_heatmap.html"
        interactive_viz.create_performance_heatmap(results, heatmap_path)
    
    return results

if __name__ == "__main__":
    # Example usage - Single stock backtest
    print("Running Single Stock Backtest Example")
    print("="*50)
    
    symbol = "SPY"  # S&P 500 ETF
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    
    results, metrics = run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000,
        short_period=20,
        long_period=50
    )
    
    # Example usage - Multiple stocks backtest
    print("\n\nRunning Multiple Stocks Backtest Example")
    print("="*50)
    
    symbols = ["AAPL", "MSFT", "GOOGL"]
    multiple_results = run_multiple_symbols(
        symbols,
        start_date="2022-01-01",
        end_date="2023-12-31",
        initial_capital=100000,
        short_period=10,
        long_period=30
    )
    
    # Compare results
    if multiple_results:
        print("\n\nComparison of Results:")
        print("="*60)
        print(f"{'Symbol':<8} {'Total Return (%)':<18} {'Sharpe Ratio':<15} {'Max Drawdown (%)':<18}")
        print("-"*60)
        
        for symbol, data in multiple_results.items():
            metrics = data['metrics']
            print(f"{symbol:<8} {metrics['Total Return (%)']:<18.2f} "
                  f"{metrics['Sharpe Ratio']:<15.2f} {metrics['Max Drawdown (%)']:<18.2f}")
    
    print("\nBacktesting complete!")

