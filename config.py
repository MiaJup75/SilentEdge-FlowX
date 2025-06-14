import os
import json

# === Environment Variables ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))
PHANTOM_SECRET_KEY = os.getenv("PHANTOM_SECRET_KEY")
JUPITER_API_URL = "https://quote-api.jup.ag/v6"
PORT = int(os.environ.get("PORT", "10000"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# === Load config.json Parameters ===
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# === Trading Strategy Settings ===
BASE_TOKEN = CONFIG["base_token"]
QUOTE_TOKEN = CONFIG["quote_token"]
TRADE_AMOUNT = CONFIG["trade_amount"]
TAKE_PROFIT_PERCENT = CONFIG["take_profit_percent"]
STOP_LOSS_PERCENT = CONFIG["stop_loss_percent"]
COOLDOWN_MINUTES = CONFIG["cooldown_minutes"]
TRADING_MODE = CONFIG["trading_mode"]
AUTO_TRADE_ENABLED = CONFIG["auto_trade_enabled"]
SLIPPAGE_TOLERANCE = CONFIG.get("slippage_tolerance", 0.5)

# === Bot Live Mode Flag ===
LIVE_MODE = TRADING_MODE.upper() == "LIVE"
