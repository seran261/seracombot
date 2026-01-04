import yfinance as yf
import pandas as pd

class DataFetcher:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_ohlcv(self, timeframe="1h", limit=300):
        df = yf.download(
            self.symbol,
            interval=timeframe,
            period="60d",
            progress=False
        )

        if df.empty:
            return None

        df = df.rename(columns=str.lower)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        return df.tail(limit)
