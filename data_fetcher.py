import yfinance as yf
import pandas as pd
import requests
import time

class DataFetcher:
    def __init__(self, asset_config):
        self.asset = asset_config

    def get_ohlcv(self, limit=200):
        market = self.asset["market"]

        if market == "yfinance":
            return self._fetch_yfinance(limit)
        elif market == "bybit":
            return self._fetch_bybit(limit)
        else:
            return None

    # -------------------------
    # USOIL — Yahoo Finance
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
    # BTC / ETH — BYBIT FUTURES (FINAL FIX)
    # -------------------------
    def _fetch_bybit(self, limit):
        url = "https://api.bybit.com/v5/market/kline"

        params = {
            "category": "linear",              # USDT perpetuals
            "symbol": self.asset["symbol"],    # BTCUSDT / ETHUSDT
            "interval": str(self.asset["timeframe"]),
            "limit": limit
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        for attempt in range(3):
            try:
                r = requests.get(url, params=params, headers=headers, timeout=10)
                data = r.json()

                # ❌ API-level error
                if data.get("retCode") != 0:
                    time.sleep(1)
                    continue

                result = data.get("result", {})
                candles = result.get("list", [])

                # ❌ No candles returned
                if not candles or len(candles) < 10:
                    time.sleep(1)
                    continue

                # Bybit returns newest → oldest, reverse it
                candles = candles[::-1]

                df = pd.DataFrame(
                    candles,
                    columns=[
                        "open_time",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "turnover",
                    ],
                )

                # Convert to float safely
                df = df[["open", "high", "low", "close", "volume"]]
                df = df.astype(float)

                # Final sanity check
                if df.isnull().any().any():
                    continue

                return df

            except Exception:
                time.sleep(1)

        # 🔥 only here if truly failed
        return None
