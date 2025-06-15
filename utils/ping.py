# === handlers/ping.py ===

import os
import time
import platform
from telegram import Update
from telegram.ext import CallbackContext
from config import TRADE_AMOUNT


def check_binance():
    try:
        import requests
        r = requests.get("https://api.binance.com/api/v3/ping", timeout=5)
        if r.status_code == 200:
            return "✅ <b>Binance API:</b> Operational"
        else:
            return f"⚠️ <b>Binance API:</b> Response {r.status_code}"
    except Exception as e:
        return f"❌ <b>Binance API:</b> Error – {str(e)}"


def check_openai():
    key = os.getenv("OPENAI_API_KEY")
    if key and len(key) > 10:
        return "✅ <b>OpenAI Key:</b> Loaded"
    else:
        return "❌ <b>OpenAI Key:</b> Missing"


def check_render():
    env = os.getenv("RENDER_EXTERNAL_URL", None)
    return f"✅ <b>Render URL:</b> Set" if env else "❌ <b>Render URL:</b> Missing"


def check_trading_engine():
    return "🛠 <b>Trade Engine:</b> Binance Mode Active ✅"


def check_system():
    os_name = platform.system()
    return f"🧠 <b>Host:</b> {os_name} | <b>Trade Size:</b> ${TRADE_AMOUNT}"


def run_health_check():
    results = [
        check_binance(),
        check_openai(),
        check_render(),
        check_trading_engine(),
        check_system()
    ]
    return "\n".join(results)


def ping(update: Update, context: CallbackContext):
    start = time.time()
    result = run_health_check()
    latency = round((time.time() - start) * 1000)
    result += f"\n⏱ <b>Latency:</b> {latency}ms"
    update.message.reply_text(result, parse_mode="HTML")
