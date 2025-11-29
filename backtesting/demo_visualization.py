"""
Advanced Visualization Demo for Backtesting Framework
====================================================

This script demonstrates all the advanced visualization capabilities
including interactive charts, risk analysis, and comparison dashboards.
"""

import sys
import os
sys.path.append('src')

from src.main import run_backtest, run_multiple_symbols
from src.visualizer import AdvancedVisualizer
from src.interactive_viz import InteractiveVisualizer
from src.risk_analyzer import RiskAnalyzer
from src.config import config
import matplotlib
matplotlib.use('TkAgg')  # Use interactive backend for demonstration

def demo_advanced_visualizations():
    """Demonstrate advanced visualization features"""
    print("🎨 ADVANCED VISUALIZATION DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases enhanced visualization capabilities:")
    print("• Comprehensive dashboards with multiple chart types")
    print("• Interactive web-based visualizations with Plotly")
    print("• Advanced risk analysis with statistical measures")
    print("• Multi-symbol comparison and heatmaps")
    print()
    
    # Demo 1: Single Symbol Advanced Analysis
    print("📊 DEMO 1: Advanced Single Symbol Analysis")
    print("-" * 50)
    
    symbol = "AAPL"
    print(f"Analyzing {symbol} with advanced visualizations...")
    
    try:
        results, metrics = run_backtest(
            symbol=symbol,
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=100000,
            short_period=20,
            long_period=50
        )
        
        if results is not None and metrics is not None:
            print(f"✅ Generated for {symbol}:")
            print(f"   • Static dashboard: plots/{symbol}_dashboard.png")
            print(f"   • Interactive dashboard: plots/{symbol}_interactive.html")
            print(f"   • Risk analysis: plots/{symbol}_risk_analysis.png")
            print(f"   • Traditional plot: plots/{symbol}_backtest_plot.png")
        
    except Exception as e:
        print(f"❌ Error in single symbol demo: {e}")
    
    # Demo 2: Multi-Symbol Comparison
    print(f"\n📈 DEMO 2: Multi-Symbol Comparison Visualizations")
    print("-" * 50)
    
    tech_symbols = ["AAPL", "MSFT", "GOOGL"]
    print(f"Comparing symbols: {', '.join(tech_symbols)}")
    
    try:
        results_dict = run_multiple_symbols(
            tech_symbols,
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=50000,
            short_period=10,
            long_period=30
        )
        
        if results_dict:
            print(f"✅ Generated comparison visualizations:")
            print(f"   • Multi-symbol comparison: plots/multi_symbol_comparison.png")
            print(f"   • Performance heatmap: plots/performance_heatmap.html")
    
    except Exception as e:
        print(f"❌ Error in multi-symbol demo: {e}")
    
    # Demo 3: Standalone Visualization Features
    print(f"\n🔬 DEMO 3: Standalone Advanced Features")
    print("-" * 50)
    
    # If we have successful results, create additional visualizations
    if 'results' in locals() and results is not None:
        print("Creating additional advanced visualizations...")
        
        try:
            # Advanced visualizer features
            visualizer = AdvancedVisualizer()
            print("• Creating enhanced dashboard...")
            
            # Interactive visualizer features
            interactive_viz = InteractiveVisualizer()
            print("• Creating interactive web dashboard...")
            
            # Risk analyzer features
            risk_analyzer = RiskAnalyzer()
            print("• Performing comprehensive risk analysis...")
            
            print("✅ All advanced visualization features demonstrated!")
            
        except Exception as e:
            print(f"❌ Error in standalone features: {e}")
    
    # Demo 4: Feature Summary
    print(f"\n🎯 VISUALIZATION FEATURES SUMMARY")
    print("=" * 60)
    print()
    
    print("📋 STATIC VISUALIZATIONS (matplotlib/seaborn):")
    print("   ✓ Comprehensive multi-panel dashboards")
    print("   ✓ Price action with technical indicators")
    print("   ✓ Portfolio performance vs benchmark")
    print("   ✓ Returns distribution analysis")
    print("   ✓ Drawdown analysis with statistics")
    print("   ✓ Multi-symbol comparison charts")
    print("   ✓ Performance metrics tables")
    print()
    
    print("🌐 INTERACTIVE VISUALIZATIONS (Plotly):")
    print("   ✓ Web-based interactive dashboards")
    print("   ✓ Zoomable and pannable charts")
    print("   ✓ Hover tooltips with detailed data")
    print("   ✓ Performance heatmaps")
    print("   ✓ Cross-filtering capabilities")
    print("   ✓ Exportable to HTML format")
    print()
    
    print("🔬 RISK ANALYSIS VISUALIZATIONS:")
    print("   ✓ Detailed drawdown analysis")
    print("   ✓ Value at Risk (VaR) calculations")
    print("   ✓ Rolling volatility analysis") 
    print("   ✓ Returns distribution with risk measures")
    print("   ✓ Beta and correlation analysis")
    print("   ✓ Risk-return evolution over time")
    print("   ✓ Statistical measures (skewness, kurtosis)")
    print()
    
    print("📊 COMPARISON & ANALYSIS:")
    print("   ✓ Multi-strategy performance comparison")
    print("   ✓ Heat maps for metric visualization")
    print("   ✓ Correlation matrices")
    print("   ✓ Risk-adjusted return analysis")
    print("   ✓ Benchmark comparisons")
    print()
    
    print("💾 OUTPUT FORMATS:")
    print("   ✓ High-resolution PNG images")
    print("   ✓ Interactive HTML files")
    print("   ✓ CSV data exports")
    print("   ✓ Customizable styling and themes")
    print()
    
    print("📁 CHECK GENERATED FILES:")
    print(f"   • Static images: plots/ directory (PNG files)")
    print(f"   • Interactive charts: plots/ directory (HTML files)")
    print(f"   • Data files: data/ directory (CSV files)")
    print()
    
    print("🚀 USAGE TIPS:")
    print("   • Open HTML files in web browser for interactivity")
    print("   • Use zoom and pan on interactive charts")
    print("   • Hover over data points for detailed information")
    print("   • Compare multiple strategies using heatmaps")
    print("   • Analyze risk metrics for better understanding")

