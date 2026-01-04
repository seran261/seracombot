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
        elif self.asset["market"] == "bybit":
            return self._fetch_bybit(limit)
        else:
            return None

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
    # BTC / ETH (Bybit Futures)
    # -------------------------
    def _fetch_bybit(self, limit):
        url = "https://api.bybit.com/v5/market/kline"
        params = {
            "category": "linear",
            "symbol": self.asset["symbol"],
            "interval": self.asset["timeframe"],
            "limit": limit
        }

        for _ in range(2):  # retry once
            try:
                r = requests.get(url, params=params, timeout=10)
                data = r.json()

                if data.get("retCode") != 0:
                    time.sleep(1)
                    continue

                candles = data["result"]["list"]
                if not candles:
                    return None

                # Bybit returns newest first → reverse
                candles = candles[::-1]

                df = pd.DataFrame(candles, columns=[
                    "open_time", "open", "high", "low", "close", "volume", "turnover"
                ])

                df = df[["open", "high", "low", "close", "volume"]].astype(float)
                return df

            except Exception:
                time.sleep(1)

        return None
