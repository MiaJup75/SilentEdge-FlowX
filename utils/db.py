import json
import os
from datetime import datetime

LOG_FILE = "trade_log.json"

def save_trade(trade: dict):
    """Append a new trade entry to the log file."""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append(trade)

        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving trade log: {e}")

def load_trades():
    """Load all trade entries."""
    try:
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading trades: {e}")
        return []
