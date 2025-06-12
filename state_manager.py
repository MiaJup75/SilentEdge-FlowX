import os
import json
from datetime import datetime

STATE_FILE = "bot_state.json"

# === Default State ===
default_state = {
    "paused": False,
    "daily_limit": 10,
    "trades_today": 0,
    "last_reset": datetime.utcnow().strftime("%Y-%m-%d")
}

# === Load or Create State ===
def load_state():
    if not os.path.exists(STATE_FILE):
        save_state(default_state)
        return default_state

    with open(STATE_FILE, "r") as f:
        state = json.load(f)

    # Reset daily trades if date changed
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if state.get("last_reset") != today:
        state["trades_today"] = 0
        state["last_reset"] = today
        save_state(state)

    return state

# === Save State ===
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# === Pause Logic ===
def is_paused():
    return load_state().get("paused", False)

def toggle_pause():
    state = load_state()
    state["paused"] = not state["paused"]
    save_state(state)
    return state["paused"]

def set_pause(value: bool):
    state = load_state()
    state["paused"] = value
    save_state(state)

# === Limit Logic ===
def trade_limit_reached():
    state = load_state()
    return state["trades_today"] >= state.get("daily_limit", 10)

def record_trade():
    state = load_state()
    state["trades_today"] += 1
    save_state(state)

def set_daily_limit(limit):
    state = load_state()
    state["daily_limit"] = limit
    save_state(state)

def set_limit(value: int):
    state = load_state()
    state["daily_limit"] = value
    save_state(state)

# === Trade Count Access ===
def check_and_increment_trade_count():
    state = load_state()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if state.get("last_reset") != today:
        state["last_reset"] = today
        state["trades_today"] = 1
    else:
        state["trades_today"] += 1
    save_state(state)
    return state["trades_today"]

def get_trade_count():
    state = load_state()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if state.get("last_reset") != today:
        return 0
    return state.get("trades_today", 0)

def reset_trade_count():
    state = load_state()
    state["trades_today"] = 0
    state["last_reset"] = datetime.utcnow().strftime("%Y-%m-%d")
    save_state(state)

# === Status Output ===
def get_status_report():
    state = load_state()
    return (
        f"📊 <b>Bot Status</b>\n"
        f"⛔ Paused: {'Yes' if state['paused'] else 'No'}\n"
        f"📈 Daily Limit: {state['daily_limit']}\n"
        f"🔄 Trades Today: {state['trades_today']}"
    )
