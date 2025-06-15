import time
from datetime import datetime
from utils.db import save_trade
from config import TRADE_AMOUNT, SLIPPAGE_TOLERANCE, BASE_TOKEN, QUOTE_TOKEN, LIVE_MODE, TAKE_PROFIT_PERCENT, STOP_LOSS_PERCENT
import requests
import hmac
import hashlib
import os
import json

# === Load Binance API Credentials ===
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# === Endpoint Configuration ===
BASE_URL = "https://api.binance.com"
ORDER_ENDPOINT = "/api/v3/order"
PRICE_ENDPOINT = "/api/v3/ticker/price"


def get_binance_price(symbol: str):
    try:
        response = requests.get(f"{BASE_URL}{PRICE_ENDPOINT}?symbol={symbol}")
        return float(response.json().get("price", 0))
    except Exception as e:
        print("[Price Fetch Error]", e)
        return 0.0


def sign_payload(params):
    query = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(BINANCE_API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={signature}"


def execute_binance_trade(side: str, amount_usdc=TRADE_AMOUNT, live=LIVE_MODE, slippage=SLIPPAGE_TOLERANCE, retries=3):
    trade_result = {}
    symbol = f"{BASE_TOKEN}{QUOTE_TOKEN}"

    for attempt in range(retries):
        try:
            execution_price = get_binance_price(symbol)
            if not execution_price:
                raise Exception("Price fetch failed")

            min_price = execution_price * (1 - slippage / 100)
            max_price = execution_price * (1 + slippage / 100)

            if not live:
                # Simulated entry
                trade_result = {
                    "side": side,
                    "amount": amount_usdc,
                    "status": "✅ Simulated Trade",
                    "price": f"${execution_price:.4f}",
                    "tx_hash": "sim_tx_" + str(int(time.time()))
                }
                break

            else:
                timestamp = int(time.time() * 1000)
                params = {
                    "symbol": symbol,
                    "side": side.upper(),
                    "type": "MARKET",
                    "quoteOrderQty": amount_usdc,
                    "timestamp": timestamp
                }

                headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
                payload = sign_payload(params)
                url = f"{BASE_URL}{ORDER_ENDPOINT}?{payload}"
                response = requests.post(url, headers=headers)
                res = response.json()

                if "orderId" in res:
                    price_executed = float(res["fills"][0]["price"]) if res.get("fills") else execution_price

                    # Calculate TP/SL thresholds
                    tp_price = price_executed * (1 + TAKE_PROFIT_PERCENT / 100)
                    sl_price = price_executed * (1 - STOP_LOSS_PERCENT / 100)

                    trade_result = {
                        "side": side,
                        "amount": amount_usdc,
                        "status": "✅ Live Trade Executed",
                        "price": f"${price_executed:.4f}",
                        "tx_hash": str(res["orderId"]),
                        "tp_price": round(tp_price, 4),
                        "sl_price": round(sl_price, 4)
                    }
                    break
                else:
                    raise Exception(res.get("msg", "Trade failed"))

        except Exception as e:
            print(f"🔥 Attempt {attempt + 1} TRADE ERROR:", str(e))
            if attempt == retries - 1:
                trade_result = {
                    "side": side,
                    "amount": amount_usdc,
                    "status": f"❌ Error: {str(e)}",
                    "price": "N/A",
                    "tx_hash": "N/A"
                }
            else:
                time.sleep(1.5)
                continue

    save_trade({
        "timestamp": datetime.utcnow().isoformat(),
        "side": trade_result.get("side"),
        "amount": trade_result.get("amount"),
        "status": trade_result.get("status"),
        "price": trade_result.get("price"),
        "tx_hash": trade_result.get("tx_hash"),
        "tp_price": trade_result.get("tp_price", None),
        "sl_price": trade_result.get("sl_price", None)
    })

    return trade_result


if __name__ == '__main__':
    print(execute_binance_trade("BUY", 50, live=False))
