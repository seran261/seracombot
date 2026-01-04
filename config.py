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
            "symbol": "BTC-USDT-SWAP",
            "timeframe": "15m",
            "market": "okx"
        },
        "ETH": {
            "symbol": "ETH-USDT-SWAP",
            "timeframe": "15m",
            "market": "okx"
        }
    }

    DEFAULT_ASSET = "USOIL"
