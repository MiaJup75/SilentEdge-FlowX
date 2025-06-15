import json
import os
from datetime import datetime

LOG_FILE = "trade_log.json"

def save_trade(trade: dict):
    """
    Append a new trade entry to the JSON log file.
    Ensures timestamp and auto-increment structure.
    """
    try:
        if "timestamp" not in trade:
            trade["timestamp"] = datetime.utcnow().isoformat()

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
    """
    Return a list of all trade entries from the JSON log.
    """
    try:
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading trades: {e}")
        return []

def get_open_trades(symbol=None):
    """
    Return all open BUY trades from the log file (not closed by TP/SL).
    """
    trades = load_trades()
    open_trades = []

    for trade in trades:
        # Consider as open if status includes 'Live' and side is BUY
        if trade.get("side") == "BUY" and "Live" in trade.get("status", ""):
            if symbol is None or symbol in trade.get("price", "") or symbol in trade.get("symbol", ""):
                open_trades.append(trade)

    return open_trades
