import yfinance as yf
import pandas as pd
import requests
import time

class DataFetcher:
    def __init__(self, asset_config):
        self.asset = asset_config

    def get_ohlcv(self, limit=200):
        if self.asset["market"] == "yfinance":
            return self._fetch_yfinance(limit)
        elif self.asset["market"] == "okx":
            return self._fetch_okx(limit)
        return None

    # -------------------------
    # USOIL (Yahoo Finance)
    # -------------------------
    def _fetch_yfinance(self, limit):
        df = yf.download(
            self.asset["symbol"],
            interval=self.asset["timeframe"],
            period="60d",
            progress=False,
            auto_adjust=False
        )

        if df is None or df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]

        return df[["open", "high", "low", "close", "volume"]].tail(limit)

    # -------------------------
    # BTC / ETH — OKX FUTURES
    # -------------------------
    def _fetch_okx(self, limit):
        url = "https://www.okx.com/api/v5/market/candles"

        params = {
            "instId": self.asset["symbol"],   # BTC-USDT-SWAP
            "bar": self.asset["timeframe"],  # 15m
            "limit": limit
        }

        for _ in range(3):  # retry
            try:
                r = requests.get(url, params=params, timeout=10)
                data = r.json()

                if data.get("code") != "0":
                    time.sleep(1)
                    continue

                candles = data.get("data", [])
                if not candles or len(candles) < 10:
                    time.sleep(1)
                    continue

                # OKX returns newest → oldest
                candles = candles[::-1]

                df = pd.DataFrame(
                    candles,
                    columns=[
                        "ts", "open", "high", "low",
                        "close", "volume", "volume_ccy", "volume_ccy_quote", "confirm"
                    ]
                )

                df = df[["open", "high", "low", "close", "volume"]].astype(float)

                if df.isnull().any().any():
                    continue

                return df

            except Exception:
                time.sleep(1)

        return None
