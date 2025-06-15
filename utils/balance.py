# === utils/balance.py (Binance Version) ===

import requests
import hmac
import hashlib
import time
import os

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

BASE_URL = "https://api.binance.com"
HEADERS = {
    "X-MBX-APIKEY": BINANCE_API_KEY
}

# === Authenticated Request Helper ===
def signed_request(endpoint="/api/v3/account", params=None):
    if params is None:
        params = {}

    params["timestamp"] = int(time.time() * 1000)
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(
        BINANCE_API_SECRET.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    query_string += f"&signature={signature}"

    url = f"{BASE_URL}{endpoint}?{query_string}"
    response = requests.get(url, headers=HEADERS, timeout=10)

    if response.status_code != 200:
        raise Exception(f"❌ Binance API Error: {response.text}")

    return response.json()

# === Fetch Wallet Balances (Filtered by Known Tokens) ===
TRACKED_TOKENS = {
    "BTC": "₿",
    "ETH": "🧪",
    "USDC": "💵",
    "XRP": "💧",
    "SOL": "🪙"
}

def get_binance_balances():
    data = signed_request("/api/v3/account")
    balances = {entry["asset"]: float(entry["free"]) for entry in data["balances"]}

    summary = []
    total_value = 0.0

    # Use Binance price ticker
    prices = requests.get(BASE_URL + "/api/v3/ticker/price", timeout=5).json()
    price_dict = {p["symbol"]: float(p["price"]) for p in prices}

    for asset, emoji in TRACKED_TOKENS.items():
        amount = balances.get(asset, 0)
        symbol_pair = f"{asset}USDC"
        reverse_pair = f"USDC{asset}"
        usd_price = price_dict.get(symbol_pair) or (1 / price_dict.get(reverse_pair, 1))

        usd_value = round(amount * usd_price, 2)
        if amount > 0:
            total_value += usd_value
            summary.append(f"{emoji} <b>{asset}</b>: {amount:.4f} ≈ ${usd_value:,.2f}")

    header = f"💰 <b>Total Wallet Value:</b> ${total_value:,.2f}\n"
    return balances, header + "\n".join(summary)
