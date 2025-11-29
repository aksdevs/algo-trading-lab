import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta

class DataLoader:
    @staticmethod
    def fetch_data(
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical market data using yfinance.
        
        Args:
            symbol (str): The stock symbol to fetch data for (e.g., 'AAPL', 'SPY')
            start_date (str, optional): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format
            period (str, optional): Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            interval (str, optional): Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            
        Returns:
            pd.DataFrame: DataFrame containing the historical market data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Reset index to make Date a column
            df.reset_index(inplace=True)
            
            # Ensure all required columns are present
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    @staticmethod
    def save_to_csv(df: pd.DataFrame, symbol: str) -> str:
        """
        Save the DataFrame to a CSV file in the data directory.
        
        Args:
            df (pd.DataFrame): DataFrame containing the market data
            symbol (str): The stock symbol
            
        Returns:
            str: Path to the saved CSV file
        """
        filepath = f"data/{symbol}.csv"
        df.to_csv(filepath, index=False)
        return filepath