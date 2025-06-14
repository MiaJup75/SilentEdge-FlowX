# config.py

import os
import json

# Load secrets and tokens from Render ENV
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
PHANTOM_SECRET_KEY = os.getenv("PHANTOM_SECRET_KEY")
JUPITER_API_URL = "https://quote-api.jup.ag/v6"

# Load config.json for all strategy settings
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Core strategy parameters
BASE_TOKEN = CONFIG["base_token"]
QUOTE_TOKEN = CONFIG["quote_token"]
TRADE_AMOUNT = CONFIG["trade_amount"]
TAKE_PROFIT_PERCENT = CONFIG["take_profit_percent"]
STOP_LOSS_PERCENT = CONFIG["stop_loss_percent"]
COOLDOWN_MINUTES = CONFIG["cooldown_minutes"]
TRADING_MODE = CONFIG["trading_mode"]
AUTO_TRADE_ENABLED = CONFIG["auto_trade_enabled"]
