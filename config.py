import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    ASSETS = {
        "USOIL": {
            "symbol": "CL=F",
            "timeframe": "1h",
            "market": "yfinance"
        },
        "BTC": {
            "symbol": "BTCUSDT",
            "timeframe": "15",
            "market": "bybit"
        },
        "ETH": {
            "symbol": "ETHUSDT",
            "timeframe": "15",
            "market": "bybit"
        }
    }

    DEFAULT_ASSET = "USOIL"
