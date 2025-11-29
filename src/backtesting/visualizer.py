import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedVisualizer:
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
        fig = plt.figure(figsize=(20, 14))
        fig.suptitle(f'{symbol} - Comprehensive Backtesting Dashboard', fontsize=20, fontweight='bold', y=0.95)
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            print(f"Dashboard saved to: {save_path}")
        plt.show()

visualizer = AdvancedVisualizer()
