import yfinance as yf
import pandas as pd
import requests
import time

class DataFetcher:
    def __init__(self, asset_config):
        self.asset = asset_config

    def get_ohlcv(self, limit=300):
        if self.asset["market"] == "yfinance":
            return self._fetch_yfinance(limit)
        else:
            return self._fetch_binance_futures(limit)

    # -------------------------
    # USOIL (Yahoo Finance)
    # -------------------------
    def _fetch_yfinance(self, limit):
        df = yf.download(
            self.asset["symbol"],
            interval=self.asset["timeframe"],
            period="60d",
            auto_adjust=False,
            progress=False
        )

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]

        return df[['open', 'high', 'low', 'close', 'volume']].tail(limit)

    # -------------------------
    # BTC / ETH (Binance Futures)
    # -------------------------
    def _fetch_binance_futures(self, limit):
        url = "https://fapi.binance.com/fapi/v1/klines"
        params = {
            "symbol": self.asset["symbol"],
            "interval": self.asset["timeframe"],
            "limit": limit
        }

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if not isinstance(data, list):
            return None

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qav", "num_trades",
            "taker_base", "taker_quote", "ignore"
        ])

        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df
