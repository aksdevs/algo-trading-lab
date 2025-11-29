import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import seaborn as sns
from scipy import stats
import os

class RiskAnalyzer:
    """Advanced risk analysis and visualization class"""
    
    def __init__(self, figsize: Tuple[int, int] = (16, 12)):
        self.figsize = figsize
        plt.style.use('seaborn-v0_8')
        
    def comprehensive_risk_analysis(self, results: pd.DataFrame, symbol: str, 
                                  benchmark_data: pd.DataFrame = None, 
                                  save_path: str = None) -> Dict:
        """
        Create comprehensive risk analysis dashboard
        
        Args:
            results: Backtest results DataFrame
            symbol: Stock symbol
            benchmark_data: Optional benchmark data for comparison
            save_path: Optional path to save the plot
            
        Returns:
            Dict: Calculated risk metrics
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'{symbol} - Comprehensive Risk Analysis', fontsize=16, fontweight='bold')
        
        # Calculate returns and metrics
        portfolio_values = pd.Series(results['Portfolio_Value'])
        returns = portfolio_values.pct_change().dropna()
        price_returns = results['Close'].pct_change().dropna()
        
        risk_metrics = self._calculate_risk_metrics(returns)
        
        # 1. Drawdown Analysis (Top Left)
        self._plot_drawdown_analysis(axes[0, 0], portfolio_values, symbol)
        
        # 2. Returns Distribution with Risk Measures (Top Center)
        self._plot_returns_distribution_with_risk(axes[0, 1], returns)
        
        # 3. Rolling Volatility (Top Right)
        self._plot_rolling_volatility(axes[0, 2], returns)
        
        # 4. Value at Risk Analysis (Bottom Left)
        self._plot_var_analysis(axes[1, 0], returns)
        
        # 5. Beta Analysis (Bottom Center) - if benchmark provided
        if benchmark_data is not None:
            benchmark_returns = benchmark_data['Close'].pct_change().dropna()
            self._plot_beta_analysis(axes[1, 1], returns, benchmark_returns)
        else:
            self._plot_correlation_analysis(axes[1, 1], returns, price_returns)
        
        # 6. Risk-Return Scatter over time (Bottom Right)
        self._plot_risk_return_evolution(axes[1, 2], returns)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"Risk analysis saved to: {save_path}")
        
        plt.show()
        
        return risk_metrics
    
    def _calculate_risk_metrics(self, returns: pd.Series) -> Dict:
        """Calculate comprehensive risk metrics"""
        annual_factor = 252  # Trading days per year
        
        metrics = {
            'Volatility (Annual)': returns.std() * np.sqrt(annual_factor),
            'Skewness': stats.skew(returns),
            'Kurtosis': stats.kurtosis(returns),
            'VaR (95%)': np.percentile(returns, 5),
            'VaR (99%)': np.percentile(returns, 1),
            'CVaR (95%)': returns[returns <= np.percentile(returns, 5)].mean(),
            'CVaR (99%)': returns[returns <= np.percentile(returns, 1)].mean(),
            'Maximum Daily Loss': returns.min(),
            'Maximum Daily Gain': returns.max(),
            'Positive Days Ratio': (returns > 0).mean(),
            'Calmar Ratio': self._calculate_calmar_ratio(returns),
            'Sortino Ratio': self._calculate_sortino_ratio(returns),
        }
        
        return metrics
    
    def _calculate_calmar_ratio(self, returns: pd.Series) -> float:
        """Calculate Calmar ratio (Annual return / Max drawdown)"""
        annual_return = (1 + returns.mean()) ** 252 - 1
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        return annual_return / max_drawdown if max_drawdown != 0 else 0
    
    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio (focuses on downside deviation)"""
        annual_return = (1 + returns.mean()) ** 252 - 1
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252)
        
        return annual_return / downside_deviation if downside_deviation != 0 else 0
    
    def _plot_drawdown_analysis(self, ax, portfolio_values: pd.Series, symbol: str):
        """Plot detailed drawdown analysis"""
        running_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - running_max) / running_max * 100
        
        # Plot drawdown
        ax.fill_between(range(len(drawdown)), drawdown, 0, 
                       color='red', alpha=0.3, label='Drawdown')
        ax.plot(drawdown, color='red', linewidth=1.5)
        
        # Mark significant drawdowns
        significant_dd = drawdown[drawdown < -5]  # More than 5% drawdown
        if not significant_dd.empty:
            ax.scatter(significant_dd.index, significant_dd.values, 
                      color='darkred', s=30, zorder=5)
        
        # Statistics
        max_dd = drawdown.min()
        avg_dd = drawdown[drawdown < 0].mean()
        dd_duration = self._calculate_drawdown_duration(drawdown)
        
        textstr = f'Max DD: {max_dd:.2f}%\nAvg DD: {avg_dd:.2f}%\nMax Duration: {dd_duration} days'
        ax.text(0.02, 0.02, textstr, transform=ax.transAxes, 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title('Drawdown Analysis', fontweight='bold')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)
    
    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate maximum drawdown duration"""
        in_drawdown = drawdown < 0
        drawdown_periods = []
        current_period = 0
        
        for is_dd in in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0
        
        return max(drawdown_periods) if drawdown_periods else 0
    
    def _plot_returns_distribution_with_risk(self, ax, returns: pd.Series):
        """Plot returns distribution with risk measures"""
        returns_pct = returns * 100
        
        # Histogram
        n, bins, patches = ax.hist(returns_pct, bins=50, alpha=0.7, 
                                  color='skyblue', edgecolor='black', density=True)
        
        # Fit normal distribution
        mu, sigma = returns_pct.mean(), returns_pct.std()
        x = np.linspace(returns_pct.min(), returns_pct.max(), 100)
        normal_curve = stats.norm.pdf(x, mu, sigma)
        ax.plot(x, normal_curve, 'r-', linewidth=2, label='Normal Distribution')
        
        # Mark VaR levels
        var_95 = np.percentile(returns_pct, 5)
        var_99 = np.percentile(returns_pct, 1)
        
        ax.axvline(var_95, color='orange', linestyle='--', linewidth=2, 
                  label=f'VaR 95%: {var_95:.2f}%')
        ax.axvline(var_99, color='red', linestyle='--', linewidth=2, 
                  label=f'VaR 99%: {var_99:.2f}%')
        ax.axvline(mu, color='green', linestyle='-', linewidth=2, 
                  label=f'Mean: {mu:.2f}%')
        
        # Add skewness and kurtosis info
        skewness = stats.skew(returns_pct)
        kurtosis = stats.kurtosis(returns_pct)
        textstr = f'Skewness: {skewness:.3f}\nKurtosis: {kurtosis:.3f}'
        ax.text(0.75, 0.95, textstr, transform=ax.transAxes, 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_title('Returns Distribution & Risk Measures', fontweight='bold')
        ax.set_xlabel('Daily Return (%)')
        ax.set_ylabel('Density')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_rolling_volatility(self, ax, returns: pd.Series):
        """Plot rolling volatility analysis"""
        windows = [20, 60, 120]  # 1 month, 3 months, 6 months
        colors = ['blue', 'green', 'red']
        
        for window, color in zip(windows, colors):
            rolling_vol = returns.rolling(window).std() * np.sqrt(252) * 100
            ax.plot(rolling_vol, color=color, linewidth=1.5, 
                   label=f'{window}-day Rolling Volatility', alpha=0.8)
        
        # Add overall volatility line
        overall_vol = returns.std() * np.sqrt(252) * 100
        ax.axhline(overall_vol, color='black', linestyle='--', 
                  label=f'Overall Volatility: {overall_vol:.2f}%')
        
        ax.set_title('Rolling Volatility Analysis', fontweight='bold')
        ax.set_ylabel('Annualized Volatility (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_var_analysis(self, ax, returns: pd.Series):
        """Plot Value at Risk analysis over time"""
        window = 60  # 3-month rolling window
        
        rolling_var_95 = returns.rolling(window).quantile(0.05) * 100
        rolling_var_99 = returns.rolling(window).quantile(0.01) * 100
        
        ax.plot(rolling_var_95, color='orange', linewidth=2, 
               label='Rolling VaR 95%', alpha=0.8)
        ax.plot(rolling_var_99, color='red', linewidth=2, 
               label='Rolling VaR 99%', alpha=0.8)
        
        # Mark actual losses beyond VaR
        returns_pct = returns * 100
        var_95_breaches = returns_pct[returns_pct < rolling_var_95]
        var_99_breaches = returns_pct[returns_pct < rolling_var_99]
        
        if not var_95_breaches.empty:
            ax.scatter(var_95_breaches.index, var_95_breaches.values, 
                      color='orange', s=30, alpha=0.7, zorder=5)
        
        if not var_99_breaches.empty:
            ax.scatter(var_99_breaches.index, var_99_breaches.values, 
                      color='red', s=30, alpha=0.7, zorder=5)
        
        ax.set_title('Value at Risk Analysis', fontweight='bold')
        ax.set_ylabel('VaR (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_beta_analysis(self, ax, returns: pd.Series, benchmark_returns: pd.Series):
        """Plot beta analysis against benchmark"""
        # Align returns
        aligned_data = pd.DataFrame({'Portfolio': returns, 'Benchmark': benchmark_returns}).dropna()
        
        # Calculate rolling beta
        window = 60
        rolling_beta = aligned_data['Portfolio'].rolling(window).cov(aligned_data['Benchmark']) / \
                      aligned_data['Benchmark'].rolling(window).var()
        
        ax.plot(rolling_beta, color='blue', linewidth=2, label='Rolling Beta (60-day)')
        ax.axhline(1, color='black', linestyle='--', alpha=0.7, label='Beta = 1')
        ax.axhline(0, color='gray', linestyle='-', alpha=0.5)
        
        # Overall beta
        overall_beta = np.cov(aligned_data['Portfolio'], aligned_data['Benchmark'])[0, 1] / \
                      np.var(aligned_data['Benchmark'])
        ax.axhline(overall_beta, color='red', linestyle='--', 
                  label=f'Overall Beta: {overall_beta:.3f}')
        
        ax.set_title('Beta Analysis vs Benchmark', fontweight='bold')
        ax.set_ylabel('Beta')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_correlation_analysis(self, ax, returns: pd.Series, price_returns: pd.Series):
        """Plot correlation analysis with underlying asset"""
        # Rolling correlation
        window = 60
        rolling_corr = returns.rolling(window).corr(price_returns)
        
        ax.plot(rolling_corr, color='purple', linewidth=2, 
               label='Rolling Correlation (60-day)')
        ax.axhline(0, color='gray', linestyle='-', alpha=0.5)
        
        # Overall correlation
        overall_corr = returns.corr(price_returns)
        ax.axhline(overall_corr, color='red', linestyle='--', 
                  label=f'Overall Correlation: {overall_corr:.3f}')
        
        ax.set_title('Correlation with Underlying Asset', fontweight='bold')
        ax.set_ylabel('Correlation')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_risk_return_evolution(self, ax, returns: pd.Series):
        """Plot risk-return evolution over time"""
        window = 60
        
        rolling_return = returns.rolling(window).mean() * 252 * 100  # Annualized
        rolling_risk = returns.rolling(window).std() * np.sqrt(252) * 100  # Annualized
        
        # Color points by time (blue to red)
        colors = plt.cm.viridis(np.linspace(0, 1, len(rolling_return.dropna())))
        
        scatter = ax.scatter(rolling_risk, rolling_return, c=colors, s=30, alpha=0.7)
        
        # Add colorbar
        plt.colorbar(scatter, ax=ax, label='Time Progress')
        
        ax.set_title('Risk-Return Evolution', fontweight='bold')
        ax.set_xlabel('Risk (Annualized Volatility %)')
        ax.set_ylabel('Return (Annualized %)')
        ax.grid(True, alpha=0.3)

# Global risk analyzer instance
risk_analyzer = RiskAnalyzer()