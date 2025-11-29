import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import os

class InteractiveVisualizer:
    """Interactive visualization class using Plotly for web-based charts"""
    
    def __init__(self):
        self.colors = {
            'price': '#2E86AB',
            'sma_short': '#A23B72',
            'sma_long': '#F18F01',
            'portfolio': '#C73E1D',
            'buy': '#00C851',
            'sell': '#FF4444',
            'volume': '#95A5A6'
        }
    
    def create_interactive_dashboard(self, results: pd.DataFrame, symbol: str, 
                                   metrics: Dict, save_path: str = None) -> None:
        # (implementation omitted for brevity; copied from original project)
        dates = pd.to_datetime(results['Date'])
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Scatter(x=dates, y=results['Close'], name='Price'))
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            fig.write_html(save_path)
            print(f"Interactive dashboard saved to: {save_path}")
        fig.show()

    def create_performance_heatmap(self, results_dict: Dict[str, Dict], save_path: str = None) -> None:
        symbols = list(results_dict.keys())
        metrics_names = ['Total Return (%)', 'Annual Return (%)', 'Sharpe Ratio', 'Max Drawdown (%)']
        data_matrix = []
        for metric in metrics_names:
            row = []
            for symbol in symbols:
                value = results_dict[symbol]['metrics'][metric]
                row.append(value)
            data_matrix.append(row)
        fig = go.Figure(data=go.Heatmap(z=data_matrix, x=symbols, y=metrics_names))
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            fig.write_html(save_path)
            print(f"Performance heatmap saved to: {save_path}")
        fig.show()

# Global interactive visualizer instance
interactive_visualizer = InteractiveVisualizer()
