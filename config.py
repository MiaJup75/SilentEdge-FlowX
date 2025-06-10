import os
import json

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
SOLFLARE_PRIVATE_KEY = os.getenv("SOLFLARE_PRIVATE_KEY")
JUPITER_API_URL = "https://quote-api.jup.ag/v6"

# Load config.json
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Accessible parameters
BASE_TOKEN = CONFIG["base_token"]
QUOTE_TOKEN = CONFIG["quote_token"]
TRADE_AMOUNT = CONFIG["trade_amount"]
TAKE_PROFIT_PERCENT = CONFIG["take_profit_percent"]
STOP_LOSS_PERCENT = CONFIG["stop_loss_percent"]
COOLDOWN_MINUTES = CONFIG["cooldown_minutes"]
TRADING_MODE = CONFIG["trading_mode"]
AUTO_TRADE_ENABLED = CONFIG["auto_trade_enabled"]
