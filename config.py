import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    USOIL_SYMBOL = os.getenv("USOIL_SYMBOL", "CL=F")

    MIN_SIGNAL_STRENGTH = 55
    RR_MIN = 1.5
