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
            group_by="column",   # 🔥 important for crypto
            auto_adjust=False,
            progress=False
        )

        if df is None or df.empty:
            return None

        # 🔥 FIX: handle MultiIndex columns safely
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]

        required = ["open", "high", "low", "close", "volume"]
        df = df[required]

        return df.tail(limit)
