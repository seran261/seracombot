import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Supported symbols
    SYMBOLS = {
        "USOIL": "CL=F",
        "BTC": "BTC-USD",
        "ETH": "ETH-USD"
    }

    DEFAULT_SYMBOL = "USOIL"
