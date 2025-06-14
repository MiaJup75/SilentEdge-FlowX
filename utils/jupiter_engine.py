# jupiter_engine.py

import requests
import time
import random

BIRDEYE_API_URL = "https://public-api.birdeye.so/defi/token-price"
BIRDEYE_API_KEY = "YOUR_BIRDEYE_API_KEY"  # Replace or use ENV
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

def get_token_price(symbol):
    try:
        response = requests.get(
            f"{BIRDEYE_API_URL}?address={symbol}",
            headers={"X-API-KEY": BIRDEYE_API_KEY}
        )
        data = response.json()
        return float(data.get("data", {}).get("value", 0))
    except Exception as e:
        print(f"[Price Error] {e}")
        return 0

def get_swap_quote(from_token, to_token, amount_usdc, slippage=0.5):
    try:
        amount = int(amount_usdc * 10**6)
        response = requests.get(
            f"https://quote-api.jup.ag/v6/quote?inputMint={from_token}&outputMint={to_token}&amount={amount}&slippageBps={int(slippage * 100)}"
        )
        return response.json()
    except Exception as e:
        print(f"[Quote Error] {e}")
        return {}

def execute_swap(wallet_address, private_key, from_token, to_token, amount_usdc, slippage=0.5):
    try:
        print(f"🔁 Executing swap: {from_token} → {to_token}, Amount: ${amount_usdc}")
        quote = get_swap_quote(from_token, to_token, amount_usdc, slippage)

        if not quote or 'swapTransaction' not in quote:
            return {"success": False, "error": "Invalid quote or missing transaction"}

        # Normally you'd sign & send here using Phantom or Keypair
        # Placeholder for signing
        time.sleep(2)

        return {
            "success": True,
            "side": f"{from_token}->{to_token}",
            "amount": amount_usdc,
            "price_estimate": round(random.uniform(0.98, 1.02), 4)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
