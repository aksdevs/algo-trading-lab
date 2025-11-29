"""
Backtesting Framework Demo
==========================

This script demonstrates the complete functionality of the backtesting framework.
Run this to see the framework in action with real market data.
"""

import sys
import os
sys.path.append('src')

from src.main import run_backtest, run_multiple_symbols
from src.config import config
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def demo_single_stock():
    """Demonstrate single stock backtesting"""
    print("=" * 60)
    print("DEMO 1: Single Stock Backtesting")
    print("=" * 60)
    
    print("Running SMA Crossover strategy on SPY (S&P 500 ETF)")
    print("Period: 2022-01-01 to 2023-12-31")
    print("Strategy: 20-day SMA vs 50-day SMA crossover")
    print("Initial Capital: $100,000")
    print()
    
    try:
        results, metrics = run_backtest(
            symbol="SPY",
            start_date="2022-01-01", 
            end_date="2023-12-31",
            initial_capital=100000,
            short_period=20,
            long_period=50
        )
        
        if results is not None and metrics is not None:
            print("✅ Backtest completed successfully!")
            print("\nKey Performance Metrics:")
            print("-" * 30)
            for metric, value in metrics.items():
                print(f"{metric}: {value:.2f}")
        else:
            print("❌ Backtest failed - possibly due to network issues")
            print("   The framework is working, but couldn't fetch live data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   This is likely due to network connectivity or API limits")

def demo_multiple_stocks():
    """Demonstrate multiple stock backtesting"""
    print("\n" + "=" * 60)
    print("DEMO 2: Multiple Stocks Comparison")
    print("=" * 60)
    
    # Get symbols from config
    tech_stocks = config.get_symbol_list('tech_stocks')[:3]  # Take first 3
    print(f"Comparing tech stocks: {', '.join(tech_stocks)}")
    print("Period: 2023-01-01 to 2023-12-31")
    print("Strategy: 10-day SMA vs 30-day SMA (faster signals)")
    print("Initial Capital: $50,000 each")
    print()
    
    try:
        results = run_multiple_symbols(
            tech_stocks,
            start_date="2023-01-01",
            end_date="2023-12-31", 
            initial_capital=50000,
            short_period=10,
            long_period=30
        )
        
        if results:
            print("✅ Multi-stock backtest completed!")
            print("\nComparison Results:")
            print("-" * 50)
            print(f"{'Stock':<8} {'Return %':<12} {'Sharpe':<8} {'Drawdown %':<12}")
            print("-" * 50)
            
            for symbol, data in results.items():
                metrics = data['metrics']
                print(f"{symbol:<8} {metrics['Total Return (%)']:<12.2f} "
                      f"{metrics['Sharpe Ratio']:<8.2f} {metrics['Max Drawdown (%)']:<12.2f}")
        else:
            print("❌ Multi-stock backtest failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_configuration():
    """Demonstrate configuration features"""
    print("\n" + "=" * 60)
    print("DEMO 3: Configuration Management") 
    print("=" * 60)
    
    print("Available configuration options:")
    print()
    
    print("SMA Strategy Parameters:")
    sma_params = config.get_sma_params()
    for key, value in sma_params.items():
        print(f"  {key}: {value}")
    
    print("\nPredefined Symbol Groups:")
    symbol_groups = ['tech_stocks', 'market_indices', 'crypto', 'commodities']
    for group in symbol_groups:
        symbols = config.get_symbol_list(group)
        print(f"  {group}: {', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''}")
    
    print(f"\nDefault Initial Capital: ${config.get('general', 'initial_capital'):,}")
    print(f"Data Directory: {config.get('general', 'data_dir')}")
    print(f"Plots Directory: {config.get('general', 'plots_dir')}")

def main():
    """Run the complete demo"""
    print("🚀 BACKTESTING FRAMEWORK DEMONSTRATION")
    print("📈 Financial Strategy Testing Made Simple")
    print()
    
    # Demo configuration
    demo_configuration()
    
    # Demo single stock
    demo_single_stock()
    
    # Demo multiple stocks  
    demo_multiple_stocks()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE!")
    print("=" * 60)
    print()
    print("🎯 What you can do next:")
    print("   • Create custom strategies by inheriting from Strategy class")
    print("   • Modify config.ini to adjust default parameters") 
    print("   • Add new symbol groups for sector analysis")
    print("   • Implement additional technical indicators")
    print("   • Run backtests on different time periods")
    print()
    print("📁 Check the following directories:")
    print("   • data/ - CSV files with backtest results")
    print("   • plots/ - Generated charts and visualizations")
    print()
    print("🧪 Run tests with: pytest -v --cov=src --cov=strategies")
    print("📖 See README.md for detailed documentation")

if __name__ == "__main__":
    main()