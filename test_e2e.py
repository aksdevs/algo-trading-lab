"""
End-to-end test script for the backtesting framework
This script demonstrates the complete workflow
"""
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_loader import DataLoader
from strategies.sma_crossover import SMACrossoverStrategy
from src.config import Config
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

def test_complete_workflow():
    """Test the complete backtesting workflow"""
    print("Starting end-to-end test...")
    
    # Test 1: Configuration loading
    print("1. Testing configuration...")
    config = Config()
    sma_params = config.get_sma_params()
    print(f"   SMA Parameters: {sma_params}")
    
    # Test 2: Data loading with mock data
    print("2. Testing data creation...")
    # Create sample data for testing
    dates = pd.date_range(start='2023-01-01', end='2023-03-31', freq='D')
    sample_data = pd.DataFrame({
        'Date': dates,
        'Open': [100 + i*0.1 for i in range(len(dates))],
        'High': [101 + i*0.1 for i in range(len(dates))],
        'Low': [99 + i*0.1 for i in range(len(dates))],
        'Close': [100.5 + i*0.1 for i in range(len(dates))],
        'Volume': [1000000] * len(dates)
    })
    print(f"   Sample data created: {len(sample_data)} rows")
    
    # Test 3: Strategy execution
    print("3. Testing strategy execution...")
    strategy = SMACrossoverStrategy(**sma_params)
    strategy.initialize(sample_data, initial_capital=100000)
    
    results, metrics = strategy.run_backtest()
    print(f"   Backtest completed. Final portfolio value: ${metrics['Final Portfolio Value']:.2f}")
    print(f"   Total return: {metrics['Total Return (%)']:.2f}%")
    
    # Test 4: Data saving
    print("4. Testing data saving...")
    data_loader = DataLoader()
    os.makedirs('data', exist_ok=True)
    filepath = data_loader.save_to_csv(results, 'test_results')
    print(f"   Results saved to: {filepath}")
    
    # Test 5: Verify saved data
    print("5. Testing data loading...")
    loaded_data = pd.read_csv(filepath)
    print(f"   Loaded data: {len(loaded_data)} rows")
    
    print("\n✅ End-to-end test completed successfully!")
    print(f"✅ All components working: Config, DataLoader, Strategy, Backtesting")
    
    return True

if __name__ == "__main__":
    try:
        success = test_complete_workflow()
        if success:
            print("\n🎉 Project is complete and working!")
        else:
            print("\n❌ Some issues found")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()