import os
import json

# === Environment Variables ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
PHANTOM_SECRET_KEY = os.getenv("PHANTOM_SECRET_KEY")
JUPITER_API_URL = "https://quote-api.jup.ag/v6"
PORT = int(os.environ.get("PORT", "10000"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# === Load config.json Parameters ===
try:
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load config.json: {e}")

# === Trading Strategy Settings ===
BASE_TOKEN = CONFIG.get("base_token", "")
QUOTE_TOKEN = CONFIG.get("quote_token", "")
TRADE_AMOUNT = CONFIG.get("trade_amount", 5)
TAKE_PROFIT_PERCENT = CONFIG.get("take_profit_percent", 1.0)
STOP_LOSS_PERCENT = CONFIG.get("stop_loss_percent", 0.5)
COOLDOWN_MINUTES = CONFIG.get("cooldown_minutes", 5)
TRADING_MODE = CONFIG.get("trading_mode", "SIM")
AUTO_TRADE_ENABLED = CONFIG.get("auto_trade_enabled", False)
SLIPPAGE_TOLERANCE = CONFIG.get("slippage_tolerance", 0.5)

# === Bot Live Mode Flag ===
LIVE_MODE = TRADING_MODE.upper() == "LIVE"
