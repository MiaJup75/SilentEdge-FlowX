# config.py

import os
import json

# === Environment Variables (Render) ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
PHANTOM_SECRET_KEY = os.getenv("PHANTOM_SECRET_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
LIVE_MODE = os.getenv("LIVE_MODE", "false").lower() == "true"
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
JUPITER_API_URL = "https://quote-api.jup.ag/v6"

# === Load Strategy Config ===
with open("config.json", "r") as f:
    CONFIG = json.load(f)

BASE_TOKEN = CONFIG["base_token"]
QUOTE_TOKEN = CONFIG["quote_token"]
TRADE_AMOUNT = float(CONFIG["trade_amount"])  # Ensure it's always a float
TAKE_PROFIT_PERCENT = CONFIG["take_profit_percent"]
STOP_LOSS_PERCENT = CONFIG["stop_loss_percent"]
COOLDOWN_MINUTES = CONFIG["cooldown_minutes"]
TRADING_MODE = CONFIG["trading_mode"]
AUTO_TRADE_ENABLED = CONFIG["auto_trade_enabled"]
