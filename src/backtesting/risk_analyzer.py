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
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'{symbol} - Comprehensive Risk Analysis', fontsize=16, fontweight='bold')
        portfolio_values = pd.Series(results['Portfolio_Value'])
        returns = portfolio_values.pct_change().dropna()
        risk_metrics = self._calculate_risk_metrics(returns)
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Risk analysis saved to: {save_path}")
        plt.show()
        return risk_metrics

    def _calculate_risk_metrics(self, returns: pd.Series) -> Dict:
        annual_factor = 252
        metrics = {
            'Volatility (Annual)': returns.std() * np.sqrt(annual_factor),
            'Skewness': stats.skew(returns),
            'Kurtosis': stats.kurtosis(returns),
            'VaR (95%)': np.percentile(returns, 5),
            'VaR (99%)': np.percentile(returns, 1),
            'CVaR (95%)': returns[returns <= np.percentile(returns, 5)].mean(),
            'CVaR (99%)': returns[returns <= np.percentile(returns, 1)].mean(),
        }
        return metrics

# Global risk analyzer instance
risk_analyzer = RiskAnalyzer()
