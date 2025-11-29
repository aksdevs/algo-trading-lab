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
        try:
            ticker = yf.Ticker(symbol)
            
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            df.reset_index(inplace=True)
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching data for {symbol}: {str(e)}")

    @staticmethod
    def save_to_csv(df: pd.DataFrame, symbol: str) -> str:
        filepath = f"data/{symbol}.csv"
        df.to_csv(filepath, index=False)
        return filepath
