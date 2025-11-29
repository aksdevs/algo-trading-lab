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
        """
        Create an interactive dashboard with plotly
        
        Args:
            results (pd.DataFrame): Backtest results
            symbol (str): Stock symbol
            metrics (Dict): Performance metrics
            save_path (str): Optional path to save the HTML file
        """
        # Create subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Price Action & Signals', 'Portfolio Performance',
                'Volume Analysis', 'Returns Distribution',
                'Drawdown Analysis', 'Rolling Metrics',
                'Trade Analysis', 'Risk Metrics'
            ),
            specs=[
                [{"secondary_y": True}, {"secondary_y": False}],
                [{"secondary_y": True}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"colspan": 2}, None]
            ],
            vertical_spacing=0.08
        )
        
        dates = pd.to_datetime(results['Date'])
        
        # 1. Price Action & Signals (Row 1, Col 1)
        # Price line
        fig.add_trace(
            go.Scatter(x=dates, y=results['Close'], name='Price',
                      line=dict(color=self.colors['price'], width=2),
                      hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'),
            row=1, col=1
        )
        
        # Moving averages
        fig.add_trace(
            go.Scatter(x=dates, y=results['SMA_Short'], name='SMA Short',
                      line=dict(color=self.colors['sma_short'], width=1.5, dash='dash')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=dates, y=results['SMA_Long'], name='SMA Long',
                      line=dict(color=self.colors['sma_long'], width=1.5, dash='dot')),
            row=1, col=1
        )
        
        # Trading signals
        buy_signals = results[results['Signal'] == 1]
        sell_signals = results[results['Signal'] == -1]
        
        if not buy_signals.empty:
            fig.add_trace(
                go.Scatter(x=pd.to_datetime(buy_signals['Date']), y=buy_signals['Close'],
                          mode='markers', name='Buy Signal',
                          marker=dict(symbol='triangle-up', size=12, color=self.colors['buy']),
                          hovertemplate='Buy Signal<br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'),
                row=1, col=1
            )
        
        if not sell_signals.empty:
            fig.add_trace(
                go.Scatter(x=pd.to_datetime(sell_signals['Date']), y=sell_signals['Close'],
                          mode='markers', name='Sell Signal',
                          marker=dict(symbol='triangle-down', size=12, color=self.colors['sell']),
                          hovertemplate='Sell Signal<br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'),
                row=1, col=1
            )
        
        # Volume (secondary y-axis)
        fig.add_trace(
            go.Bar(x=dates, y=results['Volume'], name='Volume',
                  marker_color=self.colors['volume'], opacity=0.3,
                  hovertemplate='Date: %{x}<br>Volume: %{y:,.0f}<extra></extra>'),
            row=1, col=1, secondary_y=True
        )
        
        # 2. Portfolio Performance (Row 1, Col 2)
        fig.add_trace(
            go.Scatter(x=dates, y=results['Portfolio_Value'], name='Portfolio Value',
                      line=dict(color=self.colors['portfolio'], width=3),
                      hovertemplate='Date: %{x}<br>Portfolio: $%{y:,.2f}<extra></extra>'),
            row=1, col=2
        )
        
        # Add benchmark (buy & hold)
        initial_price = results['Close'].iloc[0]
        final_price = results['Close'].iloc[-1]
        initial_portfolio = results['Portfolio_Value'].iloc[0]
        benchmark_values = (results['Close'] / initial_price) * initial_portfolio
        
        fig.add_trace(
            go.Scatter(x=dates, y=benchmark_values, name='Buy & Hold',
                      line=dict(color=self.colors['price'], width=2, dash='dash'),
                      hovertemplate='Date: %{x}<br>Buy & Hold: $%{y:,.2f}<extra></extra>'),
            row=1, col=2
        )
        
        # 3. Volume Analysis (Row 2, Col 1)
        # Volume bars with color coding based on price change
        price_change = results['Close'].pct_change()
        volume_colors = ['green' if x > 0 else 'red' for x in price_change]
        
        fig.add_trace(
            go.Bar(x=dates, y=results['Volume'], name='Volume',
                  marker_color=volume_colors, opacity=0.7,
                  hovertemplate='Date: %{x}<br>Volume: %{y:,.0f}<extra></extra>'),
            row=2, col=1
        )
        
        # 4. Returns Distribution (Row 2, Col 2)
        portfolio_returns = pd.Series(results['Portfolio_Value']).pct_change().dropna() * 100
        
        fig.add_trace(
            go.Histogram(x=portfolio_returns, name='Returns Distribution',
                        marker_color=self.colors['portfolio'], opacity=0.7,
                        nbinsx=30, hovertemplate='Return: %{x:.2f}%<br>Count: %{y}<extra></extra>'),
            row=2, col=2
        )
        
        # 5. Drawdown Analysis (Row 3, Col 1)
        portfolio_values = pd.Series(results['Portfolio_Value'])
        running_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - running_max) / running_max * 100
        
        fig.add_trace(
            go.Scatter(x=dates, y=drawdown, fill='tonexty', name='Drawdown',
                      line=dict(color=self.colors['sell']),
                      hovertemplate='Date: %{x}<br>Drawdown: %{y:.2f}%<extra></extra>'),
            row=3, col=1
        )
        
        # 6. Rolling Metrics (Row 3, Col 2)
        # Calculate 30-day rolling Sharpe ratio
        rolling_returns = portfolio_returns.rolling(30).mean()
        rolling_std = portfolio_returns.rolling(30).std()
        rolling_sharpe = np.sqrt(252) * rolling_returns / rolling_std
        
        fig.add_trace(
            go.Scatter(x=dates[30:], y=rolling_sharpe[30:], name='30-Day Rolling Sharpe',
                      line=dict(color=self.colors['portfolio'], width=2),
                      hovertemplate='Date: %{x}<br>Rolling Sharpe: %{y:.3f}<extra></extra>'),
            row=3, col=2
        )
        
        # 7. Trade Analysis (Row 4, spanning both columns)
        # Calculate trade statistics
        signals = results['Signal']
        trade_points = signals[signals != 0]
        
        if len(trade_points) > 0:
            trade_dates = []
            trade_values = []
            trade_types = []
            
            for idx in trade_points.index:
                trade_dates.append(dates.iloc[idx])
                trade_values.append(results['Portfolio_Value'].iloc[idx])
                trade_types.append('Buy' if signals.iloc[idx] == 1 else 'Sell')
            
            fig.add_trace(
                go.Scatter(x=trade_dates, y=trade_values, mode='markers+lines',
                          name='Trade Points',
                          marker=dict(size=10, color=[self.colors['buy'] if t == 'Buy' else self.colors['sell'] for t in trade_types]),
                          hovertemplate='%{text}<br>Date: %{x}<br>Portfolio: $%{y:,.2f}<extra></extra>',
                          text=trade_types),
                row=4, col=1
            )
        
        # Update layout
        fig.update_layout(
            title=f'{symbol} - Interactive Backtesting Dashboard',
            height=1200,
            showlegend=True,
            hovermode='x unified'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Date", row=4, col=1)
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=1, col=1, secondary_y=True)
        fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=2)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="Frequency", row=2, col=2)
        fig.update_yaxes(title_text="Drawdown (%)", row=3, col=1)
        fig.update_yaxes(title_text="Rolling Sharpe", row=3, col=2)
        fig.update_yaxes(title_text="Portfolio Value ($)", row=4, col=1)
        
        # Add metrics as annotations
        metrics_text = f"""
        <b>Performance Metrics:</b><br>
        Total Return: {metrics['Total Return (%)']:.2f}%<br>
        Annual Return: {metrics['Annual Return (%)']:.2f}%<br>
        Sharpe Ratio: {metrics['Sharpe Ratio']:.3f}<br>
        Max Drawdown: {metrics['Max Drawdown (%)']:.2f}%<br>
        Final Value: ${metrics['Final Portfolio Value']:,.2f}
        """
        
        fig.add_annotation(
            text=metrics_text,
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        )
        
        # Save as HTML
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            fig.write_html(save_path)
            print(f"Interactive dashboard saved to: {save_path}")
        
        # Show the plot
        fig.show()
    
    def create_performance_heatmap(self, results_dict: Dict[str, Dict], save_path: str = None) -> None:
        """
        Create a performance heatmap for multiple symbols
        
        Args:
            results_dict: Dictionary with symbol as key and {'data': df, 'metrics': dict} as value
            save_path: Optional path to save the HTML file
        """
        symbols = list(results_dict.keys())
        metrics_names = ['Total Return (%)', 'Annual Return (%)', 'Sharpe Ratio', 'Max Drawdown (%)']
        
        # Create data matrix
        data_matrix = []
        for metric in metrics_names:
            row = []
            for symbol in symbols:
                value = results_dict[symbol]['metrics'][metric]
                row.append(value)
            data_matrix.append(row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=data_matrix,
            x=symbols,
            y=metrics_names,
            colorscale='RdYlGn',
            hoverongaps=False,
            hovertemplate='Symbol: %{x}<br>Metric: %{y}<br>Value: %{z:.2f}<extra></extra>'
        ))
        
        # Add text annotations
        for i, metric in enumerate(metrics_names):
            for j, symbol in enumerate(symbols):
                value = data_matrix[i][j]
                fig.add_annotation(
                    x=j, y=i,
                    text=f"{value:.2f}",
                    showarrow=False,
                    font=dict(color="black" if abs(value) < max(abs(min(data_matrix[i])), abs(max(data_matrix[i]))) * 0.7 else "white")
                )
        
        fig.update_layout(
            title='Performance Metrics Heatmap',
            xaxis_title='Symbols',
            yaxis_title='Metrics'
        )
        
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else 'plots', exist_ok=True)
            fig.write_html(save_path)
            print(f"Performance heatmap saved to: {save_path}")
        
        fig.show()

# Global interactive visualizer instance
interactive_visualizer = InteractiveVisualizer()