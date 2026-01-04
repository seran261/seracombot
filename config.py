import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Asset configuration
    ASSETS = {
        "USOIL": {
            "symbol": "CL=F",
            "timeframe": "1h",
            "market": "yfinance"
        },
        "BTC": {
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "market": "binance_futures"
        },
        "ETH": {
            "symbol": "ETHUSDT",
            "timeframe": "15m",
            "market": "binance_futures"
        }
    }

    DEFAULT_ASSET = "USOIL"
