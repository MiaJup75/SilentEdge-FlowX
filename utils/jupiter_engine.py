import requests
import random
import time

# Jupiter API Endpoints
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

# Token Mints (can be moved to config.py later)
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def get_swap_quote(from_token, to_token, amount_usdc, slippage=0.5):
    try:
        amount_lamports = int(amount_usdc * 10**6)  # USDC has 6 decimals
        params = {
            "inputMint": from_token,
            "outputMint": to_token,
            "amount": amount_lamports,
            "slippageBps": int(slippage * 100),  # 0.5% = 50 BPS
            "onlyDirectRoutes": False
        }
        res = requests.get(JUPITER_QUOTE_URL, params=params, timeout=5)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[❌ Jupiter Quote Error] {e}")
        return {}

def execute_swap(wallet_address, private_key, from_token, to_token, amount_usdc, slippage=0.5):
    try:
        print(f"🔁 Executing Jupiter swap: {from_token} → {to_token} | ${amount_usdc} | Slippage: {slippage}%")
        quote = get_swap_quote(from_token, to_token, amount_usdc, slippage)

        if not quote or "routes" not in quote or not quote["routes"]:
            return {"success": False, "error": "No valid routes from Jupiter"}

        # === Simulated Trade Execution ===
        time.sleep(1)  # Simulate transaction delay

        return {
            "success": True,
            "side": f"{from_token}->{to_token}",
            "amount": amount_usdc,
            "price_estimate": round(random.uniform(0.97, 1.02), 4),
            "used_route": quote["routes"][0]["marketInfos"][0]["label"],
            "tx_hash": f"sim_tx_{int(time.time())}"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}
