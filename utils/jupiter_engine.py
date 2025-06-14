# utils/jupiter_engine.py

import requests
import random
import time

JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

# Token Mints
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def get_swap_quote(from_token, to_token, amount_usdc, slippage=0.5):
    try:
        amount = int(amount_usdc * 10**6)  # Convert to lamports
        params = {
            "inputMint": from_token,
            "outputMint": to_token,
            "amount": amount,
            "slippageBps": int(slippage * 100),
            "onlyDirectRoutes": False
        }
        res = requests.get(JUPITER_QUOTE_URL, params=params)
        return res.json()
    except Exception as e:
        print(f"[Quote Error] {e}")
        return {}

def execute_swap(wallet_address, private_key, from_token, to_token, amount_usdc, slippage=0.5):
    try:
        print(f"🔁 Executing Jupiter swap: {from_token} → {to_token} | ${amount_usdc}")
        quote = get_swap_quote(from_token, to_token, amount_usdc, slippage)

        # Check if valid quote returned
        if not quote or "routes" not in quote or not quote["routes"]:
            return {"success": False, "error": "No valid routes from Jupiter"}

        # Normally you'd build, sign, and send the swap transaction here
        # This version simulates success for now
        time.sleep(1)

        return {
            "success": True,
            "side": f"{from_token}->{to_token}",
            "amount": amount_usdc,
            "price_estimate": round(random.uniform(0.97, 1.02), 4),
            "used_route": quote["routes"][0]["marketInfos"][0]["label"]
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
