import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedVisualizer:
    """Advanced visualization class for backtesting results"""
    
    def __init__(self, figsize: Tuple[int, int] = (16, 12), dpi: int = 300):
        self.figsize = figsize
        self.dpi = dpi
        self.colors = {
            'price': '#2E86AB',
            'sma_short': '#A23B72',
            'sma_long': '#F18F01',
            'portfolio': '#C73E1D',
            'buy': '#00C851',
            'sell': '#FF4444',
            'background': '#F8F9FA',
            'grid': '#E0E0E0'
        }
    
    def create_comprehensive_dashboard(self, results: pd.DataFrame, symbol: str, 
                                     metrics: Dict, save_path: str = None) -> None:
        """
        Create a comprehensive dashboard with multiple visualization panels
        
        Args:
            results (pd.DataFrame): Backtest results
            symbol (str): Stock symbol
            metrics (Dict): Performance metrics
            save_path (str): Optional path to save the plot
        """
        fig = plt.figure(figsize=(20, 14))
        fig.suptitle(f'{symbol} - Comprehensive Backtesting Dashboard', 
                    fontsize=20, fontweight='bold', y=0.95)
        
        # Define grid layout
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. Price Action and Signals (Top panel - spans 2 columns)
        ax1 = fig.add_subplot(gs[0:2, :2])
        self._plot_price_action(ax1, results, symbol)
        
        # 2. Portfolio Performance (Top right - spans 2 columns)
        ax2 = fig.add_subplot(gs[0:2, 2:])
        self._plot_portfolio_performance(ax2, results, metrics)
        
        # 3. Returns Distribution (Bottom left)
        ax3 = fig.add_subplot(gs[2, :2])
        self._plot_returns_distribution(ax3, results)
        
        # 4. Drawdown Analysis (Bottom right)
        ax4 = fig.add_subplot(gs[2, 2:])
        self._plot_drawdown_analysis(ax4, results)
        
        # 5. Performance Metrics Table (Bottom panel)
        ax5 = fig.add_subplot(gs[3, :])
        self._create_metrics_table(ax5, metrics, symbol)
        
        # Save or show
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"Dashboard saved to: {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def _plot_price_action(self, ax, results: pd.DataFrame, symbol: str) -> None:
        """Plot price action with moving averages and trading signals"""
        dates = pd.to_datetime(results['Date'])
        
        # Plot price and moving averages
        ax.plot(dates, results['Close'], label='Price', 
               color=self.colors['price'], linewidth=1.5, alpha=0.8)
        ax.plot(dates, results['SMA_Short'], label=f'SMA Short', 
               color=self.colors['sma_short'], linewidth=1.2, alpha=0.8)
        ax.plot(dates, results['SMA_Long'], label=f'SMA Long', 
               color=self.colors['sma_long'], linewidth=1.2, alpha=0.8)
        
        # Plot trading signals
        buy_signals = results[results['Signal'] == 1]
        sell_signals = results[results['Signal'] == -1]
        
        if not buy_signals.empty:
            buy_dates = pd.to_datetime(buy_signals['Date'])
            ax.scatter(buy_dates, buy_signals['Close'], 
                      marker='^', color=self.colors['buy'], s=100, 
                      label='Buy Signal', zorder=5, alpha=0.8)
        
        if not sell_signals.empty:
            sell_dates = pd.to_datetime(sell_signals['Date'])
            ax.scatter(sell_dates, sell_signals['Close'], 
                      marker='v', color=self.colors['sell'], s=100, 
                      label='Sell Signal', zorder=5, alpha=0.8)
        
        # Formatting
        ax.set_title(f'{symbol} - Price Action & Trading Signals', fontsize=14, fontweight='bold')
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='upper left', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_portfolio_performance(self, ax, results: pd.DataFrame, metrics: Dict) -> None:
        """Plot portfolio performance with benchmark comparison"""
        dates = pd.to_datetime(results['Date'])
        
        # Calculate returns for comparison
        portfolio_returns = pd.Series(results['Portfolio_Value']).pct_change().fillna(0)
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        
        price_returns = results['Close'].pct_change().fillna(0)
        benchmark_cumulative = (1 + price_returns).cumprod()
        
        # Plot portfolio vs benchmark
        ax.plot(dates, portfolio_cumulative, label='Strategy', 
               color=self.colors['portfolio'], linewidth=2.5)
        ax.plot(dates, benchmark_cumulative, label='Buy & Hold', 
               color=self.colors['price'], linewidth=1.5, alpha=0.7, linestyle='--')
        
        # Add performance metrics as text
        final_return = metrics['Total Return (%)']
        sharpe_ratio = metrics['Sharpe Ratio']
        max_dd = metrics['Max Drawdown (%)']
        
        textstr = f'Strategy Return: {final_return:.2f}%\nSharpe Ratio: {sharpe_ratio:.2f}\nMax Drawdown: {max_dd:.2f}%'
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor='white', alpha=0.8))
        
        ax.set_title('Portfolio Performance vs Buy & Hold', fontsize=14, fontweight='bold')
        ax.set_ylabel('Cumulative Returns', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _plot_returns_distribution(self, ax, results: pd.DataFrame) -> None:
        """Plot daily returns distribution with statistics"""
        returns = pd.Series(results['Portfolio_Value']).pct_change().dropna() * 100
        
        # Create histogram
        n, bins, patches = ax.hist(returns, bins=30, alpha=0.7, color=self.colors['portfolio'], 
                                  edgecolor='black', linewidth=0.5)
        
        # Add normal distribution overlay
        mu, sigma = returns.mean(), returns.std()
        x = np.linspace(returns.min(), returns.max(), 100)
        normal_dist = ((1/(sigma * np.sqrt(2 * np.pi))) * 
                      np.exp(-0.5 * ((x - mu)/sigma)**2)) * len(returns) * (bins[1] - bins[0])
        ax.plot(x, normal_dist, 'r--', linewidth=2, label='Normal Distribution')
        
        # Add vertical lines for mean and std
        ax.axvline(mu, color='red', linestyle='-', linewidth=2, alpha=0.8, label=f'Mean: {mu:.3f}%')
        ax.axvline(mu + sigma, color='orange', linestyle='--', alpha=0.8, label=f'+1σ: {mu+sigma:.3f}%')
        ax.axvline(mu - sigma, color='orange', linestyle='--', alpha=0.8, label=f'-1σ: {mu-sigma:.3f}%')
        
        ax.set_title('Daily Returns Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Daily Return (%)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    def _plot_drawdown_analysis(self, ax, results: pd.DataFrame) -> None:
        """Plot drawdown analysis"""
        dates = pd.to_datetime(results['Date'])
        portfolio_values = pd.Series(results['Portfolio_Value'])
        
        # Calculate running maximum and drawdown
        running_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - running_max) / running_max * 100
        
        # Plot drawdown
        ax.fill_between(dates, drawdown, 0, color=self.colors['sell'], 
                       alpha=0.3, label='Drawdown')
        ax.plot(dates, drawdown, color=self.colors['sell'], linewidth=1.5)
        
        # Mark maximum drawdown
        max_dd_idx = drawdown.idxmin()
        max_dd_date = dates.iloc[max_dd_idx]
        max_dd_value = drawdown.iloc[max_dd_idx]
        
        ax.scatter(max_dd_date, max_dd_value, color='red', s=100, 
                  zorder=5, label=f'Max DD: {max_dd_value:.2f}%')
        
        ax.set_title('Drawdown Analysis', fontsize=14, fontweight='bold')
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    def _create_metrics_table(self, ax, metrics: Dict, symbol: str) -> None:
        """Create a formatted metrics table"""
        ax.axis('off')
        
        # Prepare data for table
        table_data = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if '%' in key:
                    formatted_value = f"{value:.2f}%"
                elif 'Value' in key:
                    formatted_value = f"${value:,.2f}"
                else:
                    formatted_value = f"{value:.3f}"
            else:
                formatted_value = str(value)
            table_data.append([key, formatted_value])
        
        # Create table
        table = ax.table(cellText=table_data,
                        colLabels=['Metric', 'Value'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.6, 0.4])
        
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2)
        
        # Style the table
        for i in range(len(table_data) + 1):
            for j in range(2):
                cell = table[i, j]
                if i == 0:  # Header row
                    cell.set_facecolor(self.colors['sma_short'])
                    cell.set_text_props(weight='bold', color='white')
                else:
                    if i % 2 == 0:
                        cell.set_facecolor('#F8F9FA')
                    else:
                        cell.set_facecolor('white')
        
        ax.set_title(f'{symbol} - Performance Summary', fontsize=14, fontweight='bold', pad=20)
    
    def create_comparison_chart(self, results_dict: Dict[str, Dict], save_path: str = None) -> None:
        """
        Create comparison chart for multiple symbols/strategies
        
        Args:
            results_dict: Dictionary with symbol as key and {'data': df, 'metrics': dict} as value
            save_path: Optional path to save the plot
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Multi-Symbol/Strategy Comparison Dashboard', fontsize=16, fontweight='bold')
        
        symbols = list(results_dict.keys())
        colors = plt.cm.Set3(np.linspace(0, 1, len(symbols)))
        
        # 1. Cumulative returns comparison
        for i, (symbol, data) in enumerate(results_dict.items()):
            results = data['data']
            portfolio_returns = pd.Series(results['Portfolio_Value']).pct_change().fillna(0)
            cumulative_returns = (1 + portfolio_returns).cumprod()
            dates = pd.to_datetime(results['Date'])
            
            ax1.plot(dates, cumulative_returns, label=symbol, 
                    color=colors[i], linewidth=2, alpha=0.8)
        
        ax1.set_title('Cumulative Returns Comparison', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Cumulative Returns')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Performance metrics comparison
        metrics_names = ['Total Return (%)', 'Sharpe Ratio', 'Max Drawdown (%)']
        x_pos = np.arange(len(symbols))
        width = 0.25
        
        for i, metric in enumerate(metrics_names):
            values = [results_dict[symbol]['metrics'][metric] for symbol in symbols]
            ax2.bar(x_pos + i * width, values, width, 
                   label=metric, alpha=0.8, color=colors[i])
        
        ax2.set_title('Key Metrics Comparison', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Symbols')
        ax2.set_ylabel('Values')
        ax2.set_xticks(x_pos + width)
        ax2.set_xticklabels(symbols)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Risk-Return scatter plot
        returns = [results_dict[symbol]['metrics']['Total Return (%)'] for symbol in symbols]
        sharpe_ratios = [results_dict[symbol]['metrics']['Sharpe Ratio'] for symbol in symbols]
        
        scatter = ax3.scatter(returns, sharpe_ratios, 
                            c=[i for i in range(len(symbols))], 
                            cmap='viridis', s=100, alpha=0.7)
        
        for i, symbol in enumerate(symbols):
            ax3.annotate(symbol, (returns[i], sharpe_ratios[i]), 
                        xytext=(5, 5), textcoords='offset points')
        
        ax3.set_title('Risk-Return Analysis', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Total Return (%)')
        ax3.set_ylabel('Sharpe Ratio')
        ax3.grid(True, alpha=0.3)
        
        # 4. Drawdown comparison
        for i, (symbol, data) in enumerate(results_dict.items()):
            results = data['data']
            portfolio_values = pd.Series(results['Portfolio_Value'])
            running_max = portfolio_values.expanding().max()
            drawdown = (portfolio_values - running_max) / running_max * 100
            dates = pd.to_datetime(results['Date'])
            
            ax4.fill_between(dates, drawdown, 0, alpha=0.3, 
                           color=colors[i], label=symbol)
        
        ax4.set_title('Drawdown Comparison', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Drawdown (%)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"Comparison chart saved to: {save_path}")
        
        plt.show()

# Global visualizer instance
visualizer = AdvancedVisualizer()