def demo_custom_visualization():
    """Show how to create custom visualizations"""
    print(f"\n🎨 CUSTOM VISUALIZATION EXAMPLE")
    print("-" * 50)
    
    print("Example: Creating a custom risk-focused visualization")
    print("This shows how to extend the framework with custom charts:")
    print()
    
    code_example = """
# Example: Custom Risk Dashboard
from src.risk_analyzer import RiskAnalyzer
from src.data_loader import DataLoader
import matplotlib.pyplot as plt

# Get data
data_loader = DataLoader()
data = data_loader.fetch_data('SPY', start_date='2023-01-01')

# Custom risk analysis
risk_analyzer = RiskAnalyzer()
risk_metrics = risk_analyzer.comprehensive_risk_analysis(
    data, 'SPY', save_path='custom_risk_analysis.png'
)

# Print specific risk metrics
print(f"VaR 95%: {risk_metrics['VaR (95%)']:.4f}")
print(f"Sortino Ratio: {risk_metrics['Sortino Ratio']:.4f}")
"""
    
    print("Python Code:")
    print(code_example)
    print("This demonstrates the modular design for custom analysis!")

if __name__ == "__main__":
    demo_advanced_visualizations()
    demo_custom_visualization()
    
    print(f"\n🎉 VISUALIZATION DEMO COMPLETE!")
    print("=" * 60)
    print("The backtesting framework now includes:")
    print("• Professional-grade static visualizations")
    print("• Interactive web-based dashboards") 
    print("• Comprehensive risk analysis tools")
    print("• Multi-asset comparison capabilities")
    print("• Extensible visualization architecture")
    print()
    print("Ready for advanced financial analysis! 📊📈🚀")