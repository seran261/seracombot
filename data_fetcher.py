import yfinance as yf

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

        if df is None or df.empty:
            return None

        df.columns = [c.lower() for c in df.columns]
        df = df[['open', 'high', 'low', 'close', 'volume']]
        return df.tail(limit)
